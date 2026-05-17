# utils/styles.py
import streamlit as st


def get_theme():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;700&family=Inter:wght@300;400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
        background-color: #0D1117 !important;
        color: #F9FAFB !important;
    }

    #MainMenu, footer, header { visibility: hidden; }

    .block-container {
        padding-top: 1rem !important;
        max-width: 1100px !important;
    }

    /* ── FORCE SIDEBAR VISIBLE ── */
    [data-testid="stSidebar"] {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        width: 240px !important;
        min-width: 240px !important;
        transform: none !important;
        background-color: #161B22 !important;
        border-right: 1px solid #30363D !important;
    }
    [data-testid="stSidebar"] > div {
        display: block !important;
        visibility: visible !important;
    }
    [data-testid="stSidebar"] * {
        color: #F9FAFB !important;
    }

    /* Sidebar buttons */
    [data-testid="stSidebar"] .stButton > button {
        background-color: transparent !important;
        color: #F9FAFB !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        text-align: left !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #DC2626 !important;
        color: #ffffff !important;
    }

    /* Main area buttons */
    section[data-testid="stMain"] .stButton > button {
        background-color: #DC2626 !important;
        color: #fff !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
    }
    section[data-testid="stMain"] .stButton > button:hover {
        background-color: #B91C1C !important;
    }

    [data-testid="metric-container"] {
        background-color: #1F2937 !important;
        border: 1px solid #30363D !important;
        border-radius: 10px !important;
        padding: 1rem !important;
    }

    hr { border-color: #30363D !important; }
    </style>
    """, unsafe_allow_html=True)


def navbar(active_page: str):
    """Top navbar using st.columns and st.button."""
    st.markdown("""
    <style>
    div[data-testid="column"] .stButton > button {
        background: transparent !important;
        color: #9CA3AF !important;
        border: none !important;
        border-radius: 8px !important;
        font-size: 0.88rem !important;
        font-weight: 500 !important;
        width: 100% !important;
    }
    div[data-testid="column"] .stButton > button:hover {
        background: #1F2937 !important;
        color: #F9FAFB !important;
    }
    </style>
    """, unsafe_allow_html=True)

    col_logo, col_home, col_reg, col_login, col_about = st.columns(
        [2.5, 0.8, 1.2, 0.8, 0.8]
    )

    with col_logo:
        st.markdown("### ⚡ UCARS")

    with col_home:
        label = "**Home**" if active_page == "home" else "Home"
        if st.button(label, key=f"{active_page}_nav_home"):
            st.session_state.current_page = "home"
            st.rerun()

    with col_reg:
        label = "**Create Account**" if active_page == "register" else "Create Account"
        if st.button(label, key=f"{active_page}_nav_register"):
            st.session_state.current_page = "register"
            st.rerun()

    with col_login:
        label = "**Login**" if active_page == "login" else "Login"
        if st.button(label, key=f"{active_page}_nav_login"):
            st.session_state.current_page = "login"
            st.rerun()

    with col_about:
        label = "**About**" if active_page == "about" else "About"
        if st.button(label, key=f"{active_page}_nav_about"):
            st.session_state.current_page = "about"
            st.rerun()

    st.divider()


def footer():
    """Simple footer."""
    st.divider()
    st.markdown(
        "<p style='text-align:center; color:#9CA3AF; font-size:0.8rem;'>"
        "© 2025 Urban Crime Analysis & Reporting System — All rights reserved."
        "</p>",
        unsafe_allow_html=True
    )