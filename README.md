# RAG Parameter Exploration

> Petunjuk (hapus sebelum dikumpulkan): semua bagian **[ISI SENDIRI]** diisi dari `experiment_results/results.md`
> (hasil aktual aplikasi) dan pendapatmu sendiri. Jika memakai PDF/pertanyaan lain, ubah bagian Informasi Eksperimen.

## Informasi Eksperimen

**Nama PDF:**
materi_pdina.pdf

**Jumlah halaman PDF:**
8

**Isi / topik PDF secara singkat:**
Dokumentasi model P-DINA (probabilistic DINA dengan variational EM) dari proyek CDA-CDM: intuisi model, persamaan,
proses training, seleksi hyperparameter, kebijakan diagnosis (τ, n_min, δ), hasil evaluasi, dan keterbatasannya.

## Pertanyaan Pengujian

### Pertanyaan 1

Berapa nilai threshold τ dan n_min yang dipilih, dan bagaimana cara memilihnya?

### Pertanyaan 2

Kenapa P-DINA tidak memakai algoritma EM DINA klasik?

## Baseline Configuration

```
Temperature:     0.2
TOP_K:           4
Chunk Size:      100 (token, dihitung dengan tokenizer model embedding)
Chunk Overlap:   20 (token)
Embedding Model: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
LLM Model:       openai/gpt-oss-120b (Groq)
```

Chunks stored pada baseline: [ISI SENDIRI — dari baris "Ingest baseline" di results.md]

## Experiment 1 - Temperature

Gunakan pertanyaan yang sama pada seluruh percobaan.

### Temperature = 0.0

**Actual Output**

[ISI SENDIRI]

**Observation**

[ISI SENDIRI]

### Temperature = 0.2

**Actual Output**

[ISI SENDIRI]

**Observation**

[ISI SENDIRI]

### Temperature = 0.8

**Actual Output**

[ISI SENDIRI]

**Observation**

[ISI SENDIRI]

### Kesimpulan Experiment Temperature

**Apa perubahan yang paling terlihat?**

[ISI SENDIRI]

**Menurut kalian nilai mana yang paling cocok untuk aplikasi RAG ini?**

[ISI SENDIRI]

**Kenapa?**

[ISI SENDIRI]

## Experiment 2 - TOP_K

### TOP_K = 1

**Actual Output**

[ISI SENDIRI]

**Sources / Similarity Score**

[ISI SENDIRI]

**Observation**

[ISI SENDIRI]

### TOP_K = 4

**Actual Output**

[ISI SENDIRI]

**Sources / Similarity Score**

[ISI SENDIRI]

**Observation**

[ISI SENDIRI]

### TOP_K = 8

**Actual Output**

[ISI SENDIRI]

**Sources / Similarity Score**

[ISI SENDIRI]

**Observation**

[ISI SENDIRI]

### Kesimpulan Experiment TOP_K

**Apakah TOP_K yang lebih besar selalu menghasilkan jawaban yang lebih baik?**

[ISI SENDIRI]

**Menurut kalian TOP_K mana yang paling cocok untuk PDF yang digunakan?**

[ISI SENDIRI]

**Kenapa?**

[ISI SENDIRI]

## Experiment 3 - Chunk Size

Gunakan:

```
CHUNK_OVERLAP = 20
```

untuk seluruh percobaan.

### Chunk Size = 50

**Chunks Stored**

[ISI SENDIRI]

**Actual Output**

[ISI SENDIRI]

**Sources / Similarity Score**

[ISI SENDIRI]

**Observation**

[ISI SENDIRI]

### Chunk Size = 100

**Chunks Stored**

[ISI SENDIRI]

**Actual Output**

[ISI SENDIRI]

**Sources / Similarity Score**

[ISI SENDIRI]

**Observation**

[ISI SENDIRI]

### Chunk Size = 120

**Chunks Stored**

[ISI SENDIRI]

**Actual Output**

[ISI SENDIRI]

**Sources / Similarity Score**

[ISI SENDIRI]

**Observation**

[ISI SENDIRI]

### Kesimpulan Experiment Chunk Size

**Apa hubungan Chunk Size dengan jumlah chunk yang tersimpan?**

[ISI SENDIRI]

**Apakah chunk yang lebih kecil selalu menghasilkan retrieval yang lebih baik?**

[ISI SENDIRI]

**Menurut kalian Chunk Size mana yang paling cocok?**

[ISI SENDIRI]

**Kenapa?**

[ISI SENDIRI]

