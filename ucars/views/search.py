# views/search.py
import streamlit as st
from utils.styles import get_theme
from utils.auth import require_login
from utils.api import (
    get_search_locations,
    get_search_categories,
    search_incidents
)
from views.user_dashboard import user_sidebar


def show():
    get_theme()
    require_login()
    user_sidebar()

    st.title("🔍 Search Incidents")
    st.caption("Search and filter crime incidents by location or category.")
    st.divider()

    # ── Filter dropdown ──
    filter_type = st.selectbox(
        "Search By",
        ["All Incidents", "Location Wise", "Category Wise"],
        index=0
    )

    area_name     = None
    city          = None
    category_name = None

    # ── Location filter ──
    if filter_type == "Location Wise":
        with st.spinner("Loading locations..."):
            loc_data = get_search_locations()

        if loc_data and loc_data.get("locations"):
            locations = loc_data["locations"]
            options   = [l["complete_location"] for l in locations]
            selected  = st.selectbox("Select Location", options)

            # Extract area_name and city from selected
            for l in locations:
                if l["complete_location"] == selected:
                    area_name = l["area_name"]
                    city      = l["city"]
                    break
        else:
            st.warning("No locations found.")
            return

    # ── Category filter ──
    elif filter_type == "Category Wise":
        with st.spinner("Loading categories..."):
            cat_data = get_search_categories()

        if cat_data and cat_data.get("categories"):
            categories = cat_data["categories"]
            options    = [
                f"{c['category_name']} ({c['incident_count']} incidents)"
                for c in categories
            ]
            selected = st.selectbox("Select Category", options)

            # Extract category_name
            for c in categories:
                label = f"{c['category_name']} ({c['incident_count']} incidents)"
                if label == selected:
                    category_name = c["category_name"]
                    break
        else:
            st.warning("No categories found.")
            return

    st.divider()

    # ── Fetch results ──
    with st.spinner("Searching incidents..."):
        if filter_type == "All Incidents":
            result = search_incidents(all_cases=True)
        elif filter_type == "Location Wise":
            result = search_incidents(
                location_wise=True,
                area_name=area_name,
                city=city
            )
        else:
            result = search_incidents(
                category_wise=True,
                category_name=category_name
            )

    if not result:
        st.error("❌ Failed to fetch results.")
        return

    incidents = result.get("results", [])
    total     = result.get("total", 0)
    filters   = result.get("active_filters", {})

    # ── Summary ──
    if filter_type == "All Incidents":
        st.info(f"📊 Showing all **{total}** incident(s) in the system.")

    elif filter_type == "Location Wise":
        loc = filters.get("complete_location", "selected location")
        st.info(f"📍 **{total}** incident(s) found in **{loc}**.")

    else:
        cat = filters.get("category_name", "selected category")
        st.info(f"📁 **{total}** incident(s) found in category **{cat}**.")

    if total == 0:
        st.warning("No incidents found for the selected filter.")
        return

    st.divider()

    # ── Visual: Bar chart ──
    if filter_type == "All Incidents" and incidents:
        st.subheader("📊 Incidents by Category")
        import pandas as pd

        # Count by category
        cat_counts = {}
        for inc in incidents:
            cat = inc.get("category_name", "Unknown")
            cat_counts[cat] = cat_counts.get(cat, 0) + 1

        df = pd.DataFrame(
            list(cat_counts.items()),
            columns=["Category", "Count"]
        ).sort_values("Count", ascending=False)

        st.bar_chart(df.set_index("Category"))
        st.divider()

    elif filter_type == "Location Wise" and incidents:
        st.subheader("📊 Incidents by Category at this Location")
        import pandas as pd

        cat_counts = {}
        for inc in incidents:
            cat = inc.get("category_name", "Unknown")
            cat_counts[cat] = cat_counts.get(cat, 0) + 1

        df = pd.DataFrame(
            list(cat_counts.items()),
            columns=["Category", "Count"]
        ).sort_values("Count", ascending=False)

        st.bar_chart(df.set_index("Category"))
        st.divider()

    elif filter_type == "Category Wise" and incidents:
        st.subheader("📊 Incidents by Location for this Category")
        import pandas as pd

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