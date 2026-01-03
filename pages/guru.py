import streamlit as st
import pandas as pd
import plotly.express as px

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="Dashboard Guru - Literasi Digital PPKS Solo",
    layout="wide"
)

# ======================================================
# LOAD CSS
# ======================================================
def load_css():
    try:
        with open("style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except:
        pass

load_css()

# ======================================================
# HEADER
# ======================================================
st.markdown(
    """
    <div style='text-align:center; margin-bottom:10px;'>
        <h2>Dashboard Data Guru</h2>
        <p>
        Ringkasan <b>Literasi Digital Guru</b> berdasarkan penilaian Yayasan PPKS Solo
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# ======================================================
# LOAD DATA
# ======================================================
@st.cache_data
def load_data():
    df = pd.read_csv("files/dashboard_dataguru.csv")
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# ======================================================
# SIDEBAR FILTER
# ======================================================
st.sidebar.markdown("### 🔍 Filter Data Guru")

level_ld = st.sidebar.multiselect(
    "Level Literasi Digital",
    sorted(df["Level_LD"].dropna().unique())
)

instansi = st.sidebar.multiselect(
    "Instansi",
    sorted(df["Asal Instansi"].dropna().unique())
)

filtered = df.copy()
if level_ld:
    filtered = filtered[filtered["Level_LD"].isin(level_ld)]
if instansi:
    filtered = filtered[filtered["Asal Instansi"].isin(instansi)]

st.sidebar.markdown(
    f"<small>Total data: <b>{len(filtered)} guru</b></small>",
    unsafe_allow_html=True
)

# ======================================================
# INFO FILTER
# ======================================================
if level_ld or instansi:
    st.info("Filter aktif diterapkan pada data guru.")
else:
    st.info("Menampilkan seluruh data guru.")

# ======================================================
# KPI RINGKAS
# ======================================================
persen_ld_tinggi = (filtered["Level_LD"] == "Tinggi").mean() * 100
jumlah_instansi = filtered["Asal Instansi"].nunique()

k1, k2, k3, k4 = st.columns(4)

k1.metric("JUMLAH GURU", len(filtered))
k2.metric("JUMLAH SEKOLAH", jumlah_instansi)
k3.metric("RATA-RATA LD GURU", round(filtered["Mean_LD"].mean(), 2))
k4.metric("LD TERTINGGI", f"{persen_ld_tinggi:.1f}%")

st.markdown("---")

# ======================================================
# MAIN VISUAL (KIRI - KANAN)
# ======================================================
left, right = st.columns([2, 1])

# ------------------------------------------------------
# LEFT : SCATTER USIA vs MEAN_LD
# ------------------------------------------------------
with left:
    fig_scatter = px.scatter(
        filtered,
        x="Usia",
        y="Mean_LD",
        color="Level_LD",
        hover_data=["NAMA", "Asal Instansi"],
        title="Hubungan Usia Guru dan Literasi Digital",
        labels={
            "Usia": "Usia Guru",
            "Mean_LD": "Mean Literasi Digital"
        }
    )
    fig_scatter.update_layout(height=380)
    st.plotly_chart(fig_scatter, use_container_width=True)

# ------------------------------------------------------
# RIGHT : DISTRIBUSI LEVEL LD
# ------------------------------------------------------
with right:
    df_level = (
        filtered
        .groupby("Level_LD", as_index=False)
        .size()
        .rename(columns={"size": "Jumlah"})
    )

    fig_level = px.pie(
        df_level,
        values="Jumlah",
        names="Level_LD",
        title="Distribusi Level Literasi Digital"
    )

    fig_level.update_layout(height=380)
    st.plotly_chart(fig_level, use_container_width=True)

# ======================================================
# PERBANDINGAN INSTANSI
# ======================================================
st.markdown("### Rata-rata Literasi Digital per Instansi")

top_n = st.slider("Top Instansi", 5, 15, 8)

df_instansi = (
    filtered
    .groupby("Asal Instansi", as_index=False)["Mean_LD"]
    .mean()
    .sort_values("Mean_LD", ascending=False)
)

fig_bar = px.bar(
    df_instansi.head(top_n),
    x="Mean_LD",
    y="Asal Instansi",
    orientation="h",
    labels={
        "Mean_LD": "Rata-rata Literasi Digital",
        "Asal Instansi": "Instansi"
    }
)

fig_bar.update_layout(height=320)
st.plotly_chart(fig_bar, use_container_width=True)

# ======================================================
# TABEL DETAIL (OPTIONAL)
# ======================================================
with st.expander("📋 Lihat Data Detail Guru"):
    st.dataframe(
        filtered[
            [
                "NAMA",
                "Usia",
                "Asal Instansi",
                "Total_LD",
                "Mean_LD",
                "Level_LD"
            ]
        ],
        use_container_width=True,
        height=350
    )
