import streamlit as st

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="Dashboard Analisis Literasi Digital & CT",
    layout="wide",
    initial_sidebar_state="expanded"
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
# NAVIGATION (PAGES)
# ======================================================
pg = st.navigation([
    st.Page(
        "pages/dashboard.py",
        title="Dashboard",
        icon="📊"
    ),
    st.Page(
        "pages/guru.py",
        title="Data Guru",
        icon="👩‍🏫"
    ),
    st.Page(
        "pages/siswa.py",
        title="Data Siswa",
        icon="👨‍🎓"
    ),
])

pg.run()
