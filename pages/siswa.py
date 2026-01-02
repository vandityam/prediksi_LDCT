import streamlit as st
import pandas as pd
import plotly.express as px

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="Data Siswa - Bebras Challenge",
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
st.markdown("<div class='main-title'>👨‍🎓 Data Siswa</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='subtitle'>Analisis Computational Thinking (CT) siswa "
    "berdasarkan hasil Bebras Challenge</div>",
    unsafe_allow_html=True
)

# ======================================================
# LOAD DATA (FULL KOLOM)
# ======================================================
@st.cache_data
def load_data():
    return pd.read_csv(
        "files/dashboard_datasiswa.csv",
        sep=";",
        encoding="utf-8"
    )

df = load_data()

# =============================================================================
# MAPPING (UNTUK FILTER CASCADING)
# =============================================================================
mapping_kategori_kelas = (
    df[["Kategori", "Kelas"]]
    .drop_duplicates()
    .groupby("Kategori")["Kelas"]
    .apply(list)
    .to_dict()
)

mapping_prov_kota = (
    df[["Provinsi", "SekolahKotaKabupaten"]]
    .drop_duplicates()
    .groupby("Provinsi")["SekolahKotaKabupaten"]
    .apply(list)
    .to_dict()
)

# =============================================================================
# SIDEBAR FILTER
# =============================================================================
st.sidebar.markdown("<div class='sidebar-title'>🔍 Filter Data</div>", unsafe_allow_html=True)

provinsi = st.sidebar.multiselect("Pilih Provinsi:", sorted(df["Provinsi"].dropna().unique()))
if provinsi:
    kota_allowed = sorted({k for p in provinsi for k in mapping_prov_kota.get(p, [])})
else:
    kota_allowed = sorted(df["SekolahKotaKabupaten"].dropna().unique())

kota = st.sidebar.multiselect("Pilih Kota/Kabupaten:", kota_allowed)

kategori = st.sidebar.multiselect("Pilih Kategori:", sorted(df["Kategori"].dropna().unique()))
if kategori:
    kelas_allowed = sorted({k for cat in kategori for k in mapping_kategori_kelas.get(cat, [])})
else:
    kelas_allowed = sorted(df["Kelas"].dropna().unique())

kelas = st.sidebar.multiselect("Pilih Kelas:", kelas_allowed)

# Filter data
filtered = df.copy()
if provinsi: filtered = filtered[filtered["Provinsi"].isin(provinsi)]
if kota: filtered = filtered[filtered["SekolahKotaKabupaten"].isin(kota)]
if kategori: filtered = filtered[filtered["Kategori"].isin(kategori)]
if kelas: filtered = filtered[filtered["Kelas"].isin(kelas)]

st.sidebar.markdown(f"<p class='small-info'>Total data: <b>{len(filtered)} peserta</b></p>", unsafe_allow_html=True)

# =============================================================================
# INFORMASI FILTER AKTIF
# =============================================================================
active_filters = []
if provinsi: active_filters.append("Provinsi: " + ", ".join(provinsi))
if kota: active_filters.append("Kota: " + ", ".join(kota))
if kategori: active_filters.append("Kategori: " + ", ".join(kategori))
if kelas: active_filters.append("Kelas: " + ", ".join(kelas))

if active_filters:
    st.info("Filter aktif: " + " | ".join(active_filters))
else:
    st.info("Menampilkan seluruh data.")

# ======================================================
# KPI
# ======================================================
st.markdown("<div class='section-title'>📌 Statistik Ringkas</div>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
c1.metric("Jumlah Siswa", len(filtered))
c2.metric("Rata-rata Nilai", round(filtered["Nilai"].mean(), 2))
c3.metric("Rata-rata CT_norm", round(filtered["CT_norm"].mean(), 3))

# ======================================================
# DISTRIBUSI LEVEL CT
# ======================================================
st.markdown("<div class='section-title'>Distribusi Level CT</div>", unsafe_allow_html=True)

fig_level = px.pie(
    filtered["Level_CT"].value_counts().reset_index(),
    names="Level_CT",
    values="count",
    title="Distribusi Level Computational Thinking"
)
st.plotly_chart(fig_level, use_container_width=True)

# ======================================================
# NILAI vs CT
# ======================================================
st.markdown("<div class='section-title'>Nilai vs CT_norm</div>", unsafe_allow_html=True)

fig_scatter = px.scatter(
    filtered,
    x="CT_norm",
    y="Nilai",
    color="Level_CT",
    hover_data=["Nama", "SekolahNama", "Kelas"],
    title="Hubungan Nilai dan CT_norm"
)
st.plotly_chart(fig_scatter, use_container_width=True)

# =============================================================================
# PERBANDINGAN PER INSTANSI (TOP N)
# =============================================================================
st.markdown("<div class='section-title'>Rata-rata CT per Sekolah</div>", unsafe_allow_html=True)

top_n = st.slider("Tampilkan Top-N Instansi", 5, 20, 10)

df_instansi = (
    filtered
    .groupby("SekolahNama", as_index=False)["CT_norm"]
    .mean()
    .sort_values("CT_norm", ascending=False)
)

fig_instansi = px.bar(
    df_instansi.head(top_n),
    x="CT_norm",
    y="SekolahNama",
    orientation="h",
    title=f"Top {top_n} Instansi Berdasarkan Mean CT"
)

fig_instansi.update_layout(height=350)
st.plotly_chart(fig_instansi, use_container_width=True)

# ======================================================
# TABEL 
# ======================================================
st.markdown("<div class='section-title'>Data Detail Siswa</div>", unsafe_allow_html=True)

tabel_cols = [
    "Nama",
    "SekolahNama",
    "SekolahKotaKabupaten",
    "Provinsi",
    "Kelas",
    "Kategori",
    "Nilai",
    "CT_norm",
    "Level_CT"
]

st.dataframe(
    filtered[tabel_cols],
    use_container_width=True,
    height=420
)
