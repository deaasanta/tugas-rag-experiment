# Langkah Mengerjakan Tugas RAG Parameter Exploration

File di kit ini: `run_rag_experiments.py`, `materi_pdina.pdf`, `README.md` (template hasil), `.gitignore`.
File ini (`LANGKAH.md`) tidak perlu di-push.

## 1. Setup (±15 menit)

```bash
git clone https://github.com/arifian853/rag-app.git
cd rag-app
python -m venv venv
venv\Scripts\activate                # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
copy .env.example .env               # macOS/Linux: cp .env.example .env
```

Isi `.env`:

```
GROQ_API_KEY=gsk_...                 # dari https://console.groq.com/
GROQ_MODEL=openai/gpt-oss-120b
```

Salin keempat file kit (`run_rag_experiments.py`, `materi_pdina.pdf`, `README.md`, `.gitignore`) ke folder `rag-app`,
timpa `README.md` dan `.gitignore` yang lama.

## 2. Cek manual sekali (±5 menit)

```bash
python -m uvicorn main:app --reload
```

Buka http://127.0.0.1:8000, upload `materi_pdina.pdf`, tanyakan Pertanyaan 1. Pastikan jawaban muncul.
**Matikan server (Ctrl+C) sebelum langkah 3**, karena script menyalakan servernya sendiri di port 8000.

## 3. Jalankan seluruh eksperimen (±10–20 menit)

```bash
python run_rag_experiments.py --pdf materi_pdina.pdf
```

Script menjalankan 12 konfigurasi (Temperature 0.0/0.2/0.8, TOP_K 1/4/8, Chunk Size 50/100/120, Chunk Overlap 0/20/40)
sesuai aturan tugas: satu parameter berubah, `qdrant_data/` dihapus dan PDF di-ingest ulang untuk eksperimen chunking.
Pada Experiment Temperature, setiap pertanyaan dijalankan 2 kali agar konsistensi jawaban bisa dinilai.

Jika satu eksperimen gagal (misalnya kuota Groq habis), ulangi hanya bagian itu:

```bash
python run_rag_experiments.py --pdf materi_pdina.pdf --only E3
```

Memakai PDF dan pertanyaan sendiri: buat `pertanyaan.txt` (satu pertanyaan per baris), lalu
`python run_rag_experiments.py --pdf nama.pdf --questions pertanyaan.txt`.

## 4. Isi README

Salin output, chunks_stored, dan sources/score dari `experiment_results/results.md` ke `README.md`, lalu tulis
Observation, kesimpulan, Final Configuration, Final Questions, dan Personal Reflection dengan pendapatmu sendiri.
Cek tidak ada `[ISI SENDIRI]` yang tersisa.

Hal yang layak diamati:
- `sources` dideduplikasi per halaman. TOP_K = 8 bisa hanya menampilkan 2–3 source, padahal 8 chunk dikirim ke LLM.
- CHUNK_SIZE dan CHUNK_OVERLAP dihitung dalam **token** (tokenizer model embedding), bukan karakter.
- Di `chunker.py`, separator ditulis `"\\n\\n"` dan `"\\n"` (backslash + huruf n), bukan baris baru. Akibatnya teks tidak
  dipotong di pergantian baris/paragraf, melainkan di `". "` atau spasi. Ini bisa menjelaskan chunk yang terpotong di
  tengah kalimat. Jangan diperbaiki, karena eksperimen harus memakai aplikasi yang sama.

## 5. Push ke GitHub (repo baru: `tugas-rag-experiment`)

Repo asli sudah berisi folder `__pycache__/` yang ter-commit, dan instruksi meminta folder itu tidak di-push.
Hapus dari tracking git dulu (file di laptop tidak terhapus):

```bash
git rm -r --cached __pycache__
git remote set-url origin https://github.com/USERNAME/tugas-rag-experiment.git
git remote -v
git add .
git status                           # pastikan .env, venv/, qdrant_data/, data/uploads/ TIDAK muncul
git commit -m "Submit RAG Parameter Exploration"
git push -u origin master
```

`experiment_results/results.json` dan `results.md` boleh ikut di-push sebagai bukti hasil aktual.
Kumpulkan link repo di LMS.
