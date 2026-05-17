# views/login.py
import streamlit as st
from utils.styles import get_theme, navbar, footer
from utils.api import get_google_login_url


def show():
    get_theme()

    # ── Handle Google OAuth callback ──
    token = st.query_params.get("access_token")
    name  = st.query_params.get("name")
    email = st.query_params.get("email")
    role  = st.query_params.get("role")

    if token and not st.session_state.get("logged_in"):
        # Store in session
        st.session_state.logged_in    = True
        st.session_state.auth_token   = token
        st.session_state.user_name    = name
        st.session_state.user_email   = email
        st.session_state.user_role    = role
        st.session_state.current_page = (
            "admin_dashboard" if role == "admin" else "user_dashboard"
        )
        # Keep token in URL — so page refresh restores session
        st.query_params["access_token"] = token
        st.query_params["name"]         = name
        st.query_params["email"]        = email
        st.query_params["role"]         = role
        st.rerun()
        return

    navbar("login")

    _, col, _ = st.columns([1, 1.2, 1])

    with col:
        st.divider()
        st.error("🔐 Secure Login")
        st.title("Welcome Back")
        st.caption("Sign in using your Google account. Your data is encrypted and protected.")
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

        if st.button("Create Account Instead", use_container_width=True, key="goto_register"):
            st.session_state.current_page = "register"
            st.rerun()

        st.caption("By continuing you agree to our Terms of Service and Privacy Policy.")

    footer()