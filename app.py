import streamlit as st

st.set_page_config(
    page_title="Dashboard Analisis Literasi Digital & CT",
    layout="wide"
)

pg = st.navigation([
    st.Page("pages/dashboard.py", title="Dashboard Utama", icon="📊"),
    st.Page("pages/guru.py", title="Data Guru", icon="👩‍🏫"),
    st.Page("pages/siswa.py", title="Data Siswa", icon="👨‍🎓"),
])

pg.run()
