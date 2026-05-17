# app.py
import streamlit as st
from utils.auth import init_session

from views.landing        import show as show_landing
from views.login          import show as show_login
from views.register       import show as show_register
from views.otp            import show as show_otp
from views.about          import show as show_about
from views.user_dashboard import show as show_user_dashboard
from views.report_detail  import show as show_report_detail
from views.new_form       import show as show_new_form
from views.search         import show as show_search
from views.admin_dashboard import show as show_admin_dashboard
from views.admin_search    import show as show_admin_search
from views.admin_logs      import show as show_admin_logs

st.set_page_config(
    page_title="UCARS",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session()

# ── Single token check — handles both fresh login and refresh ──
if not st.session_state.get("logged_in"):
    token = st.query_params.get("access_token")
    name  = st.query_params.get("name")
    email = st.query_params.get("email")
    role  = st.query_params.get("role")

    if token:
        st.session_state.logged_in    = True
        st.session_state.auth_token   = token
        st.session_state.user_name    = name
        st.session_state.user_email   = email
        st.session_state.user_role    = role
        st.session_state.current_page = (
            "admin_dashboard" if role == "admin" else "user_dashboard"
        )
        st.query_params.clear()
        st.rerun()

# ── Get current page ──
page = st.session_state.get("current_page", "home")

# ── Router ──
routes = {
    "home":           show_landing,
    "login":          show_login,
    "register":       show_register,
    "otp":            show_otp,
    "about":          show_about,
    "user_dashboard": show_user_dashboard,
    "report_detail":  show_report_detail,
    "new_form":       show_new_form,
    "search":         show_search,
    "admin_dashboard": show_admin_dashboard,
    "admin_search":    show_admin_search,
    "admin_logs":      show_admin_logs,
}

routes.get(page, show_landing)()






