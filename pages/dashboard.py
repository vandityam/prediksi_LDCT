import streamlit as st
import pandas as pd
import plotly.express as px
from scipy.stats import spearmanr, pearsonr

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="Dashboard Utama Analisis",
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
    <div style='text-align:center;'>
        <h2>Dashboard Analisis</h2>
        <p>
        Hubungan Literasi Digital Guru dan Computational Thinking Siswa<br>
        <b>Studi Kasus Sekolah Yayasan PPKS Solo</b>
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()

# ======================================================
# LOAD DATA
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
# SCHOOL KEY
# ======================================================
def key_school(name):
    return " ".join(str(name).lower().strip().split()[:4])

df_guru["sekolah_key"] = df_guru["SekolahNama"].apply(key_school)
df_siswa["sekolah_key"] = df_siswa["SekolahNama"].apply(key_school)

sekolah_sama = sorted(
    set(df_guru["sekolah_key"]) & set(df_siswa["sekolah_key"])
)

# ======================================================
# AGREGASI SEKOLAH
# ======================================================
df_korelasi = pd.merge(
    df_guru[df_guru["sekolah_key"].isin(sekolah_sama)]
        .groupby("sekolah_key", as_index=False)
        .agg(LD_Guru_Mean=("Mean_LD", "mean")),
    df_siswa[df_siswa["sekolah_key"].isin(sekolah_sama)]
        .groupby("sekolah_key", as_index=False)
        .agg(CT_Siswa_Norm=("CT_norm", "mean")),
    on="sekolah_key"
).round(3)

# ======================================================
# MAIN LAYOUT
# ======================================================
left, right = st.columns([2, 1])

# ================= LEFT — KORELASI ====================
with left:
    st.markdown("### Analisis Korelasi")

    tab1, tab2, tab3 = st.tabs([
        "Antar Sekolah",
        "Antar Sekolah per Level",
        "Pola Level Dalam Sekolah"
    ])

    # ---------- TAB 1 ----------
    with tab1:
        st.markdown("""
        Analisis hubungan antara **literasi digital guru** 
        dan **kemampuan computational thinking siswa** pada tingkat sekolah.
        """)

        r1, p1 = spearmanr(
            df_korelasi["LD_Guru_Mean"],
            df_korelasi["CT_Siswa_Norm"]
        )

        fig1 = px.scatter(
            df_korelasi,
            x="LD_Guru_Mean",
            y="CT_Siswa_Norm",
            trendline="ols",
            hover_data={
                "sekolah_key": True,
                "LD_Guru_Mean": ":.3f",
                "CT_Siswa_Norm": ":.3f"
            },
            labels={
                "LD_Guru_Mean": "Rata-rata LD Guru",
                "CT_Siswa_Norm": "Rata-rata CT Siswa",
                "sekolah_key": "Nama Sekolah"
            }
        )

        fig1.update_layout(height=350)
        st.plotly_chart(fig1, use_container_width=True)

        k1, k2 = st.columns(2)

        k1.metric("Spearman r", round(r1, 3))
        k2.metric("p-value", round(p1, 3))

        if p1 < 0.05:
            st.info(
                f"Terdapat **hubungan positif yang signifikan** antara LD guru "
                f"dan kemampuan CT siswa pada tingkat sekolah. "
                "Hal ini menunjukkan bahwa sekolah dengan LD guru lebih tinggi cenderung "
                "memiliki rata-rata CT siswa yang lebih baik."
            )
        else:
            st.info(
                f"Terdapat **hubungan positif belum signifikan** antara LD guru "
                f"dan kemampuan CT siswa pada tingkat sekolah. "
                "Karena keterbatasan jumlah sampel dan variabel prediktor"
            )

    # ---------- TAB 2 ----------
    with tab2:
        st.markdown("""
        Analisis hubungan antara **literasi digital guru** dan **kemampuan computational thinking siswa**
        pada **level tertentu**. Perbandingan dilakukan antar sekolah, namun hanya pada level yang sama.
        """)

        level_pilih = st.selectbox(
            "Pilih Level Literasi Digital Guru",
            sorted(df_guru["Level_LD"].dropna().unique())
        )

        guru_lvl = df_guru[df_guru["Level_LD"] == level_pilih]
        siswa_lvl = df_siswa[df_siswa["Level_CT"] == level_pilih]

        df_lvl = pd.merge(
            guru_lvl.groupby("sekolah_key")["Mean_LD"].mean().reset_index(),
            siswa_lvl.groupby("sekolah_key")["CT_norm"].mean().reset_index(),
            on="sekolah_key"
        )

        if len(df_lvl) >= 3:
            r2, p2 = spearmanr(df_lvl["Mean_LD"], df_lvl["CT_norm"])
            st.dataframe(df_lvl.round(3), use_container_width=True)
            k1, k2 = st.columns(2)
            k1.metric("Spearman r", round(r2, 3))
            k2.metric("p-value", round(p2, 3))
        else:
            st.warning("Jumlah sekolah belum mencukupi untuk analisis.")

        if len(df_lvl) >= 3:
            if p2 < 0.05:
                st.info(
                    f"Pada level **{level_pilih}**, terdapat **hubungan signifikan** antara "
                    f"literasi digital guru dan kemampuan CT siswa (r = {round(r2,3)}, p < 0,05). "
                    "Artinya, pada level ini, peningkatan LD guru cenderung diikuti oleh "
                    "peningkatan CT siswa."
                )
            else:
                st.info(
                    f"Pada level **{level_pilih}**, hubungan antara literasi digital guru dan "
                    f"kemampuan CT siswa bersifat **positif namun belum signifikan** "
                    f"(r = {round(r2,3)}, p = {round(p2,3)})."
                )

    # ---------- TAB 3 ----------
    with tab3:
        st.markdown("""
        Analisis hubungan antara **level literasi digital guru**
        dan **level kemampuan computational thinking siswa** antar sekolah.
        Hasil korelasi ditampilkan per sekolah.
        """)

        # ---------- fungsi interpretasi ----------
        def interpretasi_korelasi(r, p):
            ar = abs(r)
            if ar < 0.20:
                kekuatan = "sangat lemah"
            elif ar < 0.40:
                kekuatan = "lemah"
            elif ar < 0.60:
                kekuatan = "sedang"
            elif ar < 0.80:
                kekuatan = "kuat"
            else:
                kekuatan = "sangat kuat"

            signifikan = "signifikan" if p < 0.05 else "tidak signifikan"
            return f"{kekuatan} dan {signifikan}"

        hasil = []

        for sekolah in sekolah_sama:
            g = df_guru[df_guru["sekolah_key"] == sekolah]
            s = df_siswa[df_siswa["sekolah_key"] == sekolah]

            g_lvl = g.groupby("Level_LD")["Mean_LD"].mean()
            s_lvl = s.groupby("Level_CT")["CT_norm"].mean()

            df_pola = pd.merge(
                g_lvl.reset_index(),
                s_lvl.reset_index(),
                left_on="Level_LD",
                right_on="Level_CT"
            )

            if len(df_pola) >= 3:
                r3, p3 = pearsonr(df_pola["Mean_LD"], df_pola["CT_norm"])
                hasil.append({
                    "Sekolah": sekolah,
                    "r": round(r3, 3),
                    "p-value": round(p3, 3),
                    "Interpretasi": interpretasi_korelasi(r3, p3)
                })

        df_hasil = pd.DataFrame(hasil)
        st.dataframe(df_hasil, use_container_width=True)

        st.info(
            "Hasil korelasi menunjukkan pola hubungan antara level LD guru dan kemampuan CT siswa **berbeda-beda pada setiap sekolah**. "
        )