## Experiment 4 - Chunk Overlap

Gunakan:

```
CHUNK_SIZE = 100
```

untuk seluruh percobaan.

### Chunk Overlap = 0

**Chunks Stored**

[ISI SENDIRI]

**Actual Output**

[ISI SENDIRI]

**Sources / Similarity Score**

[ISI SENDIRI]

**Observation**

[ISI SENDIRI]

### Chunk Overlap = 20

**Chunks Stored**

[ISI SENDIRI]

**Actual Output**

[ISI SENDIRI]

**Sources / Similarity Score**

[ISI SENDIRI]

**Observation**

[ISI SENDIRI]

### Chunk Overlap = 40

**Chunks Stored**

[ISI SENDIRI]

**Actual Output**

[ISI SENDIRI]

**Sources / Similarity Score**

[ISI SENDIRI]

**Observation**

[ISI SENDIRI]

### Kesimpulan Experiment Chunk Overlap

**Apa pengaruh Chunk Overlap yang kalian lihat?**

[ISI SENDIRI]

**Apakah overlap yang lebih besar selalu menghasilkan jawaban yang lebih baik?**

[ISI SENDIRI]

**Menurut kalian nilai mana yang paling cocok?**

[ISI SENDIRI]

## Final Configuration

```
Temperature:   [ISI SENDIRI]
TOP_K:         [ISI SENDIRI]
Chunk Size:    [ISI SENDIRI]
Chunk Overlap: [ISI SENDIRI]
```

[ISI SENDIRI — alasan memilih konfigurasi ini berdasarkan hasil eksperimen]

## Final Questions

**1. Parameter mana yang paling terasa memengaruhi hasil aplikasi kalian?**

[ISI SENDIRI]

**2. Apakah Temperature memengaruhi Retrieval atau Generation? Jelaskan.**

[ISI SENDIRI]

**3. Apakah TOP_K yang lebih besar selalu menghasilkan jawaban yang lebih baik?**

[ISI SENDIRI]

**4. Apa yang terjadi ketika Chunk Size dibuat lebih kecil?**

[ISI SENDIRI]

**5. Setelah melakukan eksperimen, apa fungsi Chunk Overlap menurut pemahaman kalian?**

[ISI SENDIRI]

**6. Kenapa perubahan Chunk Size dan Chunk Overlap membutuhkan ingestion ulang?**

[ISI SENDIRI]

**7. Kenapa perubahan Temperature tidak membutuhkan ingestion ulang?**

[ISI SENDIRI]

**8. Menurut kalian, apakah ada satu konfigurasi RAG yang akan selalu paling bagus untuk semua jenis dokumen?**

[ISI SENDIRI]

## Personal Reflection

**Bagian eksperimen mana yang hasilnya paling berbeda dari dugaan kalian?**

[ISI SENDIRI]

**Parameter mana yang awalnya kalian anggap tidak terlalu penting tetapi ternyata berpengaruh?**

[ISI SENDIRI]

**Setelah mengerjakan tugas ini, bagaimana kalian menjelaskan hubungan antara Retrieval dan Generation pada RAG?**

[ISI SENDIRI]

**Jika aplikasi ini dikembangkan lebih lanjut, parameter atau bagian apa lagi yang ingin kalian coba?**

[ISI SENDIRI]

## AI Usage

**AI tools yang digunakan**

[ISI SENDIRI]

**AI digunakan untuk membantu bagian apa?**

[ISI SENDIRI]

**Bagian eksperimen mana yang kalian lakukan dan evaluasi sendiri?**

[ISI SENDIRI]

---

## Cara Eksperimen Dijalankan

Eksperimen dijalankan dengan `run_rag_experiments.py`. Untuk setiap konfigurasi, script mengubah satu parameter di
`config.py`/`llm.py`, menghapus `qdrant_data/` saat server mati (khusus eksperimen chunking), menyalakan ulang server,
ingest ulang PDF yang sama, lalu mengirim pertanyaan yang sama ke `POST /ask`. Hasil mentah ada di
`experiment_results/results.json` dan `experiment_results/results.md`. Di akhir, `config.py` dan `llm.py` dikembalikan
ke nilai baseline.

```bash
python run_rag_experiments.py --pdf materi_pdina.pdf
```

Catatan: daftar `sources` dari `/ask` dideduplikasi per halaman oleh aplikasi, sehingga jumlah source yang terlihat bisa
lebih kecil dari TOP_K. Jumlah chunk yang benar-benar dikirim ke LLM tetap sama dengan TOP_K.
