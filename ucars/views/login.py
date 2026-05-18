# views/login.py
import streamlit as st
from utils.styles import get_theme, navbar, footer
from utils.api import get_google_login_url

import streamlit.components.v1 as components
from urllib.parse import urlencode


def show_google_login_button():
    client_id   = st.secrets["GOOGLE_CLIENT_ID"]
    redirect_uri = st.secrets["GOOGLE_REDIRECT_URI"]  # your Vercel callback URL
    
    params = {
        "client_id":     client_id,
        "redirect_uri":  redirect_uri,
        "response_type": "code",
        "scope":         "openid email profile",
        "access_type":   "offline",
        "prompt":        "consent",
    }
    return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"

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

        google_url = show_google_login_button()
        st.markdown("""
            <style>
                /* Target link_button anchor */
                [data-testid="stLinkButton"] a {
                    display: block;
                    text-align: center;
                    padding: 1rem;
                    background: #DC2626 !important;
                    color: white !important;
                    border-radius: 8px !important;
                    text-decoration: none;
                    font-weight: 700;
                    border: none;
                }
                [data-testid="stLinkButton"] a:hover {
                    background: #B91C1C !important;
                    color: white !important;
                }
            </style>
        """, unsafe_allow_html=True)

        st.link_button("🔵 Continue with Google", google_url,use_container_width=True)

        st.write(" ")

        if st.button("Create Account Instead", use_container_width=True, key="goto_register"):
            st.session_state.current_page = "register"
            st.rerun()

        st.caption("By continuing you agree to our Terms of Service and Privacy Policy.")

    footer()