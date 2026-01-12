import streamlit as st
import pandas as pd
import plotly.express as px

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="Dashboard Guru - Literasi Digital Yayasan PPKS",
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
    <div style='text-align:center; margin-top:5px; margin-bottom:10px;'>
        <h2>Dashboard Data Guru</h2>
        <p>
            Ringkasan <b>Literasi Digital Guru</b> berdasarkan penilaian Yayasan PPKS   
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

df_guru = load_data()

# ======================================================
# FILTER – GURU
# ======================================================
f1, f2 = st.columns(2)

with f1:
    sekolah_guru = st.multiselect(
        "Filter Sekolah",
        sorted(df_guru["Asal Instansi"].dropna().unique()),
        placeholder="Choose option"
    )

with f2:
    level_ld = st.multiselect(
        "Filter Level Literasi Digital",
        ["Rendah", "Sedang", "Tinggi"],
        placeholder="Choose option"
    )

# ======================================================
# APPLY FILTER – GURU
# ======================================================
filtered_guru = df_guru.copy()

if sekolah_guru:
    filtered_guru = filtered_guru[
        filtered_guru["Asal Instansi"].isin(sekolah_guru)
    ]

if level_ld:
    filtered_guru = filtered_guru[
        filtered_guru["Level_LD"].isin(level_ld)
    ]

# ======================================================
# INFO FILTER – GURU
# ======================================================
active_filters = []

if sekolah_guru:
    active_filters.append(f"Sekolah: {len(sekolah_guru)}")

if level_ld:
    active_filters.append("Level LD: " + ", ".join(level_ld))

if active_filters:
    st.info("Filter aktif → " + " | ".join(active_filters))
else:
    st.info("Menampilkan seluruh data guru.")

# ======================================================
# KPI RINGKAS
# ======================================================
persen_ld_tinggi = (
    (filtered_guru["Level_LD"] == "Tinggi").mean() * 100
)
jumlah_instansi = filtered_guru["Asal Instansi"].nunique()

k1, k2, k3, k4 = st.columns(4)

k1.metric("Jumlah Guru", len(filtered_guru))
k2.metric("Jumlah Sekolah", jumlah_instansi)
k3.metric("Rata-rata LD Guru", round(filtered_guru["Mean_LD"].mean(), 2))
k4.metric("LD Tertinggi", f"{persen_ld_tinggi:.1f}%")

st.markdown("---")

# ======================================================
# MAIN VISUAL (KIRI - KANAN)
# ======================================================
left, right = st.columns([1, 2])

warna_level = {
    "Rendah": "#E74C3C",
    "Sedang": "#F1C40F",
    "Tinggi": "#2ECC71"
}

# ======================================================
# LEFT : DISTRIBUSI LEVEL LITERASI DIGITAL
# ======================================================
with left:
    df_level = (
        filtered_guru
        .groupby("Level_LD", as_index=False)
        .size()
        .rename(columns={"size": "Jumlah"})
    )

    fig_pie = px.pie(
        df_level,
        values="Jumlah",
        names="Level_LD",
        title="Distribusi Tingkat Literasi Digital Guru",
        color="Level_LD",
        color_discrete_map=warna_level
    )

    fig_pie.update_layout(height=380)
    st.plotly_chart(fig_pie, use_container_width=True)

# ======================================================
# RIGHT : VARIASI SKOR LD (BOXPLOT)
# ======================================================
with right:
    fig_box = px.box(
        filtered_guru,
        x="Level_LD",
        y="Mean_LD",
        color="Level_LD",
        color_discrete_map=warna_level,
        title="Variasi Skor Literasi Digital Guru berdasarkan Level",
        labels={
            "Level_LD": "Level Literasi Digital",
            "Mean_LD": "Skor Literasi Digital"
        }
    )

    fig_box.update_layout(height=380, showlegend=False)
    st.plotly_chart(fig_box, use_container_width=True)

# ======================================================
# PERBANDINGAN INSTANSI
# ======================================================
st.markdown("### Rata-rata Literasi Digital per Sekolah")

top_n = st.slider("Top Instansi", 5, 15, 8)

df_instansi = (
    filtered_guru
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

fig_bar.update_layout(height=350)
st.plotly_chart(fig_bar, use_container_width=True)

# ======================================================
# TABEL DETAIL DATA GURU
# ======================================================
st.markdown("### 📋 Tabel Detail Data Guru")

st.dataframe(
    filtered_guru[
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
