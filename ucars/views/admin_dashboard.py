# views/admin_dashboard.py
import streamlit as st
import base64
from datetime import datetime, date
from utils.styles import get_theme
from utils.auth import require_admin
from utils.api import (
    get_all_users, get_user_incidents,
    get_user_incident_detail, admin_update_incident,
    admin_delete_incident, get_user_by_id
)


def _fmt_dt(val) -> str:
    """FIX 1: Format ISO datetime to readable string."""
    if not val:
        return "—"
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f"):
        try:
            return datetime.strptime(str(val), fmt).strftime("%d %b %Y, %I:%M %p")
        except ValueError:
            continue
    return str(val)


def _show_image(data_str: str, caption: str):
    """Display image from base64 string."""
    if not data_str:
        st.caption(f"No {caption} uploaded.")
        return
    try:
        img_bytes = base64.b64decode(data_str)
        st.image(img_bytes, caption=caption, use_container_width=True)
    except Exception:
        try:
            st.image(data_str, caption=caption, use_container_width=True)
        except Exception:
            st.caption(f"Cannot display {caption}.")


def admin_sidebar():
    with st.sidebar:
        st.title("⚡ UCARS Admin")
        st.divider()
        st.write(f"🛡️ **{st.session_state.get('user_name', 'Admin')}**")
        st.caption(st.session_state.get('user_email', ''))
        st.caption("🔴 Administrator")
        st.divider()
        st.caption("NAVIGATION")

        if st.button("🏠  Dashboard", key="asb_dashboard", use_container_width=True):
            st.session_state.admin_view = None
            st.session_state.admin_selected_user = None
            st.session_state.admin_selected_incident = None
            st.session_state.current_page = "admin_dashboard"
            st.rerun()

        if st.button("🔍  Search", key="asb_search", use_container_width=True):
            st.session_state.current_page = "admin_search"
            st.rerun()

        if st.button("📋  Transaction / Logs", key="asb_logs", use_container_width=True):
            st.session_state.current_page = "admin_logs"
            st.rerun()

        st.divider()

        if st.button("🚪  Logout", key="asb_logout", use_container_width=True):
            from utils.api import logout
            from utils.auth import logout_user
            st.query_params.clear()
            logout()
            logout_user()
            st.session_state.current_page = "home"
            st.rerun()


def show():
    get_theme()
    require_admin()
    admin_sidebar()

    if st.session_state.get("admin_view") == "incident_detail":
        _show_incident_detail()
        return

    if st.session_state.get("admin_view") == "user_incidents":
        _show_user_incidents()
        return

    st.title("🛡️ Admin Dashboard")
    st.caption("All registered users are listed below.")
    st.divider()

    with st.spinner("Loading users..."):
        response = get_all_users()

    users = response.get("users", []) if response else []
    total = response.get("total", 0) if response else 0

    st.write(f"**Total Users:** {total}")
    st.divider()

    if not users:
        st.info("No registered users found.")
        return

    for u in users:
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**👤 {u.get('name', 'Unknown')}**")
                st.caption(
                    f"📧 {u.get('email', '—')}  |  "
                    f"🆔 User ID: {u.get('user_id')}  |  "
                    f"📅 Joined: {u.get('created_at', '—')}"
                )
            with col2:
                if st.button("📂 View Reports", key=f"view_user_{u['user_id']}"):
                    st.session_state.admin_selected_user = u
                    st.session_state.admin_view = "user_incidents"
                    st.rerun()


