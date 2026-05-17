# views/new_form.py
import streamlit as st
from utils.styles import get_theme
from utils.auth import require_login
from utils.api import submit_crime_report
from datetime import datetime, date
import re


def validate_cnic(cnic: str) -> str | None:
    digits = re.sub(r"[-\s]", "", cnic)
    if not digits.isdigit():
        return "CNIC must contain numbers only (e.g. 42101-1234567-1)."
    if len(digits) != 13:
        return f"CNIC must be exactly 13 digits. You entered {len(digits)}."
    return None


def validate_phone(phone: str) -> str | None:
    digits = re.sub(r"[-\s+]", "", phone)
    if not digits.isdigit():
        return "Phone must contain numbers only (e.g. 03001234567)."
    if len(digits) < 10 or len(digits) > 13:
        return f"Phone must be 10–13 digits. You entered {len(digits)}."
    return None


def show():
    get_theme()
    require_login()

    if st.button("← Back to Dashboard", key="back_to_dash"):
        st.session_state.current_page = "user_dashboard"
        st.rerun()

    st.title("📋 New Crime Report")
    st.caption("Fill in the details below to submit a new crime report.")
    st.divider()

    with st.form("crime_report_form"):

        st.subheader("🚨 Incident Information")

        title = st.text_input(
            "Title *", placeholder="e.g. Vehicle Theft at Main Street"
        )

        col1, col2 = st.columns(2)
        with col1:
            category_name = st.selectbox(
                "Category *",
                ["theft", "robbery", "assault", "homicide", "cybercrime", "fraud"]
            )
        with col2:
            # FIX 3: max_value=date.today() prevents future dates
            incident_date = st.date_input(
                "Incident Date *",
                value=date.today(),
                max_value=date.today(),       # ← blocks future dates
            )

        incident_time = st.time_input(
            "Incident Time (24 Hours clock) *",
            value=datetime.now().time()
        )

        description = st.text_area(
            "Description",
            placeholder="Describe what happened in detail... (optional)",
            height=120
        )

        st.divider()

        st.subheader("📍 Location Information")

        col1, col2 = st.columns(2)
        with col1:
            area_name = st.text_input(
                "Area Name *", placeholder="e.g. Gulshan-e-Iqbal"
            )
        with col2:
            city = st.text_input("City *", placeholder="e.g. Karachi")

        col3, col4 = st.columns(2)
        with col3:
            street_address = st.text_input(
                "Street Address", placeholder="e.g. Block 10, Street 5 (optional)"
            )
        with col4:
            postal_code = st.text_input(
                "Postal Code", placeholder="e.g. 75300 (optional)"
            )

        st.divider()

        st.subheader("👤 Victim Information")
        st.caption("Your name and email are automatically taken from your account.")

        col1, col2 = st.columns(2)
        with col1:
            victim_cnic = st.text_input(
                "CNIC *", placeholder="e.g. 42101-1234567-1", max_chars=15
            )
        with col2:
            victim_phone = st.text_input(
                "Phone *", placeholder="e.g. 03001234567", max_chars=13
            )

        victim_address = st.text_input(
            "Home Address", placeholder="Your home address (optional)"
        )
        injury_type = st.text_input(
            "Injury Type", placeholder="e.g. Minor bruises, None (optional)"
        )

        st.divider()

        st.subheader("📎 Evidence")
        st.caption("Upload images or footage if available (optional).")

        col1, col2 = st.columns(2)
        with col1:
            cctv_file = st.file_uploader(
                "CCTV Footage / Image",
                type=["jpg", "jpeg", "png", "webp", "mp4", "avi", "mov"],
                key="cctv_uploader"
            )
        with col2:
            picture_file = st.file_uploader(
                "Picture / Photo",
                type=["jpg", "jpeg", "png", "webp"],
                key="picture_uploader"
            )

        st.divider()

        submitted = st.form_submit_button(
            "🚀 Submit Crime Report", use_container_width=True
        )

    if submitted:
        errors = []

        if not title.strip():
            errors.append("Title is required.")
        if not area_name.strip():
            errors.append("Area Name is required.")
        if not city.strip():
            errors.append("City is required.")

        if not victim_cnic.strip():
            errors.append("CNIC is required.")
        else:
            err = validate_cnic(victim_cnic.strip())
            if err:
                errors.append(f"CNIC: {err}")

        if not victim_phone.strip():
            errors.append("Phone is required.")
        else:
            err = validate_phone(victim_phone.strip())
            if err:
                errors.append(f"Phone: {err}")

        if errors:
            st.error("Please fix the following before submitting:")
            for e in errors:
                st.markdown(f"• {e}")
            return

        # FIX: block future datetime — date+time combined must not exceed now
        from datetime import date as date_type
        combined_check = datetime.combine(incident_date, incident_time)
        if combined_check > datetime.now():
            errors.append("Incident date and time cannot be in the future.")

        if errors:
            st.error("Please fix the following before submitting:")
            for e in errors:
                st.markdown(f"• {e}")
            return

        combined_datetime = datetime.combine(
            incident_date, incident_time
        ).strftime("%Y-%m-%dT%H:%M:%S")

        payload = {
            "title":             title.strip(),
            "category_name":     category_name,
            "incident_datetime": combined_datetime,
            "area_name":         area_name.strip(),
            "city":              city.strip(),
            "victim_cnic":       victim_cnic.strip(),
            "victim_phone":      victim_phone.strip(),
        }

        if description.strip():    payload["description"]    = description.strip()
        if street_address.strip(): payload["street_address"] = street_address.strip()
        if postal_code.strip():    payload["postal_code"]    = postal_code.strip()
        if victim_address.strip(): payload["victim_address"] = victim_address.strip()
        if injury_type.strip():    payload["injury_type"]    = injury_type.strip()

        import base64
        if cctv_file:
            payload["cctv_footage_path"] = base64.b64encode(
                cctv_file.read()).decode()
        if picture_file:
            payload["picture_path"] = base64.b64encode(
                picture_file.read()).decode()

        with st.spinner("Submitting your report..."):
            result = submit_crime_report(payload)

        if result:
            st.success("✅ Crime report submitted successfully!")
            st.balloons()
            import time
            time.sleep(2)
            st.session_state.current_page = "user_dashboard"
            st.rerun()
        else:
            st.error("❌ Submission failed. Please check your inputs and try again.")