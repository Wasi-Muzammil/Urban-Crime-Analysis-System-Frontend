# views/register.py
import streamlit as st
from utils.styles import get_theme, navbar, footer
from utils.api import get_google_login_url


def show():
    get_theme()
    navbar("register")

    _, col, _ = st.columns([1, 1.2, 1])

    with col:
        st.divider()
        st.success("✨ New Account")
        st.title("Join UCARS")
        st.caption("Create your account in seconds using Google. No password required.")
        st.divider()

        google_url = get_google_login_url()
        st.markdown(
            f'<a href="{google_url}" target="_self" style="'
            f'display:block; text-align:center; padding:0.6rem; '
            f'background:#DC2626; color:white; border-radius:8px; '
            f'text-decoration:none; font-weight:700;">'
            f'🔵 Continue with Google</a>',
            unsafe_allow_html=True
        )

        st.write(" ")

        if st.button("Already have an account? Log In", use_container_width=True, key="goto_login"):
            st.session_state.current_page = "login"
            st.rerun()

        st.caption("Your info is used only for crime reporting and never shared.")

    footer()