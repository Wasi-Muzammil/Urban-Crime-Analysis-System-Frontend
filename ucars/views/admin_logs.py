# views/admin_logs.py
import streamlit as st
import pandas as pd
from utils.styles import get_theme
from utils.auth import require_admin
from utils.api import admin_get_transaction_logs, admin_get_audit_logs
from views.admin_dashboard import admin_sidebar


def show():
    get_theme()
    require_admin()
    admin_sidebar()

    st.title("📋 Transaction & Audit Logs")
    st.caption("Monitor all system activity and security events.")
    st.divider()

    # ── Tab selector ──
    tab1, tab2 = st.tabs(["💳 Transaction Logs", "🔐 Audit Logs"])

    # ══════════════════════════════
    # TAB 1: TRANSACTION LOGS
    # ══════════════════════════════
    with tab1:
        st.subheader("💳 Transaction Logs")
        st.caption("Every INSERT, UPDATE, DELETE operation on core tables.")

        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            t_action = st.selectbox(
                "Action Type",
                ["All", "INSERT", "UPDATE", "DELETE"],
                key="t_action"
            )
        with col2:
            t_table = st.text_input(
                "Table Name",
                placeholder="e.g. Incident",
                key="t_table"
            )
        with col3:
            t_user_id = st.number_input(
                "User ID (0 = all)",
                min_value=0, value=0,
                key="t_user_id"
            )

        if st.button("🔍 Load Transaction Logs", use_container_width=True,
                     key="load_t_logs"):
            with st.spinner("Loading..."):
                result = admin_get_transaction_logs(
                    user_id     = int(t_user_id) if t_user_id else None,
                    table_name  = t_table if t_table else None,
                    action_type = t_action if t_action != "All" else None,
                )

            if result:
                logs  = result.get("logs", [])
                total = result.get("total", 0)
                st.write(f"**Total:** {total}")

                if logs:
                    df = pd.DataFrame(logs)
                    # Reorder columns for clarity
                    cols = ["transaction_id", "user_name", "user_email",
                            "action_type", "table_name", "record_id",
                            "ip_address", "logged_at"]
                    cols = [c for c in cols if c in df.columns]
                    st.dataframe(df[cols], use_container_width=True)
                else:
                    st.info("No transaction logs found.")
            else:
                st.error("❌ Failed to load logs.")

    # ══════════════════════════════
    # TAB 2: AUDIT LOGS
    # ══════════════════════════════
    with tab2:
        st.subheader("🔐 Audit Logs")
        st.caption("Security events: logins, logouts, admin actions.")

        col1, col2 = st.columns(2)
        with col1:
            a_event = st.selectbox(
                "Event Type",
                ["All", "LOGIN", "LOGOUT", "ADMIN_ACTION"],
                key="a_event"
            )
        with col2:
            a_user_id = st.number_input(
                "User ID (0 = all)",
                min_value=0, value=0,
                key="a_user_id"
            )

        if st.button("🔍 Load Audit Logs", use_container_width=True,
                     key="load_a_logs"):
            with st.spinner("Loading..."):
                result = admin_get_audit_logs(
                    user_id    = int(a_user_id) if a_user_id else None,
                    event_type = a_event if a_event != "All" else None,
                )

            if result:
                logs  = result.get("logs", [])
                total = result.get("total", 0)
                st.write(f"**Total:** {total}")

                if logs:
                    df = pd.DataFrame(logs)
                    cols = ["audit_id", "user_name", "user_email",
                            "event_type", "description",
                            "ip_address", "logged_at"]
                    cols = [c for c in cols if c in df.columns]
                    st.dataframe(df[cols], use_container_width=True)
                else:
                    st.info("No audit logs found.")
            else:
                st.error("❌ Failed to load logs.")