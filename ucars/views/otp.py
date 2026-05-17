# views/otp.py
import streamlit as st
from utils.styles import get_theme, footer


def show():
    get_theme()

    _, col, _ = st.columns([1, 1.2, 1])

    with col:
        st.divider()
        st.warning("📧 Email Verification")
        st.title("Enter Your OTP")
        st.caption(
            "A 6-digit verification code was sent to your registered email. "
            "Enter it below to confirm your identity."
        )
        st.divider()

        with st.form("otp_form"):
            otp_code  = st.text_input("OTP Code", placeholder="Enter 6-digit code",
                                       max_chars=6)
            submitted = st.form_submit_button("✅ Verify OTP", use_container_width=True)

        if submitted:
            if len(otp_code) != 6 or not otp_code.isdigit():
                st.error("⚠️ Please enter a valid 6-digit OTP.")
            else:
                from utils.api import _post
                email  = st.session_state.get("user_email", "")
                result = _post("/verify-otp", {"email": email, "otp": otp_code})

                if result and result.get("verified"):
                    st.session_state.otp_verified = True
                    st.success("✅ Verified! Redirecting...")
                    role = st.session_state.get("user_role")
                    st.session_state.current_page = (
                        "admin_dashboard" if role == "admin" else "user_dashboard"
                    )
                    st.rerun()
                else:
                    st.error("❌ Invalid or expired OTP. Please try again.")

        st.caption("Didn't receive the code? Contact support.")

    footer()