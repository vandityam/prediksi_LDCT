import streamlit as st
import pandas as pd
import plotly.express as px

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="Data Guru - Literasi Digital",
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
# TITLE
# ======================================================
st.title("👩‍🏫 Data Guru")
st.markdown(
    "Analisis **Literasi Digital Guru** berdasarkan hasil kuesioner."
)

# ======================================================
# LOAD DATA
# ======================================================
@st.cache_data
def load_data():
    df = pd.read_csv("files/dashboard_dataguru.csv", sep=";")
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# ======================================================
# SIDEBAR FILTER
# ======================================================
st.sidebar.markdown("## 🔍 Filter Data Guru")

level_ld = st.sidebar.multiselect(
    "Level Literasi Digital",
    ["Rendah", "Sedang", "Tinggi"]
)

filtered = df.copy()
if level_ld: filtered = filtered[filtered["Level_LD"].isin(level_ld)]

st.sidebar.caption(f"Total data: **{len(filtered)} guru**")

# ======================================================
# KPI
# ======================================================
st.markdown("<div class='section-title'>📌 Statistik Ringkas</div>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
c1.metric("Jumlah Guru", len(filtered))
c2.metric("Rata-rata LD", round(filtered["Mean_LD"].mean(), 2))
c3.metric("LD Tertinggi", round(filtered["Mean_LD"].max(), 2))

# ======================================================
# DISTRIBUSI LEVEL
# ======================================================
st.markdown("<div class='section-title'>Distribusi Level Literasi Digital</div>", unsafe_allow_html=True)

fig_level = px.pie(
    filtered["Level_LD"].value_counts().reset_index(),
    names="Level_LD",
    values="count"
)
st.plotly_chart(fig_level, use_container_width=True)

# =============================================================================
# PERBANDINGAN PER INSTANSI (TOP N)
# =============================================================================
st.markdown("<div class='section-title'>Rata-rata LD per Sekolah</div>", unsafe_allow_html=True)

top_n = st.slider("Tampilkan Top-N Instansi", 5, 20, 10)

df_instansi = (
    filtered
    .groupby("Asal Instansi", as_index=False)["Mean_LD"]
    .mean()
    .sort_values("Mean_LD", ascending=False)
)

fig_instansi = px.bar(
    df_instansi.head(top_n),
    x="Mean_LD",
    y="Asal Instansi",
    orientation="h",
    title=f"Top {top_n} Instansi Berdasarkan Mean Literasi Digital"
)

fig_instansi.update_layout(height=350)
st.plotly_chart(fig_instansi, use_container_width=True)

# ======================================================
# TABEL
# ======================================================
st.markdown("<div class='section-title'>Data Guru</div>", unsafe_allow_html=True)

st.dataframe(
    filtered[
        ["NAMA", "Usia", "Asal Instansi", "Total_LD", "Mean_LD", "Level_LD"]
    ],
    use_container_width=True
)
