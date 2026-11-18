# Evaluasi Perbandingan TF-IDF–SVM dan BERT untuk Klasifikasi Intent Layanan Perbankan serta Implementasinya pada Aplikasi Web

Skripsi ini membandingkan kedua model pada 77 intent berbahasa Inggris. Target demo minggu pertama adalah memuat pipeline TF-IDF–SVM di terminal laptop dan memprediksi satu pertanyaan dengan hasil yang sama seperti di Colab.

## Penyimpanan proyek

| Lokasi | Isi |
|---|---|
| Repo ini | Kode eksperimen, konfigurasi, manifes sumber, indeks pembagian, ringkasan audit, dan log penelitian |
| Drive · `data/raw/` | Berkas asli PolyAI |
| Drive · `data/processed/` | CSV fitting, validasi, dan test dengan ID baris |
| Drive · `models/` | Pipeline SVM dan checkpoint BERT |
| Drive · `results/` | Keluaran eksperimen dan bukti demo |

Backend FastAPI dan frontend Next.js mengikuti setelah pemilihan model. Baca [protokol audit](docs/audit-data.md) sebelum menyiapkan data. Keputusan metode dan hasil aktual dicatat di [log penelitian](LOGBOOK.md).
