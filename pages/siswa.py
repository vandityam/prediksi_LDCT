import streamlit as st
import pandas as pd
import plotly.express as px

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="Dashboard Siswa - Bebras Challenge",
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
        <h2>Dashboard Data Siswa</h2>
        <p>
        Ringkasan <b>Computational Thinking Siswa</b> berdasarkan hasil Bebras Challenge
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
    return pd.read_csv(
        "files/dashboard_datasiswa.csv",
        encoding="utf-8"
    )

df = load_data()

# ======================================================
# SIDEBAR FILTER
# ======================================================
st.sidebar.markdown("### 🔍 Filter Data")

provinsi = st.sidebar.multiselect(
    "Provinsi",
    sorted(df["Provinsi"].dropna().unique())
)

kategori = st.sidebar.multiselect(
    "Kategori",
    sorted(df["Kategori"].dropna().unique())
)

filtered = df.copy()
if provinsi:
    filtered = filtered[filtered["Provinsi"].isin(provinsi)]
if kategori:
    filtered = filtered[filtered["Kategori"].isin(kategori)]

st.sidebar.markdown(
    f"<small>Total data: <b>{len(filtered)} siswa</b></small>",
    unsafe_allow_html=True
)

# ======================================================
# INFO FILTER
# ======================================================
active_filters = []
if provinsi: active_filters.append("Provinsi: " + ", ".join(provinsi))
if kategori: active_filters.append("Kategori: " + ", ".join(kategori))

if active_filters:
    st.info("Filter aktif → " + " | ".join(active_filters))
else:
    st.info("Menampilkan seluruh data siswa.")

# ======================================================
# KPI RINGKAS (UPGRADE)
# ======================================================
persen_ct_tinggi = (filtered["Level_CT"] == "Tinggi").mean() * 100
jumlah_instansi = filtered["SekolahNama"].nunique()

k1, k2, k3, k4 = st.columns(4)

k1.metric("JUMLAH SISWA", len(filtered))
# k2.metric("RATA-RATA NILAI", round(filtered["Nilai"].mean(), 2))
k2.metric("JUMLAH SEKOLAH", jumlah_instansi)
k3.metric("RATA-RATA CT NORM", round(filtered["CT_norm"].mean(), 3))
k4.metric("CT TERTINGGI", f"{persen_ct_tinggi:.1f}%")

st.markdown("---")

# ======================================================
# MAIN VISUAL (KIRI - KANAN)
# ======================================================
left, right = st.columns([2, 1])

# ------------------------------------------------------
# LEFT : SCATTER CT vs NILAI
# ------------------------------------------------------
with left:
    fig_scatter = px.scatter(
        filtered,
        x="CT_norm",
        y="Nilai",
        color="Level_CT",
        hover_data=["Nama", "SekolahNama", "Kelas"],
        title="Hubungan Nilai dan Computational Thinking",
        labels={
            "CT_norm": "CT Normalisasi",
            "Nilai": "Nilai Bebras"
        }
    )
    fig_scatter.update_layout(height=380)
    st.plotly_chart(fig_scatter, use_container_width=True)

# ------------------------------------------------------
# RIGHT : DISTRIBUSI LEVEL CT (BAR)
# ------------------------------------------------------
with right:
    df_level = (
        filtered
        .groupby("Level_CT", as_index=False)
        .size()
        .rename(columns={"size": "Jumlah"})
    )

    fig_level = px.pie(
        df_level,
        values="Jumlah",
        names="Level_CT",
        title="Distribusi Level CT"
    )

    fig_level.update_layout(height=380)
    st.plotly_chart(fig_level, use_container_width=True)


# ======================================================
# PERBANDINGAN SEKOLAH
# ======================================================
st.markdown("### Rata-rata CT per Sekolah")

top_n = st.slider("Top Sekolah", 5, 15, 8)

df_school = (
    filtered
    .groupby("SekolahNama", as_index=False)["CT_norm"]
    .mean()
    .sort_values("CT_norm", ascending=False)
)

fig_bar = px.bar(
    df_school.head(top_n),
    x="CT_norm",
    y="SekolahNama",
    orientation="h",
    labels={
        "CT_norm": "Rata-rata CT",
        "SekolahNama": "Sekolah"
    }
)

fig_bar.update_layout(height=320)
st.plotly_chart(fig_bar, use_container_width=True)

# ======================================================
# TABEL DETAIL (OPTIONAL)
# ======================================================
with st.expander("📋 Lihat Data Detail Siswa"):
    st.dataframe(
        filtered[
            [
                "Nama",
                "SekolahNama",
                "Provinsi",
                "Kategori",
                "Nilai",
                "CT_norm",
                "Level_CT"
            ]
        ],
        use_container_width=True,
        height=350
    )
