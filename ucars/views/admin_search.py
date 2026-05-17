# views/admin_search.py
import streamlit as st
from utils.styles import get_theme
from utils.auth import require_admin
from utils.api import (
    admin_get_locations, admin_get_categories,
    admin_get_case_statuses, admin_get_police_stations,
    admin_search_incidents
)
from views.admin_dashboard import admin_sidebar
from datetime import datetime


def _fmt_dt(val) -> str:
    if not val:
        return "—"
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f"):
        try:
            return datetime.strptime(str(val), fmt).strftime("%d %b %Y, %I:%M %p")
        except ValueError:
            continue
    return str(val)


def show():
    get_theme()
    require_admin()
    admin_sidebar()

    st.title("🔍 Admin Search")
    st.caption("Search and filter all crime incidents.")
    st.divider()

    filter_type = st.selectbox(
        "Search By",
        ["All Incidents", "Location Wise", "Category Wise",
         "Case Status Wise", "Police Station Wise"],
        key="admin_search_filter_type",
        index=0
    )

    # Reset stored filter values when filter type changes
    if st.session_state.get("_last_filter_type") != filter_type:
        st.session_state["_last_filter_type"] = filter_type
        st.session_state["_search_area_name"]    = None
        st.session_state["_search_city"]         = None
        st.session_state["_search_category"]     = None
        st.session_state["_search_status"]       = None
        st.session_state["_search_station"]      = None

    ready = True

    # ── Location filter ──
    if filter_type == "Location Wise":
        ready = False
        with st.spinner("Loading locations..."):
            loc_data = admin_get_locations()
        if loc_data and loc_data.get("locations"):
            options  = [l["complete_location"] for l in loc_data["locations"]]
            selected = st.selectbox("Select Location", options,
                                    key="admin_search_location")
            for l in loc_data["locations"]:
                if l["complete_location"] == selected:
                    st.session_state["_search_area_name"] = l["area_name"]
                    st.session_state["_search_city"]      = l["city"]
                    break
            ready = bool(st.session_state.get("_search_area_name"))
        else:
            st.warning("No locations found.")
            return

    # ── Category filter ──
    elif filter_type == "Category Wise":
        ready = False
        with st.spinner("Loading categories..."):
            cat_data = admin_get_categories()
        if cat_data and cat_data.get("categories"):
            cat_map  = {
                f"{c['category_name']} ({c['incident_count']} incidents)": c["category_name"]
                for c in cat_data["categories"]
            }
            selected = st.selectbox("Select Category", list(cat_map.keys()),
                                    key="admin_search_category")
            st.session_state["_search_category"] = cat_map.get(selected)
            ready = bool(st.session_state["_search_category"])
        else:
            st.warning("No categories found.")
            return

    # ── Case Status filter ──
    elif filter_type == "Case Status Wise":
        ready = False
        with st.spinner("Loading statuses..."):
            stat_data = admin_get_case_statuses()
        if stat_data and stat_data.get("statuses"):
            stat_map = {
                f"{s['status_name']} ({s['incident_count']} incidents)": s["status_name"]
                for s in stat_data["statuses"]
            }
            selected = st.selectbox("Select Status", list(stat_map.keys()),
                                    key="admin_search_status")
            st.session_state["_search_status"] = stat_map.get(selected)
            ready = bool(st.session_state["_search_status"])
        else:
            st.warning("No statuses found.")
            return

    # ── Police Station filter ──
    elif filter_type == "Police Station Wise":
        ready = False
        with st.spinner("Loading stations..."):
            ps_data = admin_get_police_stations()
        if ps_data and ps_data.get("stations"):
            ps_map = {
                f"{p['station_name']} ({p['incident_count']} incidents)": p["station_name"]
                for p in ps_data["stations"]
            }
            selected = st.selectbox(
                "Select Police Station", list(ps_map.keys()),
                key="admin_search_station"
            )
            st.session_state["_search_station"] = ps_map.get(selected)
            ready = bool(st.session_state["_search_station"])
        else:
            st.warning("No police stations found.")
            return

    st.divider()

    search_clicked = st.button("🔍 Search", use_container_width=True)

    if not search_clicked:
        return

    if not ready:
        st.warning("⚠️ Please select a valid filter value before searching.")
        return

    # ── Read values from session state (survives rerun) ──
    area_name     = st.session_state.get("_search_area_name")
    city          = st.session_state.get("_search_city")
    category_name = st.session_state.get("_search_category")
    status_name   = st.session_state.get("_search_status")
    station_name  = st.session_state.get("_search_station")

    # ── Fetch results ──
    with st.spinner("Searching..."):
        if filter_type == "All Incidents":
            result = admin_search_incidents(all_cases=True)
        elif filter_type == "Location Wise":
            result = admin_search_incidents(
                location_wise=True,
                area_name=area_name,
                city=city
            )
        elif filter_type == "Category Wise":
            result = admin_search_incidents(
                category_wise=True,
                category_name=category_name
            )
        elif filter_type == "Case Status Wise":
            result = admin_search_incidents(
                casestatus_wise=True,
                status_name=status_name
            )
        else:
            result = admin_search_incidents(
                policestation_wise=True,
                station_name=station_name
            )

    if not result:
        st.error("❌ Failed to fetch results.")
        return

    incidents = result.get("results", [])
    total     = result.get("total", 0)

    st.info(f"📊 **{total}** incident(s) found.")

    if total == 0:
        st.warning("No incidents found for the selected filter.")
        return

    # ── Visual chart ──
    if incidents:
        import pandas as pd
        st.subheader("📊 Visual Summary")

        if filter_type in ["All Incidents", "Location Wise",
                            "Case Status Wise", "Police Station Wise"]:
            cat_counts = {}
            for inc in incidents:
                cat = inc.get("category_name", "Unknown")
                cat_counts[cat] = cat_counts.get(cat, 0) + 1
            df = pd.DataFrame(
                list(cat_counts.items()),
                columns=["Category", "Count"]
            ).sort_values("Count", ascending=False)
            st.bar_chart(df.set_index("Category"))

        elif filter_type == "Category Wise":
            loc_counts = {}
            for inc in incidents:
                loc = inc.get("area_name", "Unknown")
                loc_counts[loc] = loc_counts.get(loc, 0) + 1
            df = pd.DataFrame(
                list(loc_counts.items()),
                columns=["Location", "Count"]
            ).sort_values("Count", ascending=False)
            st.bar_chart(df.set_index("Location"))

    st.divider()

    # ── Results ──
    st.subheader(f"📋 Results ({total})")
    for inc in incidents:
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(
                    f"**#{inc.get('incident_id')} — "
                    f"{inc.get('title', 'Untitled')}**"
                )
                st.caption(
                    f"📁 {inc.get('category_name', '—')}  |  "
                    f"📅 {_fmt_dt(inc.get('incident_datetime'))}  |  "
                    f"📍 {inc.get('area_name', '—')}, {inc.get('city', '—')}"
                )
            with col2:
                status = inc.get("status_name", "Waiting")
                {
                    "Waiting":                       st.warning,
                    "Accepted; Under Investigation": st.info,
                    "Investigated":                  st.success,
                    "Rejected":                      st.error,
                }.get(status, st.warning)(status)