# Log penelitian Banking77

## 18 November 2026 · Setup minggu pertama

Repo GitHub proyek berhasil dikloning dalam keadaan kosong. Kode eksperimen Python, FastAPI, dan Next.js akan berbagi satu repo. Aturan commit dan pencatatan tersedia di `AGENTS.md`.

Protokol di `docs/audit-data.md` menetapkan pemeriksaan data sebelum pelatihan. Pemisahan berbasis kelompok teks mengurangi risiko pertanyaan identik tersebar pada fitting dan validasi.

## 18 November 2026 · Audit data dan pembagian untuk kedua model

Revisi PolyAI `57ec275d8078af65b7731c2a98be812d844a6d6b` menghasilkan 10.003 baris train dan 3.080 baris test dengan 77 intent. Semua teks dan label terisi. Semua label ada dalam daftar resmi. Audit setelah trim dan penyeragaman spasi menemukan empat kelompok duplikat di train, satu di test, serta tujuh pertanyaan unik yang muncul di kedua subset resmi. Label pada seluruh kelompok konsisten. Semua baris dipertahankan. Tujuh pasangan train–test tercatat di laporan untuk pembahasan evaluasi akhir.

Pembagian berstrata pada kelompok teks unik dengan seed 42 menghasilkan 8.003 baris fitting dan 2.000 validasi. Setiap subset mencakup 77 kelas. Pemeriksaan terhadap CSV dan indeks mengonfirmasi cakupan 10.003 ID train serta irisan ID dan teks kosong antarsubset. Dua eksekusi menghasilkan SHA-256 indeks yang sama, `609612f252faf7af963e08178b449d046d93ea0c03dedf4c30136ee2d01d28f0`.

Bukti tersimpan di `data/raw/manifest.json`, `data/processed/audit_report.json`, `data/processed/label_mapping.json`, dan `data/processed/split_indices.json`. Lingkungan lokal menggunakan Python 3.11.0 dan scikit-learn 1.6.1. Hasil pemeriksaan perangkat dan pustaka tersedia di `artifacts/env_info.json`.

## 24 November 2026 · Baseline TF-IDF–SVM di laptop

Satu konfigurasi awal memakai unigram, min_df 1, C 1, dan seed 42 untuk memeriksa alur pelatihan sampai prediksi dari disk. Skrip membaca train resmi dan indeks split 18 November. TF-IDF dan LinearSVC di-fit pada 8.003 pertanyaan. Macro-F1 pada 2.000 pertanyaan validasi dari 77 intent adalah **0,882217**. LinearSVC konvergen dalam 13 iterasi. Semua 2.000 prediksi identik setelah pipeline dimuat ulang.

Dalam proses terminal terpisah, model lokal dan salinannya di Drive sama-sama memprediksi `card_delivery_estimate` untuk “When will my card arrive?”. Model ada di Drive `Skripsi Banking77/models/svm_baseline_local.joblib`. Laporan ada di Drive `results/svm_baseline_local.json` dan di repo pada `artifacts/results/svm_baseline_local.json`. Checksum salinan model dan laporan pada Drive untuk desktop cocok dengan sumber lokal.

Notebook CPU siap di Drive pada `notebooks/svm_baseline.ipynb`. Pelatihan di Colab dan pemeriksaan label dari model Colab di terminal laptop masih menunggu eksekusi. Test resmi belum dievaluasi.
