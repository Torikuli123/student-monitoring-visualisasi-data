"""Student Wellbeing Monitor - Dashboard Streamlit."""
import pandas as pd
import plotly.express as px
import streamlit as st

from cleaning import NUMERIK, URUT_KEHADIRAN, URUT_RISIKO, load_clean

st.set_page_config(page_title="Student Wellbeing Monitor", page_icon="🎓", layout="wide")

WARNA_RISIKO = {"Rendah": "#5AA9E6", "Sedang": "#E9A23B", "Tinggi": "#C6534B"}
WARNA_HADIR = {"Hadir": "#245B8F", "Terlambat": "#E9A23B", "Absen": "#C6534B"}
WARNA_INDIKATOR = {"Kecemasan": "#E9A23B", "Mood": "#245B8F"}
TEMPLATE = "plotly_white"

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
:root { --navy:#102B46; --navy-2:#1B4568; --amber:#F0A23B; --paper:#F3F5F7; --ink:#17324D; }
.stApp { background:var(--paper); color:var(--ink); font-family:'DM Sans',sans-serif; }
h1,h2,h3,[data-testid="stMetricValue"] { font-family:'Manrope','DM Sans',sans-serif; }
h1,h2,h3 { color:var(--navy); }
.hero { background:linear-gradient(112deg,#102B46 0%,#1B4568 65%,#27628A 100%); color:#fff;
  border-radius:5px; padding:28px 32px; margin:4px 0 22px; border-bottom:4px solid var(--amber); }
.hero h1 { color:#fff; font-size:30px; line-height:1.2; margin:0 0 8px; }
.hero p { color:#D8E4EF; margin:0; font-size:14px; }
div[data-testid="stMetric"] { background:#fff; border:1px solid #D8E0E7; border-top:3px solid var(--navy-2);
  padding:14px 16px; border-radius:4px; box-shadow:0 2px 8px #102B4610; }
div[data-testid="stMetricLabel"] { color:#64788A; font-size:13px; }
div[data-testid="stMetricValue"] { color:var(--navy); font-size:27px; }
div[data-testid="stTabs"] button { color:var(--navy); font-weight:700; }
div[data-testid="stTabs"] button[aria-selected="true"] { border-bottom-color:var(--amber); color:var(--navy); }
div[data-testid="stExpander"] { background:#fff; border:1px solid #D8E0E7; border-radius:4px; }
.chart-question { color:#52697D; font-size:13px; margin-top:-10px; margin-bottom:4px; }
.chart-note { color:#718293; font-size:12px; margin-top:-10px; }
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_data
def muat_data():
    return load_clean("data/student_monitoring_data.csv")


df = muat_data()
tmin, tmax = df["Tanggal"].min().date(), df["Tanggal"].max().date()

st.sidebar.markdown("## 🎓 Student Wellbeing Monitor")
st.sidebar.caption("Dashboard pemantauan kondisi dan sinyal risiko mahasiswa.")
st.sidebar.markdown("**Sumber data**  \nDataset student monitoring")
st.sidebar.markdown(f"**Catatan**  \n{len(df):,} record · {df['Student_ID'].nunique()} mahasiswa".replace(",", "."))
st.sidebar.markdown(f"**Periode**  \n{tmin:%d %b %Y} – {tmax:%d %b %Y}")

st.markdown(
    '<div class="hero"><h1>Student Wellbeing Monitor: Membaca Sinyal Risiko Mahasiswa</h1>'
    '<p>Kehadiran · stres · tidur · kecemasan · mood · tingkat risiko</p></div>',
    unsafe_allow_html=True,
)

with st.expander("Atur filter analisis", expanded=True):
    filter_date, filter_attendance, filter_risk, filter_time = st.columns([1.45, 1.2, 1.1, 1.25])
    with filter_date:
        rentang = st.date_input("Rentang tanggal", (tmin, tmax), min_value=tmin, max_value=tmax)
    with filter_attendance:
        kehadiran = st.multiselect("Status kehadiran", URUT_KEHADIRAN, default=URUT_KEHADIRAN)
    with filter_risk:
        risiko = st.multiselect("Tingkat risiko", URUT_RISIKO, default=URUT_RISIKO)
    with filter_time:
        jam_mulai = st.multiselect(
            "Jam mulai kelas", sorted(df["Jam_Mulai"].unique()), default=sorted(df["Jam_Mulai"].unique()),
            format_func=lambda x: f"{int(x):02d}:00",
        )

if isinstance(rentang, tuple) and len(rentang) == 2:
    awal, akhir = rentang
else:
    awal = akhir = rentang[0] if isinstance(rentang, tuple) else rentang

f = df[
    df["Tanggal"].between(pd.Timestamp(awal), pd.Timestamp(akhir))
    & df["Kehadiran"].isin(kehadiran)
    & df["Risiko"].isin(risiko)
    & df["Jam_Mulai"].isin(jam_mulai)
].copy()

if f.empty:
    st.warning("Tidak ada data untuk kombinasi filter ini. Longgarkan filter di atas.")
    st.stop()

tinggi = (f["Risiko"] == "Tinggi").mean()
st.caption("Ringkasan mengikuti filter yang dipilih. Stres (GSR) berskala 0,5–5; kecemasan dan mood 1–10.")
k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("🗂️ Total catatan", f"{len(f):,}".replace(",", "."), help="Jumlah record sesuai filter")
k2.metric("🔴 Risiko tinggi", f"{tinggi:.1%}", help="Proporsi record dengan risiko tinggi")
k3.metric("📅 Tingkat absen", f"{(f['Kehadiran'] == 'Absen').mean():.1%}")
k4.metric("⚡ Rata-rata stres", f"{f['Stres_GSR'].mean():.2f} / 5")
k5.metric("🌙 Rata-rata tidur", f"{f['Jam_Tidur'].mean():.1f} jam")
k6.metric("🧠 Rata-rata cemas", f"{f['Kecemasan'].mean():.1f} / 10")

tab_ringkasan, tab_waktu, tab_faktor, tab_prioritas = st.tabs(
    ["Ringkasan", "Pola Waktu", "Faktor Risiko", "Mahasiswa Prioritas & Insight"]
)

with tab_ringkasan:
    st.subheader("Gambaran tingkat risiko")
    st.markdown('<div class="chart-question">Pertanyaan analisis: Bagaimana komposisi risiko pada catatan terpilih?</div>', unsafe_allow_html=True)
    d = f["Risiko"].value_counts().reindex(URUT_RISIKO).dropna().reset_index()
    d.columns = ["Risiko", "Jumlah"]
    fig = px.pie(d, names="Risiko", values="Jumlah", hole=0.58, color="Risiko",
                 color_discrete_map=WARNA_RISIKO, template=TEMPLATE)
    fig.update_traces(textinfo="percent+label", sort=False)
    fig.update_layout(showlegend=False, margin=dict(t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<div class="chart-note">Donut dipilih untuk memperlihatkan proporsi dari satu keseluruhan dengan tiga kategori.</div>', unsafe_allow_html=True)

with tab_waktu:
    st.subheader("Perubahan risiko dari hari ke hari")
    st.markdown('<div class="chart-question">Pertanyaan analisis: Apakah persentase risiko tinggi berubah sepanjang periode?</div>', unsafe_allow_html=True)
    t = f.groupby("Tanggal").agg(
        Persen_Tinggi=("Risiko", lambda x: (x == "Tinggi").mean() * 100)).reset_index()
    fig = px.line(t, x="Tanggal", y="Persen_Tinggi", markers=True, template=TEMPLATE,
                  labels={"Persen_Tinggi": "Risiko tinggi (%)", "Tanggal": "Tanggal"})
    fig.update_traces(line_color=WARNA_RISIKO["Tinggi"])
    fig.update_yaxes(range=[0, max(100, t["Persen_Tinggi"].max() + 5)] if len(t) else None)
    fig.update_layout(margin=dict(t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<div class="chart-note">Line chart dipilih untuk menonjolkan arah dan perubahan nilai berdasarkan waktu.</div>', unsafe_allow_html=True)

with tab_faktor:
    st.subheader("Kehadiran dan risiko")
    st.markdown('<div class="chart-question">Pertanyaan analisis: Bagaimana komposisi risiko berbeda menurut status kehadiran?</div>', unsafe_allow_html=True)
    x = pd.crosstab(f["Kehadiran"], f["Risiko"], normalize="index").mul(100).reset_index()
    x = x.melt(id_vars="Kehadiran", var_name="Risiko", value_name="Persen")
    fig = px.bar(x, x="Kehadiran", y="Persen", color="Risiko", barmode="stack",
                 category_orders={"Kehadiran": URUT_KEHADIRAN, "Risiko": URUT_RISIKO},
                 color_discrete_map=WARNA_RISIKO, template=TEMPLATE,
                 labels={"Kehadiran": "Status kehadiran", "Persen": "Persentase catatan (%)"}, text_auto=".0f")
    fig.update_layout(margin=dict(t=10, b=10), legend_title_text="Tingkat risiko")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<div class="chart-note">Stacked bar 100% dipilih untuk membandingkan komposisi risiko antarstatus.</div>', unsafe_allow_html=True)

    st.divider()
    factor_left, factor_right = st.columns(2)
    with factor_left:
        st.subheader("Sebaran stres menurut risiko")
        st.markdown('<div class="chart-question">Pertanyaan analisis: Bagaimana distribusi stres di tiap kelompok risiko?</div>', unsafe_allow_html=True)
        fig = px.box(f, x="Risiko", y="Stres_GSR", color="Risiko", template=TEMPLATE,
                     category_orders={"Risiko": URUT_RISIKO}, color_discrete_map=WARNA_RISIKO,
                     labels={"Risiko": "Tingkat risiko", "Stres_GSR": "Stres (GSR)"})
        fig.update_layout(showlegend=False, margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('<div class="chart-note">Box plot memperlihatkan median, sebaran, dan pencilan tiap kelompok.</div>', unsafe_allow_html=True)

    with factor_right:
        st.subheader("Profil kecemasan dan mood")
        st.markdown('<div class="chart-question">Pertanyaan analisis: Bagaimana rata-rata kecemasan dan mood pada tiap risiko?</div>', unsafe_allow_html=True)
        p = f.groupby("Risiko", observed=True)[["Kecemasan", "Mood"]].mean().reset_index()
        p = p.melt(id_vars="Risiko", var_name="Indikator", value_name="Rata-rata (1–10)")
        fig = px.bar(p, x="Risiko", y="Rata-rata (1–10)", color="Indikator", barmode="group",
                     category_orders={"Risiko": URUT_RISIKO}, template=TEMPLATE, text_auto=".1f",
                     color_discrete_map=WARNA_INDIKATOR,
                     labels={"Risiko": "Tingkat risiko", "Rata-rata (1–10)": "Skor rata-rata"})
        fig.update_layout(margin=dict(t=10, b=10), legend_title_text="Indikator")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('<div class="chart-note">Grouped bar memudahkan perbandingan dua indikator di tiap kelompok risiko.</div>', unsafe_allow_html=True)

    st.divider()
    st.subheader("Hubungan antarindikator")
    st.markdown('<div class="chart-question">Pertanyaan analisis: Seberapa kuat hubungan linear antarindikator numerik?</div>', unsafe_allow_html=True)
    corr = f[NUMERIK].corr().round(2)
    nama = {"Stres_GSR": "Stres", "Jam_Tidur": "Tidur", "Kecemasan": "Kecemasan", "Mood": "Mood"}
    corr = corr.rename(index=nama, columns=nama)
    fig = px.imshow(corr, text_auto=True, zmin=-1, zmax=1, color_continuous_scale="RdBu_r",
                    template=TEMPLATE, labels={"color": "Korelasi"})
    fig.update_layout(margin=dict(t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<div class="chart-note">Heatmap merangkum banyak pasangan korelasi dalam satu tampilan.</div>', unsafe_allow_html=True)

    stress_left, stress_right = st.columns(2)
    with stress_left:
        st.subheader("Distribusi tingkat stres")
        st.markdown('<div class="chart-question">Pertanyaan analisis: Nilai stres mana yang paling sering muncul?</div>', unsafe_allow_html=True)
        fig = px.histogram(f, x="Stres_GSR", nbins=30, color="Risiko", template=TEMPLATE,
                           category_orders={"Risiko": URUT_RISIKO}, color_discrete_map=WARNA_RISIKO,
                           labels={"Stres_GSR": "Stres (GSR)", "count": "Jumlah catatan"})
        fig.add_vline(x=3.5, line_dash="dash", line_color="#444", annotation_text="3,5", annotation_position="top")
        fig.update_layout(barmode="stack", yaxis_title="Jumlah catatan", margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('<div class="chart-note">Histogram dipilih untuk melihat bentuk distribusi satu variabel numerik.</div>', unsafe_allow_html=True)

    with stress_right:
        st.subheader("Tidur dan stres")
        st.markdown('<div class="chart-question">Pertanyaan analisis: Apakah durasi tidur berkaitan dengan tingkat stres?</div>', unsafe_allow_html=True)
        sampel = f.sample(min(len(f), 2500), random_state=42)
        fig = px.scatter(sampel, x="Jam_Tidur", y="Stres_GSR", color="Risiko", opacity=0.55,
                         template=TEMPLATE, category_orders={"Risiko": URUT_RISIKO},
                         color_discrete_map=WARNA_RISIKO,
                         labels={"Jam_Tidur": "Jam tidur", "Stres_GSR": "Stres (GSR)"})
        fig.update_layout(margin=dict(t=10, b=10), legend_title_text="Tingkat risiko")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('<div class="chart-note">Scatter plot memperlihatkan hubungan dua variabel numerik pada tiap catatan.</div>', unsafe_allow_html=True)

with tab_prioritas:
    st.subheader("Sepuluh mahasiswa untuk ditindaklanjuti")
    st.markdown('<div class="chart-question">Daftar diurutkan berdasarkan persentase hari berisiko tinggi, lalu rata-rata stres.</div>', unsafe_allow_html=True)
    prio = (
        f.groupby("Student_ID")
        .agg(Catatan=("Risiko", "size"),
             Hari_Risiko_Tinggi=("Risiko", lambda x: int((x == "Tinggi").sum())),
             Hari_Absen=("Kehadiran", lambda x: int((x == "Absen").sum())),
             Rata2_Stres=("Stres_GSR", "mean"))
        .assign(Persen_Risiko_Tinggi=lambda x: (x["Hari_Risiko_Tinggi"] / x["Catatan"] * 100).round(1),
                Rata2_Stres=lambda x: x["Rata2_Stres"].round(2))
        .sort_values(["Persen_Risiko_Tinggi", "Rata2_Stres"], ascending=False)
        .head(10).reset_index()
    )
    st.dataframe(prio, use_container_width=True, hide_index=True)
    st.divider()
    st.subheader("Insight & rekomendasi")

    def pct(x):
        return "–" if pd.isna(x) else f"{x:.1%}"

    def num(x, d=2):
        return "–" if pd.isna(x) else f"{x:.{d}f}"

    absen = f[f["Kehadiran"] == "Absen"]
    stres_tinggi = f[f["Stres_GSR"] >= 3.5]
    nonabsen_tinggi = f[(f["Kehadiran"] != "Absen") & (f["Risiko"] == "Tinggi")]
    rata = f.groupby("Risiko", observed=True)[["Kecemasan", "Mood", "Stres_GSR"]].mean()
    r_tidur = f["Jam_Tidur"].corr(f["Stres_GSR"])
    st.markdown(
        f"""
1. **Absen hampir selalu berarti risiko tinggi.** Dari {len(absen)} catatan absen,
   **{pct((absen['Risiko'] == 'Tinggi').mean() if len(absen) else float('nan'))}** berstatus risiko tinggi; hadir atau terlambat tidak menunjukkan pola serupa.
2. **Stres GSR ≥ 3,5 menandai risiko tinggi.** Sebanyak **{pct((stres_tinggi['Risiko'] == 'Tinggi').mean() if len(stres_tinggi) else float('nan'))}** catatan
   dengan stres di atas ambang itu berisiko tinggi. Pada mahasiswa yang tidak absen, stres rata-rata
   kelompok tinggi **{num(nonabsen_tinggi['Stres_GSR'].mean())}** (kelompok lain sekitar 2,0).
3. **Risiko sedang dan rendah dibedakan oleh kondisi psikologis, bukan stres.** Kelompok sedang memiliki kecemasan
   rata-rata **{num(rata['Kecemasan'].get('Sedang', float('nan')), 1)}** dan mood **{num(rata['Mood'].get('Sedang', float('nan')), 1)}**, sedangkan kelompok rendah
   kecemasan **{num(rata['Kecemasan'].get('Rendah', float('nan')), 1)}** dan mood **{num(rata['Mood'].get('Rendah', float('nan')), 1)}**.
4. **Jam tidur tidak berhubungan dengan indikator lain.** Korelasi tidur dengan stres hanya **{num(r_tidur)}**,
   dan korelasi antarindikator numerik mendekati nol.
5. **Rekomendasi.** Prioritaskan tindak lanjut pada mahasiswa dengan hari absen berulang atau stres ≥ 3,5, dan
   pantau kecemasan tinggi bersama mood rendah sebagai peringatan dini risiko sedang.
   Intervensi yang hanya menargetkan jam tidur tidak didukung data ini.
"""
    )
    with st.expander("Catatan metodologi"):
        st.markdown(
            """
- Data dibersihkan melalui `cleaning.py` (cek missing value, duplikat, outlier IQR, format tanggal, kategori,
  dan pembuatan kolom turunan). Ringkasannya ada di `docs/log_cleaning.txt`.
- Pola di atas adalah hubungan statistik pada data ini, bukan bukti sebab-akibat.
- Ambang stres 3,5 ditetapkan dari pola data, bukan standar klinis.
"""
        )