# ================= RIGHT — PREDIKSI ===================
with right:
    st.markdown("### Prediksi CT Siswa")

    st.caption(
        "Simulasi prediksi kemampuan CT siswa "
        "berdasarkan rata-rata LD guru menggunakan model regresi linear."
    )

    # Parameter model
    INTERCEPT = -1.4366
    SLOPE = 0.5150

    # Input LD
    ld_input = st.slider(
        "Rata-rata Literasi Digital Guru",
        min_value=float(df_korelasi["LD_Guru_Mean"].min()),
        max_value=float(df_korelasi["LD_Guru_Mean"].max()),
        value=float(df_korelasi["LD_Guru_Mean"].mean()),
        step=0.01
    )

    # Prediksi CT
    ct_pred = round(INTERCEPT + SLOPE * ld_input, 3)
    st.metric("Hasil Prediksi CT Siswa", ct_pred)

    # Visualisasi prediksi
    fig_pred = px.scatter(
        df_korelasi,
        x="LD_Guru_Mean",
        y="CT_Siswa_Norm",
        trendline="ols",
        hover_data=["sekolah_key"],
        labels={
            "LD_Guru_Mean": "Rata-rata LD Guru",
            "CT_Siswa_Norm": "Rata-rata CT Siswa",
            "sekolah_key": "Nama Sekolah"
        }
    )

    fig_pred.add_scatter(
        x=[ld_input],
        y=[ct_pred],
        mode="markers",
        marker=dict(size=14, symbol="star"),
        name="Titik Prediksi"
    )

    fig_pred.update_layout(height=320)
    st.plotly_chart(fig_pred, use_container_width=True)

    # Interpretasi prediksi
    rata_ct = df_korelasi["CT_Siswa_Norm"].mean()

    if ct_pred > rata_ct:
        st.success(
            "📈 **CT siswa diprediksi di atas rata-rata sekolah**. "
            "Ada potensi peningkatan kemampuan CT siswa seiring naiknya LD guru."
        )
    else:
        st.warning(
            "📉 **CT siswa diprediksi di bawah rata-rata sekolah**. "
            "Perlu peningkatan LD guru untuk mendorong kemampuan CT siswa."
        )

    # Model & evaluasi
    st.markdown("""
    **Model Regresi Linear:**  
    CT = **-1.4366 + 0.5150 × LD**

    Artinya, setiap kenaikan **1 poin LD guru** diperkirakan
    meningkatkan **0,515 poin kemampuan CT siswa**.
    """)

    st.success("""
    **Dengan Evaluasi Model:**
    - R² = 0,653 (Adj. R² = 0,537)  
    - RMSE = 0,053  
    - MAE = 0,045  

    Model mampu menjelaskan **53–65% variasi kemampuan CT siswa**, 
    dengan tingkat kesalahan prediksi yang relatif kecil.
    """)
