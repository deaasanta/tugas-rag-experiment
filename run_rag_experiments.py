"""Menjalankan 4 eksperimen RAG (12 konfigurasi) pada aplikasi rag-app yang ASLI, lewat HTTP.

Yang dilakukan script untuk setiap konfigurasi:
  1. mengubah SATU nilai di config.py atau llm.py (nilai lain = baseline),
  2. untuk eksperimen chunking: menghapus qdrant_data/ saat server mati,
  3. menyalakan server (python -m uvicorn main:app),
  4. untuk eksperimen chunking: upload + ingest PDF yang sama, mencatat chunks_stored,
  5. mengirim pertanyaan yang sama ke POST /ask dan menyimpan jawaban + sources + score,
  6. mematikan server.
Di akhir, config.py dan llm.py dikembalikan ke isi semula.

Pakai (dari folder rag-app, venv aktif, .env sudah berisi GROQ_API_KEY):
  python run_rag_experiments.py --pdf materi_pdina.pdf
  python run_rag_experiments.py --pdf materi_pdina.pdf --only E3      # ulang satu eksperimen saja

Hasil: experiment_results/results.md (untuk disalin ke README) dan results.json (data mentah).
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import urllib.error
import urllib.request
import uuid

ROOT = Path(__file__).resolve().parent
CONFIG = ROOT / "config.py"
LLM = ROOT / "llm.py"
QDRANT_DIR = ROOT / "qdrant_data"
OUT_DIR = ROOT / "experiment_results"
PORT = 8000
BASE = f"http://127.0.0.1:{PORT}"

# Pertanyaan yang SAMA untuk semua eksperimen. Ganti jika memakai PDF lain.
DEFAULT_QUESTIONS = [
    "Berapa nilai threshold τ dan n_min yang dipilih, dan bagaimana cara memilihnya?",
    "Kenapa P-DINA tidak memakai algoritma EM DINA klasik?",
]

BASELINE = {"temperature": 0.2, "TOP_K": 4, "CHUNK_SIZE": 100, "CHUNK_OVERLAP": 20}

# (kode, judul, parameter, nilai, perlu ingest ulang?)
EXPERIMENTS = [
    ("E1", "Experiment 1 - Temperature", "temperature", [0.0, 0.2, 0.8], False),
    ("E2", "Experiment 2 - TOP_K", "TOP_K", [1, 4, 8], False),
    ("E3", "Experiment 3 - Chunk Size", "CHUNK_SIZE", [50, 100, 120], True),
    ("E4", "Experiment 4 - Chunk Overlap", "CHUNK_OVERLAP", [0, 20, 40], True),
]


# ---------------------------------------------------------------------------- edit parameter
# newline="" menjaga line ending asli (CRLF di Windows) agar file tidak berubah selain nilai parameternya
def read_src(path: Path) -> str:
    with open(path, encoding="utf-8", newline="") as f:
        return f.read()


def write_src(path: Path, text: str):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def set_config_value(name: str, value):
    text = read_src(CONFIG)
    new, n = re.subn(rf"(?m)^{name}[ \t]*=[ \t]*[^\r\n#]+", f"{name} = {value}", text)
    if n != 1:
        raise RuntimeError(f"{name} tidak ditemukan tepat satu kali di config.py")
    write_src(CONFIG, new)


def set_temperature(value: float):
    text = read_src(LLM)
    new, n = re.subn(r"temperature\s*=\s*[0-9.]+", f"temperature={value}", text)
    if n != 1:
        raise RuntimeError("temperature=... tidak ditemukan tepat satu kali di llm.py")
    write_src(LLM, new)


def apply(params: dict):
    set_temperature(params["temperature"])
    for k in ("TOP_K", "CHUNK_SIZE", "CHUNK_OVERLAP"):
        set_config_value(k, params[k])


def read_current() -> dict:
    cfg = read_src(CONFIG)
    llm = read_src(LLM)
    cur = {"temperature": float(re.search(r"temperature\s*=\s*([0-9.]+)", llm).group(1))}
    for k in ("TOP_K", "CHUNK_SIZE", "CHUNK_OVERLAP"):
        cur[k] = int(re.search(rf"(?m)^{k}\s*=\s*(\d+)", cfg).group(1))
    return cur


# ---------------------------------------------------------------------------- HTTP (library bawaan Python saja)
def http(method: str, path: str, body: bytes | None = None, headers: dict | None = None, timeout: float = 180):
    req = urllib.request.Request(BASE + path, data=body, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode("utf-8") or "null")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")


def server_up() -> bool:
    try:
        return http("GET", "/health", timeout=2)[0] == 200
    except (urllib.error.URLError, OSError):
        return False


# ---------------------------------------------------------------------------- server
def start_server() -> subprocess.Popen:
    if server_up():
        raise RuntimeError(f"Sudah ada server di port {PORT}. Matikan server rag-app yang sedang berjalan dulu.")
    log = open(OUT_DIR / "server.log", "a", encoding="utf-8")
    proc = subprocess.Popen([sys.executable, "-m", "uvicorn", "main:app", "--port", str(PORT)], cwd=ROOT,
                            stdout=log, stderr=subprocess.STDOUT)
    proc._log = log
    deadline = time.time() + 300           # run pertama mengunduh model embedding
    while time.time() < deadline:
        if proc.poll() is not None:
            log.close()
            tail = (OUT_DIR / "server.log").read_text(encoding="utf-8", errors="replace")[-2000:]
            raise RuntimeError("Server berhenti saat start. Akhir server.log:\n" + tail)
        if server_up():
            return proc
        time.sleep(1)
    proc.kill()
    raise RuntimeError("Server tidak siap dalam 300 detik (lihat experiment_results/server.log)")


def stop_server(proc: subprocess.Popen):
    proc.terminate()
    try:
        proc.wait(timeout=20)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
    proc._log.close()
    time.sleep(1)                           # beri waktu lock qdrant_data dilepas (penting di Windows)


def reset_qdrant():
    for _ in range(10):
        if not QDRANT_DIR.exists():
            return
        try:
            shutil.rmtree(QDRANT_DIR)
        except OSError:
            time.sleep(1)
    if QDRANT_DIR.exists():
        raise RuntimeError("qdrant_data/ gagal dihapus. Pastikan tidak ada server lain yang berjalan.")


# ---------------------------------------------------------------------------- API calls
def ingest(pdf: Path) -> dict:
    boundary = uuid.uuid4().hex
    body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{pdf.name}\"\r\n"
            f"Content-Type: application/pdf\r\n\r\n").encode() + pdf.read_bytes() + f"\r\n--{boundary}--\r\n".encode()
    status, data = http("POST", "/ingest", body, {"Content-Type": f"multipart/form-data; boundary={boundary}"}, timeout=600)
    if status != 200:
        raise RuntimeError(f"Ingest gagal (HTTP {status}): {data}")
    return data


def ask(question: str) -> dict:
    body = json.dumps({"question": question}).encode("utf-8")
    for attempt in range(5):
        status, data = http("POST", "/ask", body, {"Content-Type": "application/json"})
        if status == 200:
            return data
        wait = 10 * (attempt + 1)
        print(f"    HTTP {status} dari /ask, coba lagi dalam {wait} detik ... ({str(data)[:150]})")
        time.sleep(wait)
    raise RuntimeError(f"/ask terus gagal (HTTP {status}): {data}. Cek GROQ_API_KEY / kuota Groq.")


# ---------------------------------------------------------------------------- run
def run_config(params: dict, pdf: Path, questions: list[str], reingest: bool, repeats: int) -> dict:
    apply(params)
    if reingest:
        reset_qdrant()
    proc = start_server()
    try:
        info = {"params": dict(params), "ingest": None, "answers": []}
        if reingest:
            info["ingest"] = ingest(pdf)
            print(f"    chunks_stored = {info['ingest']['chunks_stored']}")
        for q in questions:
            runs = []
            for _ in range(repeats):
                runs.append(ask(q))
                time.sleep(2)               # menghindari rate limit Groq
            info["answers"].append({"question": q, "runs": runs})
        return info
    finally:
        stop_server(proc)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True, type=Path)
    ap.add_argument("--questions", type=Path, help="file .txt, satu pertanyaan per baris (default: 2 pertanyaan bawaan)")
    ap.add_argument("--only", choices=[e[0] for e in EXPERIMENTS], nargs="*")
    ap.add_argument("--temperature-repeats", type=int, default=2,
                    help="jumlah run per pertanyaan di Experiment 1, untuk melihat konsistensi (default 2)")
    args = ap.parse_args()

    pdf = args.pdf.resolve()
    if not pdf.exists():
        sys.exit(f"PDF tidak ditemukan: {pdf}")
    questions = ([l.strip() for l in args.questions.read_text(encoding="utf-8").splitlines() if l.strip()]
                 if args.questions else DEFAULT_QUESTIONS)
    selected = [e for e in EXPERIMENTS if not args.only or e[0] in args.only]

    OUT_DIR.mkdir(exist_ok=True)
    original = {CONFIG: CONFIG.read_bytes(), LLM: LLM.read_bytes()}
    found = read_current()
    if found != BASELINE:
        print(f"PERINGATAN: nilai di file saat ini {found} berbeda dari baseline tugas {BASELINE}. "
              "Script tetap memakai baseline tugas.")

    json_path = OUT_DIR / "results.json"
    results = json.loads(json_path.read_text(encoding="utf-8")) if json_path.exists() else {}
    try:
        need_baseline_index = any(not e[4] for e in selected)
        if need_baseline_index:
            print("Menyiapkan index baseline (CHUNK_SIZE=100, CHUNK_OVERLAP=20) untuk Experiment 1 & 2 ...")
            apply(BASELINE)
            reset_qdrant()
            proc = start_server()
            try:
                results["baseline_ingest"] = ingest(pdf)
            finally:
                stop_server(proc)
            print(f"    chunks_stored baseline = {results['baseline_ingest']['chunks_stored']}")

        for code, title, param, values, reingest in selected:
            results[code] = {"title": title, "param": param, "runs": []}
            for v in values:
                params = dict(BASELINE, **{param: v})
                print(f"{code}: {param} = {v}")
                repeats = args.temperature_repeats if code == "E1" else 1
                results[code]["runs"].append(run_config(params, pdf, questions, reingest, repeats))
                json_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        results["meta"] = {"pdf": pdf.name, "questions": questions, "finished": datetime.now().isoformat(timespec="seconds")}
        json_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    finally:
        for path, raw in original.items():
            path.write_bytes(raw)
        print("config.py dan llm.py dikembalikan ke isi semula.")

    write_markdown(results)
    print(f"Selesai. Lihat {OUT_DIR / 'results.md'}")


# ---------------------------------------------------------------------------- laporan
def fmt_sources(sources: list[dict]) -> str:
    return "\n".join(f"- {s['source']} | halaman {s['page']} | score {s['score']:.4f}" for s in sources) or "- (tidak ada)"


def write_markdown(results: dict):
    meta = results.get("meta", {})
    lines = [f"# Hasil Aktual Eksperimen RAG\n",
             f"PDF: `{meta.get('pdf', '-')}` · selesai: {meta.get('finished', '-')}\n"]
    if "baseline_ingest" in results:
        b = results["baseline_ingest"]
        lines.append(f"Ingest baseline (CHUNK_SIZE=100, CHUNK_OVERLAP=20): pages_read = {b['pages_read']}, "
                     f"chunks_stored = {b['chunks_stored']}\n")
    for code, _, param, _, _ in EXPERIMENTS:
        if code not in results:
            continue
        exp = results[code]
        lines.append(f"\n## {exp['title']}\n")
        for run in exp["runs"]:
            p = run["params"]
            lines.append(f"\n### {param} = {p[param]}\n")
            lines.append(f"Konfigurasi: temperature={p['temperature']}, TOP_K={p['TOP_K']}, "
                         f"CHUNK_SIZE={p['CHUNK_SIZE']}, CHUNK_OVERLAP={p['CHUNK_OVERLAP']}\n")
            if run["ingest"]:
                lines.append(f"**Chunks Stored:** {run['ingest']['chunks_stored']} "
                             f"(pages_read = {run['ingest']['pages_read']})\n")
            lines.append(f"Jumlah chunk yang dikirim ke LLM sebagai context: {p['TOP_K']} "
                         "(daftar sources di bawah sudah dideduplikasi per halaman oleh aplikasi)\n")
            for a in run["answers"]:
                lines.append(f"\n**Pertanyaan:** {a['question']}\n")
                for i, r in enumerate(a["runs"], 1):
                    label = f"Actual Output (run {i})" if len(a["runs"]) > 1 else "Actual Output"
                    lines.append(f"\n**{label}:**\n\n{r['answer'].strip()}\n")
                lines.append(f"\n**Sources / Similarity Score:**\n\n{fmt_sources(a['runs'][0]['sources'])}\n")
    (OUT_DIR / "results.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
