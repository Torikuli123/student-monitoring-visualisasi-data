# Data to Insight · Student Monitoring

Dashboard interaktif Streamlit untuk tugas Visualisasi Data (Project Based Assignment).

## Cara menjalankan
```bash
pip install -r requirements.txt
python cleaning.py        # opsional: menghasilkan data bersih + docs/log_cleaning.txt
streamlit run app.py
```

## Struktur
| Berkas | Fungsi |
|---|---|
| `data/student_monitoring_data.csv` | Dataset mentah (15.000 baris x 9 kolom) |
| `data/student_monitoring_clean.csv` | Dataset setelah cleaning (14 kolom) |
| `cleaning.py` | Audit kualitas data, cleaning, kolom turunan |
| `docs/log_cleaning.txt` | Dokumentasi proses cleaning |
| `app.py` | Dashboard (KPI, 8 visualisasi, tabel prioritas, insight) |

## Pemenuhan tugas
- **Tahap 1:** dataset 15.000 catatan, 500 mahasiswa, 30 hari (1-30 Des 2024), 9 atribut. *Isi sumber data di sini.*
- **Tahap 2:** missing value, duplikat, outlier (IQR), format tanggal, kategori, numerik, dan jam kelas diperiksa.
- **Tahap 3 (EDA):** statistik deskriptif, distribusi, perbandingan kategori, tren harian, korelasi.
- **Tahap 4:** 8 visualisasi, 7 jenis (donut, line, bar [stacked dan grouped], box, heatmap, histogram, scatter), tiap grafik
  menjawab satu pertanyaan analisis dan memuat alasan pemilihan jenis grafik.

## Temuan utama
1. Seluruh catatan absen berisiko tinggi.
2. Stres GSR >= 3,5 hampir selalu berisiko tinggi.
3. Risiko sedang vs rendah dibedakan oleh kecemasan tinggi/mood rendah.
4. Jam tidur dan indikator numerik lain nyaris tidak berkorelasi.
