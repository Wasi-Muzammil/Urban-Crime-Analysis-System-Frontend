import streamlit as st
from utils.styles import get_theme, navbar, footer

def show():
    get_theme()
    navbar("home")

    # --- LOGIC FIX: Check Session State ---
    # Show logged-in banner if user navigates back to landing
    if st.session_state.get("authenticated") or st.session_state.get("logged_in"):
        name = st.session_state.get("user_name") or "there"
        role = st.session_state.get("user_role", "viewer")
        dashboard_page = "admin_dashboard" if role == "admin" else "user_dashboard"

        st.markdown(
            f"""
            <div style="
                background: linear-gradient(90deg, #161B22, #0D1117);
                border: 1px solid #DC2626;
                border-radius: 12px;
                padding: 1rem 1.4rem;
                margin-bottom: 1.5rem;
            ">
                <span style="color:#F9FAFB; font-weight:600; font-size:1rem;">
                    🛡️ &nbsp; Welcome back, <strong>{name}</strong>. You are currently securely logged in.
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_dash, col_logout, _ = st.columns([1.5, 1.2, 4])
        with col_dash:
            if st.button("🏠 Go to Dashboard", use_container_width=True, key="landing_go_dashboard"):
                st.session_state.current_page = dashboard_page
                st.rerun()
        with col_logout:
            if st.button("🚪 Logout", use_container_width=True, key="landing_logout"):
                # Clean up all possible auth keys
                st.session_state.authenticated = False
                st.session_state.logged_in = False
                from utils.auth import logout_user
                logout_user()
                st.rerun()

        st.markdown("<br/>", unsafe_allow_html=True)

    # Hero Section
    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center; color: #F9FAFB;'>🛡️ Urban Crime Analysis & Reporting System</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center; color:#9CA3AF; font-style: italic;'>\"Empowering Communities. Exposing Patterns. Delivering Justice.\"</h3>", unsafe_allow_html=True)

    st.divider()

    col_reviews, col_cta = st.columns([1.1, 0.9], gap="large")

    with col_reviews:
        st.subheader("💬 What People Say")

        with st.container(border=True):
            st.write("⭐⭐⭐⭐⭐")
            st.write(
                "Reporting a crime used to feel hopeless. This platform made it simple — "
                "I submitted my case, got confirmation, and could track what was happening."
            )
            st.caption("— Ahmed Khan, Verified User · Karachi")

        with st.container(border=True):
            st.write("⭐⭐⭐⭐⭐")
            st.write(
                "As a law enforcement coordinator, the analytics dashboard is invaluable. "
                "Crime heatmaps, severity filters, station workload — all in one place."
            )
            st.caption("— Supt. Imran Siddiqui, Admin · Lahore Police")

    with col_cta:
        st.subheader("🚀 Report. Track. Resolve.")
        st.write(
            "Join thousands of citizens using UCARS to submit verified crime reports, "
            "monitor case progress, and hold the system accountable."
        )

        # Metrics with custom styling via st.metric
        st.metric("Reports Filed", "12K+")
        st.metric("Cases Tracked", "94%")
        st.metric("Stations Linked", "80+")

        st.markdown("<br/>", unsafe_allow_html=True)

        if st.session_state.get("logged_in"):
            # User is already logged in
            st.success(f"👋 Welcome back, {st.session_state.get('user_name')}!")
            if st.button("Go to My Dashboard →", use_container_width=True, key="go_dashboard"):
                st.session_state.current_page = "user_dashboard"
                st.rerun()
        else:
            # No one logged in
            if st.button("🚀 Get Started →", use_container_width=True, key="get_started"):
                st.session_state.current_page = "login"
                st.rerun()

    footer()