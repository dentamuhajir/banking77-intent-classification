# Protokol audit Banking77

Gunakan berkas `train.csv`, `test.csv`, dan `categories.json` dari satu revisi [Banking77 milik PolyAI](https://github.com/PolyAI-LDN/task-specific-datasets/tree/master/banking_data). Simpan salinan asli sebelum menyiapkan data turunan.

| Pemeriksaan | Isi laporan |
|---|---|
| Asal data | URL tiap berkas, revisi Git, tanggal akuisisi, dan SHA-256 |
| Struktur | Nama kolom, jumlah aktual train dan test, serta banyak label unik dalam daftar resmi. Acuan proposal adalah 10.003, 3.080, dan 77. |
| Kelengkapan | Jumlah teks kosong setelah trim, label kosong, label asing, dan ID baris yang terdampak |
| Distribusi | Jumlah baris tiap kelas serta ringkasan panjang teks dalam karakter dan kata untuk setiap subset resmi |
| Duplikat | Kelompokkan berdasarkan teks setelah trim dan penyeragaman spasi. Pertahankan kapitalisasi dan tanda baca. Hitung kelompok dan baris tambahan di dalam tiap subset, konflik label, serta irisan teks train–test. |
| Pembagian | Dari train resmi, buat fitting dan validasi sekitar 80/20 dengan seed 42 dan stratifikasi kelas. Kelompokkan teks identik. Laporkan jumlah aktual, kelas yang terwakili, irisan ID dan teks, serta hasil pengulangan split. |

ID baris harus merujuk ke subset resmi dan posisi baris pada berkas sumber. Pertahankan label asli dan simpan pemetaan menurut urutan daftar resmi. Catat tindakan dan jumlah baris terdampak bila ditemukan anomali. Tumpang tindih train–test dilaporkan untuk pembahasan. Penilaian performa pada test dijadwalkan setelah model dipilih melalui validasi.
