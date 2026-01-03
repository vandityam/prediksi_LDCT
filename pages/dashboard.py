import streamlit as st
import pandas as pd
import plotly.express as px
from scipy.stats import spearmanr, pearsonr

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="Analisis Korelasi LD Guru & CT Siswa",
    layout="wide"
)

# ======================================================
# LOAD CSS
# ======================================================
def load_css():
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ======================================================
# HEADER
# ======================================================
st.markdown(
    """
    <div style='text-align:center;'>
        <h2>📊 Dashboard Analisis Korelasi</h2>
        <p>Literasi Digital Guru & Computational Thinking Siswa</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()

# ======================================================
# LOAD & PREPROCESS DATA
# ======================================================
@st.cache_data
def load_data():
    df_guru = pd.read_csv("files/dashboard_dataguru.csv")
    df_siswa = pd.read_csv("files/dashboard_datasiswa.csv")

    df_guru = df_guru.rename(columns={"Asal Instansi": "SekolahNama"})

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
# SEKOLAH KEY (SAMA DENGAN IPYNB)
# ======================================================
def key_school(name):
    if pd.isna(name):
        return ""
    return " ".join(str(name).lower().strip().split()[:4])


df_guru["sekolah_key"] = df_guru["SekolahNama"].apply(key_school)
df_siswa["sekolah_key"] = df_siswa["SekolahNama"].apply(key_school)

sekolah_sama = sorted(
    set(df_guru["sekolah_key"]) & set(df_siswa["sekolah_key"])
)

# ======================================================
# AGREGASI SEKOLAH (INTI)
# ======================================================
df_guru_match = df_guru[df_guru["sekolah_key"].isin(sekolah_sama)]
df_siswa_match = df_siswa[df_siswa["sekolah_key"].isin(sekolah_sama)]

df_korelasi = pd.merge(
    df_guru_match.groupby("sekolah_key", as_index=False)
        .agg(LD_Guru_Mean=("Mean_LD", "mean")),
    df_siswa_match.groupby("sekolah_key", as_index=False)
        .agg(CT_Siswa_Norm=("CT_norm", "mean")),
    on="sekolah_key"
).round(3)

# ======================================================
# TABS LAYOUT
# ======================================================
tab1, tab2, tab3 = st.tabs([
    "📌 Korelasi Antar Sekolah",
    "📊 Korelasi Antar Sekolah per Level",
    "🏫 Korelasi Per Level di Dalam Sekolah"
])

# ======================================================
# TAB 1 — KORELASI ANTAR SEKOLAH
# ======================================================
with tab1:
    st.subheader("Korelasi Antar Sekolah (Agregat)")

    r, p = spearmanr(
        df_korelasi["LD_Guru_Mean"],
        df_korelasi["CT_Siswa_Norm"]
    )

    c1, c2 = st.columns([2, 1])

    with c1:
        fig = px.scatter(
            df_korelasi,
            x="LD_Guru_Mean",
            y="CT_Siswa_Norm",
            trendline="ols",
            hover_data=["sekolah_key"],
            labels={
                "LD_Guru_Mean": "Rata-rata Literasi Digital Guru",
                "CT_Siswa_Norm": "Rata-rata CT Siswa"
            }
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.metric("Spearman r", round(r, 3))
        st.metric("p-value", round(p, 3))

        st.info(
            "Hubungan signifikan secara statistik"
            if p < 0.05 else
            "Hubungan kuat namun belum signifikan"
        )

    st.markdown("#### 📋 Data Agregat per Sekolah")
    st.dataframe(df_korelasi, use_container_width=True)

# ======================================================
# TAB 2 — KORELASI ANTAR SEKOLAH PER LEVEL
# ======================================================
with tab2:
    st.subheader("Korelasi Antar Sekolah per Level")

    level_pilih = st.selectbox(
        "Pilih Level",
        sorted(df_guru["Level_LD"].dropna().unique())
    )

    guru_lvl = df_guru[df_guru["Level_LD"] == level_pilih]
    siswa_lvl = df_siswa[df_siswa["Level_CT"] == level_pilih]

    sekolah_lvl = sorted(
        set(guru_lvl["sekolah_key"]) & set(siswa_lvl["sekolah_key"])
    )

    if len(sekolah_lvl) < 3:
        st.warning("Jumlah sekolah belum mencukupi untuk analisis korelasi.")
    else:
        df_lvl = pd.merge(
            guru_lvl[guru_lvl["sekolah_key"].isin(sekolah_lvl)]
                .groupby("sekolah_key")["Mean_LD"].mean()
                .reset_index(name="LD_Guru_Mean"),
            siswa_lvl[siswa_lvl["sekolah_key"].isin(sekolah_lvl)]
                .groupby("sekolah_key")["CT_norm"].mean()
                .reset_index(name="CT_Siswa_Norm"),
            on="sekolah_key"
        )

        r, p = spearmanr(
            df_lvl["LD_Guru_Mean"],
            df_lvl["CT_Siswa_Norm"]
        )

        st.metric("Spearman r", round(r, 3))
        st.metric("p-value", round(p, 3))

        st.dataframe(df_lvl.round(3), use_container_width=True)

# ======================================================
# TAB 3 — KORELASI PER LEVEL DALAM SEKOLAH
# ======================================================
with tab3:
    st.subheader("Korelasi Per Level di Dalam Sekolah")

    hasil = []

    for sekolah in sekolah_sama:
        guru_f = df_guru[df_guru["sekolah_key"] == sekolah]
        siswa_f = df_siswa[df_siswa["sekolah_key"] == sekolah]

        guru_lvl = guru_f.groupby("Level_LD")["Mean_LD"].mean().reset_index()
        siswa_lvl = siswa_f.groupby("Level_CT")["CT_norm"].mean().reset_index()

        guru_lvl["Level"] = guru_lvl["Level_LD"].str.lower()
        siswa_lvl["Level"] = siswa_lvl["Level_CT"].str.lower()

        df_lvl = pd.merge(
            guru_lvl[["Level", "Mean_LD"]],
            siswa_lvl[["Level", "CT_norm"]],
            on="Level"
        )

        if len(df_lvl) >= 3:
            r, p = pearsonr(df_lvl["Mean_LD"], df_lvl["CT_norm"])
            interpret = "Signifikan" if p < 0.05 else "Tidak signifikan"
        else:
            r, p, interpret = None, None, "Data tidak mencukupi"

        hasil.append({
            "Sekolah": sekolah,
            "r": None if r is None else round(r, 3),
            "p": None if p is None else round(p, 3),
            "Interpretasi": interpret
        })

    st.dataframe(pd.DataFrame(hasil), use_container_width=True)

    st.info(
        "Analisis ini bersifat eksploratif untuk melihat pola hubungan "
        "di dalam masing-masing sekolah berdasarkan level."
    )
