"""Tahap 2 - Data Cleaning & Preprocessing (Student Monitoring)."""
import sys
from pathlib import Path
import pandas as pd

RAW = Path("data/student_monitoring_data.csv")
CLEAN = Path("data/student_monitoring_clean.csv")
LOG = Path("docs/log_cleaning.txt")

RENAME = {
    "Student ID": "Student_ID", "Date": "Tanggal", "Class Time": "Jam_Kelas",
    "Attendance Status": "Kehadiran", "Stress Level (GSR)": "Stres_GSR",
    "Sleep Hours": "Jam_Tidur", "Anxiety Level": "Kecemasan",
    "Mood Score": "Mood", "Risk Level": "Risiko",
}
KEHADIRAN = {"Present": "Hadir", "Late": "Terlambat", "Absent": "Absen"}
RISIKO = {"Low": "Rendah", "Medium": "Sedang", "High": "Tinggi"}
HARI = {0: "Senin", 1: "Selasa", 2: "Rabu", 3: "Kamis", 4: "Jumat", 5: "Sabtu", 6: "Minggu"}
URUT_KEHADIRAN = ["Hadir", "Terlambat", "Absen"]
URUT_RISIKO = ["Rendah", "Sedang", "Tinggi"]
NUMERIK = ["Stres_GSR", "Jam_Tidur", "Kecemasan", "Mood"]


def audit(df):
    """Pemeriksaan kualitas data pada data mentah (sudah di-rename)."""
    rep = {"baris": len(df), "kolom": df.shape[1]}
    rep["missing"] = df.isna().sum().to_dict()
    rep["duplikat_baris"] = int(df.duplicated().sum())
    rep["duplikat_student_tanggal"] = int(df.duplicated(["Student_ID", "Tanggal"]).sum())
    rep["tipe_data"] = df.dtypes.astype(str).to_dict()
    rep["kategori_kehadiran"] = sorted(df["Kehadiran"].astype(str).unique())
    rep["kategori_risiko"] = sorted(df["Risiko"].astype(str).unique())
    out = {}
    for c in NUMERIK:
        q1, q3 = df[c].quantile([.25, .75])
        iqr = q3 - q1
        n = int(((df[c] < q1 - 1.5 * iqr) | (df[c] > q3 + 1.5 * iqr)).sum())
        out[c] = {"min": float(df[c].min()), "max": float(df[c].max()), "outlier_iqr": n}
    rep["numerik"] = out
    return rep


def clean(df):
    df = df.rename(columns=RENAME).copy()
    before = audit(df)
    # teks: rapikan spasi, samakan penulisan kategori
    for c in ["Jam_Kelas", "Kehadiran", "Risiko"]:
        df[c] = df[c].astype(str).str.strip()
    df["Kehadiran"] = df["Kehadiran"].str.title().map(KEHADIRAN)
    df["Risiko"] = df["Risiko"].str.title().map(RISIKO)
    # tanggal -> datetime
    df["Tanggal"] = pd.to_datetime(df["Tanggal"], errors="coerce")
    # numerik -> tipe yang sesuai
    for c in NUMERIK:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    # hapus baris tidak valid / duplikat
    df = df.dropna().drop_duplicates().copy()
    # fitur turunan
    jam = df["Jam_Kelas"].str.extract(r"^(\d{1,2}):\d{2}-(\d{1,2}):\d{2}$").astype(float)
    df["Jam_Mulai"], df["Jam_Selesai"] = jam[0], jam[1]
    df["Durasi_Jam"] = df["Jam_Selesai"] - df["Jam_Mulai"]
    df["Hari"] = df["Tanggal"].dt.dayofweek.map(HARI)
    df["Kategori_Stres"] = pd.cut(df["Stres_GSR"], [0, 2, 3.5, 5.01],
                                  labels=["Rendah", "Sedang", "Tinggi"], right=False).astype(str)
    df["Kehadiran"] = pd.Categorical(df["Kehadiran"], URUT_KEHADIRAN, ordered=True)
    df["Risiko"] = pd.Categorical(df["Risiko"], URUT_RISIKO, ordered=True)
    df = df.sort_values(["Student_ID", "Tanggal"]).reset_index(drop=True)
    return df, before, audit(df.assign(Risiko=df["Risiko"].astype(str), Kehadiran=df["Kehadiran"].astype(str)))


def load_clean(path=RAW):
    return clean(pd.read_csv(path))[0]


if __name__ == "__main__":
    raw = pd.read_csv(RAW)
    df, before, after = clean(raw)
    df.to_csv(CLEAN, index=False)
    lines = ["LOG DATA CLEANING - STUDENT MONITORING", "=" * 40,
             f"Data mentah : {before['baris']} baris x {before['kolom']} kolom",
             f"Missing value: {sum(before['missing'].values())}",
             f"Baris duplikat: {before['duplikat_baris']}",
             f"Duplikat Student_ID+Tanggal: {before['duplikat_student_tanggal']}",
             f"Kategori kehadiran (mentah): {before['kategori_kehadiran']}",
             f"Kategori risiko (mentah)   : {before['kategori_risiko']}",
             "Outlier (IQR 1.5x) per variabel numerik:"]
    for k, v in before["numerik"].items():
        lines.append(f"  - {k}: min={v['min']}, max={v['max']}, outlier={v['outlier_iqr']}")
    lines += ["", f"Data bersih : {len(df)} baris x {df.shape[1]} kolom",
              f"Baris dibuang: {len(raw) - len(df)}", "", "Kolom turunan:",
              "  Jam_Mulai, Jam_Selesai, Durasi_Jam (dari Jam_Kelas), Hari (dari Tanggal),",
              "  Kategori_Stres (Rendah <2, Sedang 2-3,49, Tinggi >=3,5)"]
    LOG.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