def _show_user_incidents():
    u = st.session_state.get("admin_selected_user", {})

    if st.button("← Back to Users", key="back_to_users"):
        st.session_state.admin_view = None
        st.session_state.admin_selected_user = None
        st.rerun()

    st.title(f"📂 Reports — {u.get('name', 'User')}")
    st.caption(f"📧 {u.get('email')}  |  🆔 User ID: {u.get('user_id')}")
    st.divider()

    with st.spinner("Loading incidents..."):
        response = get_user_incidents(u["user_id"])

    incidents = response.get("incidents", []) if response else []
    total     = response.get("total", 0) if response else 0

    if not incidents:
        st.info("📭 This user has not submitted any reports yet.")
        return

    st.write(f"**Total Reports:** {total}")
    st.divider()

    for inc in incidents:
        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**#{inc.get('incident_id')} — {inc.get('title', 'Untitled')}**")
                st.caption(
                    f"📁 {inc.get('category_name', '—')}  |  "
                    # FIX 1: formatted date in incident cards too
                    f"📅 {_fmt_dt(inc.get('incident_datetime'))}  |  "
                    f"📍 {inc.get('area_name', '—')}, {inc.get('city', '—')}"
                )
                status = inc.get("status_name", "Waiting")
                {
                    "Waiting":                       st.warning,
                    "Accepted; Under Investigation": st.info,
                    "Investigated":                  st.success,
                    "Rejected":                      st.error,
                }.get(status, st.warning)(f"Status: {status}")

            with col2:
                if st.button("📝 Edit", key=f"edit_inc_{inc['incident_id']}"):
                    with st.spinner("Loading..."):
                        detail = get_user_incident_detail(u["user_id"], inc["incident_id"])
                    if detail:
                        st.session_state.admin_selected_incident = detail
                        st.session_state.admin_selected_incident_id = inc["incident_id"]
                        st.session_state.admin_view = "incident_detail"
                        st.rerun()

            with col3:
                if inc.get("status_name") == "Rejected":
                    if st.button("🗑️ Delete", key=f"del_inc_{inc['incident_id']}"):
                        with st.spinner("Deleting..."):
                            result = admin_delete_incident(u["user_id"], inc["incident_id"])
                        if result:
                            st.success("✅ Incident deleted!")
                            st.rerun()
                else:
                    st.caption("Delete only for Rejected")


