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
        st.markdown("""
            <style>
                /* Target link_button anchor */
                [data-testid="stLinkButton"] a {
                    display: block;
                    text-align: center;
                    padding: 0.6rem;
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

        st.link_button("🔵 Continue with Google", google_url)

        st.write(" ")

        if st.button("Already have an account? Log In", use_container_width=True, key="goto_login"):
            st.session_state.current_page = "login"
            st.rerun()

        st.caption("Your info is used only for crime reporting and never shared.")

    footer()