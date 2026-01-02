import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.linear_model import LinearRegression
import numpy as np

st.set_page_config(page_title="Dashboard Utama", layout="wide")

# ======================================================
# LOAD CSS
# ======================================================
def load_css():
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ======================================================
# TITLE
# ======================================================
st.markdown("<div class='main-title'>📊 Dashboard Utama</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='subtitle'>Korelasi & Prediksi Literasi Digital Guru "
    "terhadap Computational Thinking Siswa</div>",
    unsafe_allow_html=True
)

# ======================================================
# LOAD & PREPROCESS DATA
# ======================================================
@st.cache_data
def load_data():
    df_guru = pd.read_csv("files/dashboard_dataguru.csv", sep=";")
    df_siswa = pd.read_csv("files/dashboard_datasiswa.csv", sep=";")

    # Rename kolom sekolah (KUNCI)
    df_guru = df_guru.rename(columns={"Asal Instansi": "SekolahNama"})

    # Standarisasi nama sekolah
    for df in [df_guru, df_siswa]:
        df["SekolahNama"] = (
            df["SekolahNama"]
            .astype(str)
            .str.strip()
            .str.upper()
        )

    return df_guru, df_siswa

df_guru, df_siswa = load_data()

# ======================================================
# BUAT SEKOLAH KEY (FIX UTAMA)
# ======================================================
def key_school(name):
    if pd.isna(name):
        return ""
    return " ".join(str(name).lower().strip().split()[:4])

df_guru["sekolah_key"] = df_guru["SekolahNama"].apply(key_school)
df_siswa["sekolah_key"] = df_siswa["SekolahNama"].apply(key_school)

# ======================================================
# AGREGASI LEVEL SEKOLAH (PAKAI KEY)
# ======================================================
guru_avg = df_guru.groupby("sekolah_key", as_index=False).agg(
    LD_avg=("Mean_LD", "mean")
)

siswa_avg = df_siswa.groupby("sekolah_key", as_index=False).agg(
    CT_avg=("CT_norm", "mean")
)

df_merge = pd.merge(guru_avg, siswa_avg, on="sekolah_key", how="inner")

