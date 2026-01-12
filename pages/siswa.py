import streamlit as st
import pandas as pd
import plotly.express as px

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="Dashboard Siswa - Hasil CT Bebras Challenge",
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

df_siswa = load_data()

# ======================================================
# FILTER – SISWA
# ======================================================
f1, f2, f3 = st.columns(3)

with f1:
    provinsi = st.multiselect(
        "Filter Provinsi",
        sorted(df_siswa["Provinsi"].dropna().unique()),
        placeholder="Choose option"
    )

df_filter = df_siswa.copy()
if provinsi:
    df_filter = df_filter[df_filter["Provinsi"].isin(provinsi)]

with f2:
    sekolah_siswa = st.multiselect(
        "Filter Sekolah",
        sorted(df_filter["SekolahNama"].dropna().unique()),
        placeholder="Choose option"
    )

with f3:
    kategori = st.multiselect(
        "Filter Kategori",
        sorted(df_siswa["Kategori"].dropna().unique()),
        placeholder="Choose option"
    )

# ======================================================
# APPLY FILTER – SISWA
# ======================================================
filtered_siswa = df_siswa.copy()

if sekolah_siswa:
    filtered_siswa = filtered_siswa[
        filtered_siswa["SekolahNama"].isin(sekolah_siswa)
    ]

if provinsi:
    filtered_siswa = filtered_siswa[
        filtered_siswa["Provinsi"].isin(provinsi)
    ]

if kategori:
    filtered_siswa = filtered_siswa[
        filtered_siswa["Kategori"].isin(kategori)
    ]

# ======================================================
# INFO FILTER – SISWA
# ======================================================
active_filters = []

if sekolah_siswa:
    active_filters.append(f"Sekolah: {len(sekolah_siswa)}")
if provinsi:
    active_filters.append("Provinsi: " + ", ".join(provinsi))
if kategori:
    active_filters.append("Kategori: " + ", ".join(kategori))

if active_filters:
    st.info("Filter aktif → " + " | ".join(active_filters))
else:
    st.info("Menampilkan seluruh data siswa.")

# ======================================================
# KPI RINGKAS
# ======================================================
persen_ct_tinggi = (
    (filtered_siswa["Level_CT"] == "Tinggi").mean() * 100
)
jumlah_sekolah = filtered_siswa["SekolahNama"].nunique()

k1, k2, k3, k4 = st.columns(4)

k1.metric("Jumlah Siswa", len(filtered_siswa))
k2.metric("Jumlah Sekolah", jumlah_sekolah)
k3.metric("Rata-rata CT Norm", round(filtered_siswa["CT_norm"].mean(), 3))
k4.metric("CT Tertinggi", f"{persen_ct_tinggi:.1f}%")

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
# LEFT : DISTRIBUSI LEVEL CT
# ======================================================
with left:
    df_level = (
        filtered_siswa
        .groupby("Level_CT", as_index=False)
        .size()
        .rename(columns={"size": "Jumlah"})
    )

    fig_pie = px.pie(
        df_level,
        values="Jumlah",
        names="Level_CT",
        title="Distribusi Tingkat Computational Thinking Siswa",
        color="Level_CT",
        color_discrete_map=warna_level
    )

    fig_pie.update_layout(height=380)
    st.plotly_chart(fig_pie, use_container_width=True)

# ======================================================
# RIGHT : VARIASI SKOR CT (BOXPLOT)
# ======================================================
with right:
    fig_box = px.box(
        filtered_siswa,
        x="Level_CT",
        y="CT_norm",
        color="Level_CT",
        color_discrete_map=warna_level,
        title="Variasi Skor Computational Thinking Siswa berdasarkan Level",
        labels={
            "Level_CT": "Level Computational Thinking",
            "CT_norm": "Skor CT (Normalisasi)"
        }
    )

    fig_box.update_layout(height=380, showlegend=False)
    st.plotly_chart(fig_box, use_container_width=True)

# ======================================================
# PERBANDINGAN SEKOLAH
# ======================================================
st.markdown("### Rata-rata CT per Sekolah")

top_n = st.slider("Top Sekolah", 5, 15, 8)

df_school = (
    filtered_siswa
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
st.markdown("### 📋 Tabel Detail Data Siswa")

st.dataframe(
    filtered_siswa[
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
