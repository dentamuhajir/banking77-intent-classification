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

## Mengulang persiapan data

Jalankan dari root repo pada PowerShell dengan Python 3.11.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts/00_check_env.py --output artifacts/env_info.json
.\.venv\Scripts\python.exe scripts/01_prepare_data.py
```

Skrip membaca revisi dan checksum dari `data/raw/manifest.json`, mengunduh berkas asli yang belum tersedia, lalu memeriksa checksum sebelum memproses data. Di Colab, gunakan versi pustaka yang sama dan jalankan skrip dengan `--data-dir "/content/drive/MyDrive/Skripsi Banking77/data"` setelah Drive terpasang. ID baris dimulai dari 0 pada setiap CSV resmi. Daftar ID fitting dan validasi sama-sama merujuk ke `train.csv`.

Bandingkan `data/processed/split_indices.json` sesudah dua eksekusi. Ringkasan audit dan pasangan ID yang tumpang tindih antara train dan test tersedia di `data/processed/audit_report.json`.

## Baseline TF-IDF–SVM dan demo terminal

Untuk Colab, buka `Skripsi Banking77/notebooks/svm_baseline.ipynb` dari Google Drive dengan Google Colaboratory, gunakan runtime CPU, lalu jalankan semua sel. Notebook memakai salinan `03_train_svm.py`, `predict_cli.py`, dan `requirements.txt` di `notebooks/runner/` pada Drive. Sumber ketiganya ada di repo. Satu run membaca train resmi sesuai checksum dan ID split yang sudah diaudit, lalu menulis `models/svm_baseline_colab.joblib` dan `results/svm_baseline_colab.json` di Drive. Sel terakhir menampilkan label demo dan checksum model.

Sesudah berkas Colab tersinkron, jalankan dari root repo di laptop. Cocokkan checksum dan label terminal dengan keluaran sel terakhir di Colab.

```powershell
$modelColab = 'G:\My Drive\Skripsi Banking77\models\svm_baseline_colab.joblib'
Get-FileHash -Algorithm SHA256 -LiteralPath $modelColab
.\.venv\Scripts\python.exe scripts/predict_cli.py --model $modelColab 'When will my card arrive?'
```

Untuk mengulang pemeriksaan lokal dengan konfigurasi yang sama, gunakan perintah berikut. Hasilnya tersimpan di `artifacts/models/` dan `artifacts/results/`.

```powershell
.\.venv\Scripts\python.exe scripts/03_train_svm.py --output-dir artifacts --run-name local
```
