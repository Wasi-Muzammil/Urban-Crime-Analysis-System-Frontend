# utils/auth.py
import streamlit as st


def init_session():
    """Initialize session state keys only if not already set."""
    defaults = {
        "logged_in":    False,
        "user_id":      None,
        "user_name":    "",
        "user_email":   "",
        "user_role":    None,
        "auth_token":   None,
        "otp_verified": False,
        "current_page": "home",  # only set if not already set
    }
    for key, val in defaults.items():
        if key not in st.session_state:  # ← only set if missing
            st.session_state[key] = val


def login_user(user_data: dict, token: str):
    st.session_state.logged_in  = True
    st.session_state.user_id    = user_data.get("user_id")
    st.session_state.user_name  = user_data.get("name", "")
    st.session_state.user_email = user_data.get("email", "")
    st.session_state.user_role  = user_data.get("role", "viewer")
    st.session_state.auth_token = token


def logout_user():
    """Clear session on logout."""
    st.session_state.logged_in    = False
    st.session_state.user_id      = None
    st.session_state.user_name    = ""
    st.session_state.user_email   = ""
    st.session_state.user_role    = None
    st.session_state.auth_token   = None
    st.session_state.otp_verified = False
    st.session_state.current_page = "home"


def require_login():
    """Stop page if not logged in."""
    if not st.session_state.get("logged_in"):
        st.warning("⚠️ Please log in to access this page.")
        st.stop()


def require_admin():
    """Stop page if not admin."""
    require_login()
    if st.session_state.get("user_role") != "admin":
        st.error("🚫 Access denied. Admins only.")
        st.stop()


def get_headers():
    """Return auth headers for API requests."""
    token = st.session_state.get("auth_token")
    return {"Authorization": f"Bearer {token}"} if token else {}