# views/about.py
import streamlit as st
from utils.styles import get_theme, navbar, footer


def show():
    get_theme()
    navbar("about")

    st.title("🛡️ About UCARS")
    st.write(
        "The **Urban Crime Analysis & Reporting System** bridges the gap between "
        "citizens and law enforcement. It enables victims to file verified crime "
        "reports digitally, track case progress in real-time, and empowers "
        "administrators with powerful analytics."
    )

    st.divider()
    st.subheader("⚙️ Core Features")

    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.write("📋 **Easy Crime Reporting**")
            st.caption(
                "Submit detailed incident reports with evidence uploads, "
                "location tagging, and OTP-verified submissions."
            )
        with st.container(border=True):
            st.write("🔍 **Real-Time Case Tracking**")
            st.caption(
                "Monitor your filed reports at every stage — from submission "
                "through investigation to resolution."
            )
        with st.container(border=True):
            st.write("🔒 **Secure & Transparent**")
            st.caption(
                "Google OAuth login, OTP email verification, full audit logs, "
                "and role-based access."
            )

    with col2:
        with st.container(border=True):
            st.write("📊 **Crime Analytics**")
            st.caption(
                "Live dashboards with heatmaps, severity charts, "
                "station workload analysis, and trend reports."
            )
        with st.container(border=True):
            st.write("🏢 **Police Station Network**")
            st.caption(
                "Incidents routed to relevant police stations. "
                "Admins can reassign and manage suspects."
            )
        with st.container(border=True):
            st.write("🗂️ **Full Audit Trail**")
            st.caption(
                "Every action logged with timestamp and IP address "
                "for complete transparency."
            )

    st.divider()
    st.subheader("🛠️ Built With")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.info("FastAPI")
        st.info("MySQL")
    with col2:
        st.info("Streamlit")
        st.info("Google OAuth")
    with col3:
        st.info("Plotly")
        st.info("Altair")
    with col4:
        st.info("JWT Auth")
        st.info("SMTP OTP")

    footer()