# ======================================================
# KPI
# ======================================================
st.markdown("<div class='section-title'>📌 Ringkasan Data</div>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
c1.metric("Jumlah Sekolah Yang Sama", df_merge["sekolah_key"].nunique())
c2.metric("Jumlah Guru", len(df_guru))
c3.metric("Jumlah Siswa", len(df_siswa))

# ======================================================
# TABEL PERBANDINGAN
# ======================================================

st.markdown("Pada Sekolah yang Sama")

# Ambil sekolah yang ada di kedua data
sekolah_sama = sorted(
    set(df_guru["sekolah_key"]) & set(df_siswa["sekolah_key"])
)

# Filter data guru
df_guru_match = df_guru[df_guru["sekolah_key"].isin(sekolah_sama)]

ld_sekolah = (
    df_guru_match
    .groupby("sekolah_key", as_index=False)
    .agg(
        LD_Guru_Mean=("Mean_LD", "mean"),
        count_guru=("sekolah_key", "count")   # jumlah guru per sekolah
    )
    .round(3)
)

# Filter data siswa
df_siswa_match = df_siswa[df_siswa["sekolah_key"].isin(sekolah_sama)]

ct_sekolah = (
    df_siswa_match
    .groupby("sekolah_key", as_index=False)
    .agg(
        CT_Siswa_Norm=("CT_norm", "mean"),
        count_siswa=("sekolah_key", "count")  # jumlah siswa per sekolah
    )
    .round(3)
)

# Gabungkan untuk korelasi
df_korelasi = pd.merge(
    ld_sekolah,
    ct_sekolah,
    on="sekolah_key",
    how="inner"
)

# Tampilkan tabel
st.dataframe(
    df_korelasi,
    use_container_width=True
)

# ======================================================
# KORELASI
# ======================================================
st.markdown("<div class='section-title'>Analisis Korelasi</div>", unsafe_allow_html=True)

corr_value = df_merge["LD_avg"].corr(df_merge["CT_avg"])

col1, col2 = st.columns([2, 1])

with col1:
    fig = px.scatter(
        df_merge,
        x="LD_avg",
        y="CT_avg",
        trendline="ols",
        hover_data=["sekolah_key"],
        labels={
            "LD_avg": "Rata-rata Literasi Digital Guru",
            "CT_avg": "Rata-rata CT Siswa"
        }
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.metric("Koefisien Korelasi (Pearson)", round(corr_value, 3))

    r = abs(corr_value)
    if r >= 0.7:
        interpretasi = "Hubungan kuat"
    elif r >= 0.4:
        interpretasi = "Hubungan sedang"
    elif r >= 0.2:
        interpretasi = "Hubungan lemah"
    else:
        interpretasi = "Tidak terdapat hubungan berarti"

    st.info(f"📌 **Interpretasi:** {interpretasi}")

# ======================================================
# ANALISIS KORELASI LANJUTAN
# ======================================================

from scipy.stats import spearmanr

st.markdown(
    "<div class='section-title'>Korelasi Antar Sekolah</div>",
    unsafe_allow_html=True
)

r, p = spearmanr(
    df_korelasi["LD_Guru_Mean"],
    df_korelasi["CT_Siswa_Norm"]
)

c1, c2 = st.columns(2)
c1.metric("Koefisien Korelasi Spearman (r)", round(r, 3))
c2.metric("p-value", round(p, 3))

if p < 0.05:
    ket = "Terdapat hubungan yang signifikan secara statistik."
else:
    ket = "Tidak terdapat hubungan yang signifikan secara statistik."

st.info(
    f"""
    **Penjelasan:**
    
    Analisis ini mengukur hubungan antara **rata-rata literasi digital guru**
    dan **rata-rata kemampuan Computational Thinking siswa** pada tingkat sekolah.
    
    Hasil menunjukkan bahwa {ket}
    """
)

st.markdown(
    "<div class='section-title'>Korelasi Antar Sekolah per Level</div>",
    unsafe_allow_html=True
)

level_pilih = st.selectbox(
    "Pilih Level",
    sorted(df_guru["Level_LD"].dropna().unique())
)

guru_lvl = df_guru[df_guru["Level_LD"] == level_pilih]
siswa_lvl = df_siswa[df_siswa["Level_CT"] == level_pilih]

sekolah_sama_lvl = sorted(
    set(guru_lvl["sekolah_key"]) & set(siswa_lvl["sekolah_key"])
)

if len(sekolah_sama_lvl) < 3:
    st.warning("Data sekolah pada level ini belum cukup untuk analisis korelasi.")
else:
    ld_lvl = (
        guru_lvl[guru_lvl["sekolah_key"].isin(sekolah_sama_lvl)]
        .groupby("sekolah_key")["Mean_LD"]
        .mean()
        .reset_index(name="LD_Guru_Mean")
    )

    ct_lvl = (
        siswa_lvl[siswa_lvl["sekolah_key"].isin(sekolah_sama_lvl)]
        .groupby("sekolah_key")["CT_norm"]
        .mean()
        .reset_index(name="CT_Siswa_Norm")
    )

    df_lvl = pd.merge(ld_lvl, ct_lvl, on="sekolah_key")

    r, p = spearmanr(df_lvl["LD_Guru_Mean"], df_lvl["CT_Siswa_Norm"])

    # Tampilkan hasil korelasi dalam dua kolom
    c1, c2 = st.columns(2)
    c1.metric("Koefisien Korelasi Spearman (r)", round(r, 3))
    c2.metric("p-value", round(p, 3))

    st.info(
        f"""
        **Penjelasan:**
        
        Analisis ini dilakukan untuk melihat hubungan literasi digital guru dan
        kemampuan CT siswa **pada level {level_pilih}**.
        
        Analisis ini membantu mengidentifikasi apakah pola hubungan berbeda
        pada masing-masing tingkat kemampuan.
        """
    )

from scipy.stats import pearsonr

st.markdown(
    "<div class='section-title'>Korelasi Per Level di Dalam Sekolah</div>",
    unsafe_allow_html=True
)

hasil = []

for sekolah in sekolah_sama:
    guru_filt = df_guru[df_guru["sekolah_key"] == sekolah]
    siswa_filt = df_siswa[df_siswa["sekolah_key"] == sekolah]

    guru_lvl = (
        guru_filt.groupby("Level_LD")["Mean_LD"]
        .mean()
        .reset_index(name="mean_LD")
    )

    siswa_lvl = (
        siswa_filt.groupby("Level_CT")["CT_norm"]
        .mean()
        .reset_index(name="mean_CT")
    )

    guru_lvl["Level"] = guru_lvl["Level_LD"].str.lower()
    siswa_lvl["Level"] = siswa_lvl["Level_CT"].str.lower()

    df_lvl = pd.merge(
        guru_lvl[["Level", "mean_LD"]],
        siswa_lvl[["Level", "mean_CT"]],
        on="Level"
    )

    if len(df_lvl) >= 3:
        r, p = pearsonr(df_lvl["mean_LD"], df_lvl["mean_CT"])
        interpret = "Signifikan" if p < 0.05 else "Tidak signifikan"
    else:
        r, p, interpret = None, None, "Data level tidak mencukupi"

    hasil.append({
        "Sekolah": sekolah,
        "r": None if r is None else round(r, 3),
        "p": None if p is None else round(p, 3),
        "Interpretasi": interpret
    })

df_hasil = pd.DataFrame(hasil)
st.dataframe(df_hasil, use_container_width=True)

st.info(
    """
    **Penjelasan:**
    
    Analisis ini dilakukan untuk melihat hubungan literasi digital guru dan
    kemampuan CT siswa **di dalam masing-masing sekolah berdasarkan level**.
    
    Tidak semua sekolah memiliki jumlah level yang cukup, sehingga pada
    beberapa sekolah korelasi tidak dapat dihitung.
    """
)

# ======================================================
# PREDIKSI
# ======================================================
st.markdown("<div class='section-title'>Prediksi CT Siswa</div>", unsafe_allow_html=True)

X = df_merge[["LD_avg"]]
y = df_merge["CT_avg"]

model = LinearRegression().fit(X, y)

ld_input = st.slider(
    "Masukkan nilai Literasi Digital Guru",
    float(X.min()),
    float(X.max()),
    float(X.mean())
)

ct_pred = model.predict([[ld_input]])[0]

c1, c2 = st.columns(2)
c1.metric("Prediksi Rata-rata CT Siswa", round(ct_pred, 3))
c2.metric("Koefisien Regresi", round(model.coef_[0], 3))