def _show_incident_detail():
    data = st.session_state.get("admin_selected_incident", {})
    u    = st.session_state.get("admin_selected_user", {})

    if st.button("← Back to Reports", key="back_to_incidents"):
        st.session_state.admin_view = "user_incidents"
        st.session_state.admin_selected_incident = None
        st.rerun()

    inc      = data.get("incident", {})
    loc      = data.get("location", {})
    vic      = data.get("victim", {})
    stat     = data.get("case_status", {})
    suspects = data.get("suspects", [])
    stations = data.get("police_stations", [])
    sus      = suspects[0] if suspects else {}

    incident_city = loc.get("city", "")

    st.title(f"📝 Edit — {inc.get('title', 'Incident')}")
    st.caption(f"Incident ID: #{inc.get('incident_id')}  |  User: {u.get('name')}")
    st.divider()

    # ── Read-only: Victim Info ──
    st.subheader("👤 Victim Information (Read Only)")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Name:** {vic.get('name') or '—'}")
        st.write(f"**CNIC:** {vic.get('cnic') or '—'}")
        st.write(f"**Phone:** {vic.get('phone') or '—'}")
    with col2:
        st.write(f"**Email:** {vic.get('email') or '—'}")
        st.write(f"**Address:** {vic.get('address') or '—'}")
        st.write(f"**Injury Type:** {vic.get('injury_type') or '—'}")
    st.divider()

    # ── Read-only: Incident Info ──
    st.subheader("🚨 Incident Information (Read Only)")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Title:** {inc.get('title') or '—'}")
        st.write(f"**Category:** {inc.get('category_name') or '—'}")
        # FIX 1: formatted dates
        st.write(f"**Date:** {_fmt_dt(inc.get('incident_datetime'))}")
        st.write(f"**Reported At:** {_fmt_dt(inc.get('reported_at'))}")
    with col2:
        st.write(f"**Area:** {loc.get('area_name') or '—'}")
        st.write(f"**City:** {incident_city or '—'}")
        st.write(f"**Street:** {loc.get('street_address') or '—'}")
        st.write(f"**Postal Code:** {loc.get('postal_code') or '—'}")
    st.write("**Description:**")
    st.info(inc.get("description") or "No description.")

    # FIX 4: Show CCTV and suspect photo in admin read-only section
    st.divider()
    st.subheader("📷 Evidence Media (Read Only)")
    col1, col2 = st.columns(2)
    with col1:
        st.write("**CCTV Footage / Image:**")
        _show_image(loc.get("cctv_footage_path"), "CCTV")
    with col2:
        st.write("**Suspect Photo:**")
        _show_image(sus.get("suspect_picture"), "Suspect Photo")

    st.divider()

    # ── Station count outside form ──
    incident_key = f"num_stations_{inc.get('incident_id')}"
    if incident_key not in st.session_state:
        st.session_state[incident_key] = max(1, len(stations))

    st.subheader("🔧 Admin Update Form")
    st.caption("Fill in the fields below and click Update to save.")

    form_key = f"admin_update_form_{inc.get('incident_id')}"

    with st.form(form_key):

        severity_options = ["Low", "Medium", "High"]
        current_severity = inc.get("crime_severity")
        severity_index   = severity_options.index(current_severity) \
            if current_severity in severity_options else 0
        crime_severity = st.selectbox(
            "Crime Severity *", severity_options, index=severity_index
        )

        if crime_severity == "High":
            st.info("ℹ️ High severity requires 2 or more police stations.")
        else:
            st.info("ℹ️ Low/Medium severity requires exactly 1 police station.")

        status_options = [
            "Waiting",
            "Accepted; Under Investigation",
            "Investigated",
            "Rejected",
        ]
        current_status = stat.get("status_name", "Waiting")
        status_index   = status_options.index(current_status) \
            if current_status in status_options else 0
        case_status = st.selectbox(
            "Case Status *", status_options, index=status_index
        )

        st.divider()
        st.write("**🕵️ Suspect Information**")
        col1, col2 = st.columns(2)
        with col1:
            suspect_name = st.text_input(
                "Suspect Name", value=sus.get("suspect_name") or ""
            )
            suspect_cnic = st.text_input(
                "Suspect CNIC",
                value=sus.get("suspect_cnic") or "",
                max_chars=15,
                placeholder="e.g. 42101-1234567-1"
            )
        with col2:
            suspect_status_opts = [
                "Unconfirmed criminal- IN custody",
                "Arrested and confirmed criminal",
                "Not arrested but confirmed criminal",
            ]
            cur_ss = sus.get("suspect_status")
            ss_idx = suspect_status_opts.index(cur_ss) \
                if cur_ss in suspect_status_opts else 0
            suspect_status = st.selectbox(
                "Suspect Status", suspect_status_opts, index=ss_idx
            )
            # FIX 5: max_value=date.today() blocks future arrest dates
            suspect_arrest_date = st.date_input(
                "Arrest Date",
                value=None,
                max_value=date.today(),       # ← blocks future arrest dates
            )

        st.divider()

        num_stations = st.session_state[incident_key]
        st.write(f"**🏫 Police Station Details ({num_stations} station(s))**")
        st.caption(f"City is auto-filled from incident location: **{incident_city}**")

        station_data = []
        for i in range(num_stations):
            st.write(f"**Station {i + 1}**")
            existing = stations[i] if i < len(stations) else {}
            sc1, sc2 = st.columns(2)
            with sc1:
                sname = st.text_input(
                    "Station Name",
                    value=existing.get("station_name") or "",
                    key=f"sname_{i}"
                )
                scity = st.text_input(
                    "Station City (auto-filled)",
                    value=incident_city,
                    key=f"scity_{i}",
                    disabled=True
                )
            with sc2:
                saddr = st.text_input(
                    "Station Address",
                    value=existing.get("station_address") or "",
                    key=f"saddr_{i}"
                )
                sofficer = st.text_input(
                    "Incharge Officer",
                    value=existing.get("incharge_officer_name") or "",
                    key=f"sofficer_{i}"
                )
            scharges = st.number_input(
                "Charges Filed",
                min_value=0,
                value=int(existing.get("charges_filed") or 0),
                key=f"scharges_{i}"
            )
            station_data.append({
                "station_name":          sname,
                "city":                  incident_city,
                "address":               saddr,
                "incharge_officer_name": sofficer,
                "charges_filed":         scharges,
            })

        submitted = st.form_submit_button(
            "💾 Update Incident", use_container_width=True
        )

    # ── Station add/remove outside form ──
    col_add, col_remove, _ = st.columns([1, 1, 3])
    with col_add:
        if st.button("➕ Add Station", key="add_station"):
            if crime_severity != "High":
                st.warning("⚠️ You can only add more stations for **High** severity incidents.")
            elif st.session_state[incident_key] < 5:
                st.session_state[incident_key] += 1
                st.rerun()
    with col_remove:
        if st.button("➖ Remove Station", key="remove_station"):
            min_required = 2 if crime_severity == "High" else 1
            if st.session_state[incident_key] > min_required:
                st.session_state[incident_key] -= 1
                st.rerun()

    if submitted:
        errors = []
        
        # Suspect CNIC validation
        if suspect_cnic.strip():
            import re
            cnic_digits = re.sub(r"[-]", "", suspect_cnic.strip())
            if not cnic_digits.isdigit():
                errors.append(
                    "Suspect CNIC can only contain digits and hyphens (-)."
                    " Letters and special characters are not allowed."
                    " Example: 42101-1234567-1"
                )
            elif len(cnic_digits) != 13:
                errors.append(
                    f"Suspect CNIC must be exactly 13 digits."
                    f" You entered {len(cnic_digits)} digit(s)."
                )

        if crime_severity == "High" and num_stations < 2:
            errors.append("⚠️ High severity requires at least 2 police stations.")

        restricted_statuses = ["Waiting", "Accepted; Under Investigation"]
        restricted_suspect  = [
            "Arrested and confirmed criminal",
            "Not arrested but confirmed criminal",
        ]
        if case_status in restricted_statuses and suspect_status in restricted_suspect:
            errors.append(
                f"⚠️ Suspect status cannot be **'{suspect_status}'** "
                f"when case is **'{case_status}'**. Set case to Investigated first."
            )

        if suspect_status == "Arrested and confirmed criminal":
            if not suspect_name.strip():
                errors.append("⚠️ Suspect **Name** is required when status is 'Arrested and confirmed criminal'.")
            if not suspect_cnic.strip():
                errors.append("⚠️ Suspect **CNIC** is required when status is 'Arrested and confirmed criminal'.")
            if not suspect_arrest_date:
                errors.append("⚠️ **Arrest Date** is required when status is 'Arrested and confirmed criminal'.")

        if case_status != "Waiting":
            for i, s in enumerate(station_data):
                if not s["station_name"].strip():
                    errors.append(f"⚠️ Station {i+1}: **Station Name** is required.")
                if not s["address"].strip():
                    errors.append(f"⚠️ Station {i+1}: **Station Address** is required.")
                if not s["incharge_officer_name"].strip():
                    errors.append(f"⚠️ Station {i+1}: **Incharge Officer** is required.")

        if errors:
            for e in errors:
                st.warning(e)
            return

        if crime_severity in ["Low", "Medium"] and num_stations > 1:
            st.warning(f"⚠️ **{crime_severity}** severity requires exactly **1 police station**.")
            return

        # Suspect CNIC validation
        if suspect_cnic.strip():
            import re
            cnic_digits = re.sub(r"[-\s]", "", suspect_cnic.strip())
            if not cnic_digits.isdigit():
                errors.append("Suspect CNIC must contain numbers only (e.g. 42101-1234567-1). Letters are not allowed.")
            elif len(cnic_digits) != 13:
                errors.append(f"Suspect CNIC must be exactly 13 digits. You entered {len(cnic_digits)}.")

        payload = {
            "crime_severity": crime_severity,
            "status_name":    case_status,
            "suspect": {
                "name":        suspect_name.strip() or None,
                "cnic":        suspect_cnic.strip() or None,
                "status":      suspect_status,
                "arrest_date": str(suspect_arrest_date) if suspect_arrest_date else None,
            },
            "police_stations": station_data,
        }

        with st.spinner("Updating..."):
            result = admin_update_incident(u["user_id"], inc["incident_id"], payload)

        if result:
            st.success("✅ Incident updated successfully!")
            if incident_key in st.session_state:
                del st.session_state[incident_key]
            with st.spinner("Refreshing..."):
                detail = get_user_incident_detail(u["user_id"], inc["incident_id"])
            if detail:
                st.session_state.admin_selected_incident = detail
            st.rerun()
        else:
            st.error("❌ Update failed. Please try again.")