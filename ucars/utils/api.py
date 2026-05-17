# utils/api.py
# All API calls to FastAPI backend — no mock data

import requests
import streamlit as st

BASE_URL = st.secrets["BACKEND_URL"]  


def _headers():
    """Attach JWT token to every protected request."""
    token = st.session_state.get("auth_token")
    return {"Authorization": f"Bearer {token}"} if token else {}


def _get(endpoint: str, params: dict = None):
    """Generic GET."""
    try:
        r = requests.get(
            f"{BASE_URL}/{endpoint}",
            headers=_headers(),
            params=params,
            timeout=30
        )
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to server. Is FastAPI running?")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ API Error {e.response.status_code}: {e.response.text}")
        return None
    except Exception as e:
        st.error(f"❌ Unexpected error: {e}")
        return None


def _post(endpoint: str, data: dict = None):
    """Generic POST."""
    try:
        r = requests.post(
            f"{BASE_URL}/{endpoint}",
            headers=_headers(),
            json=data,
            timeout=10
        )
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to server. Is FastAPI running?")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ API Error {e.response.status_code}: {e.response.text}")
        return None
    except Exception as e:
        st.error(f"❌ Unexpected error: {e}")
        return None


def _patch(endpoint: str, data: dict = None):
    """Generic PATCH."""
    try:
        r = requests.patch(
            f"{BASE_URL}/{endpoint}",
            headers=_headers(),
            json=data,
            timeout=10
        )
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to server. Is FastAPI running?")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ API Error {e.response.status_code}: {e.response.text}")
        return None
    except Exception as e:
        st.error(f"❌ Unexpected error: {e}")
        return None


# ══════════════════════════════════════════
# AUTH
# ══════════════════════════════════════════

def get_google_login_url() -> str:
    """Returns the Google OAuth redirect URL."""
    return f"{BASE_URL}/auth/google"


def logout():
    """Call logout endpoint to log audit."""
    return _post("/auth/logout")


# ══════════════════════════════════════════
# INCIDENTS (User)
# ══════════════════════════════════════════

def get_my_incidents():
    """GET /incidents/my-incidents — all reports by logged-in user."""
    return _get("/incidents/my-incidents")


def get_incident_detail(incident_id: int):
    """GET /incidents/{incident_id} — full detail of one report."""
    return _get(f"/incidents/{incident_id}")


def submit_crime_report(data: dict):
    """POST /incidents/report — file a new crime report."""
    return _post("/incidents/report", data)


def update_incident_media(incident_id: int, data: dict):
    """PATCH /incidents/{incident_id}/media — update CCTV/picture."""
    return _patch(f"/incidents/{incident_id}/media", data)


# ══════════════════════════════════════════
# SEARCH
# ══════════════════════════════════════════

def get_search_locations():
    """GET /search/locations — location dropdown options."""
    return _get("/search/locations")


def get_search_categories():
    """GET /search/categories — category dropdown options."""
    return _get("/search/categories")


def search_incidents(
    all_cases:     bool = False,
    location_wise: bool = False,
    category_wise: bool = False,
    area_name:     str  = None,
    city:          str  = None,
    category_name: str  = None,
):
    """GET /search/incidents — filtered incident search."""
    params = {
        "all_cases":     all_cases,
        "location_wise": location_wise,
        "category_wise": category_wise,
    }
    if area_name:     params["area_name"]     = area_name
    if city:          params["city"]          = city
    if category_name: params["category_name"] = category_name
    return _get("/search/incidents", params=params)


# ══════════════════════════════════════════
# USER LOGS
# ══════════════════════════════════════════

def get_my_transaction_logs(
    action_type: str = None,
    from_date:   str = None,
    to_date:     str = None,
):
    """GET /logs/my/logs/transactions."""
    params = {}
    if action_type: params["action_type"] = action_type
    if from_date:   params["from_date"]   = from_date
    if to_date:     params["to_date"]     = to_date
    return _get("/logs/my/logs/transactions", params=params)


def get_my_audit_logs(
    event_type: str = None,
    from_date:  str = None,
    to_date:    str = None,
):
    """GET /logs/my/logs/audit."""
    params = {}
    if event_type: params["event_type"] = event_type
    if from_date:  params["from_date"]  = from_date
    if to_date:    params["to_date"]    = to_date
    return _get("/logs/my/logs/audit", params=params)

# ══════════════════════════════════════════
# ADMIN — Users
# ══════════════════════════════════════════

def get_all_users():
    """GET /admin/users — all viewer accounts."""
    return _get("/admin/users")

def get_user_by_id(user_id: int):
    """GET /admin/users/{user_id}."""
    return _get(f"/admin/users/{user_id}")

def get_user_incidents(user_id: int):
    """GET /admin/users/{user_id}/incidents."""
    try:
        r = requests.get(
            f"{BASE_URL}/admin/users/{user_id}/incidents",
            headers=_headers(),
            timeout=10
        )
        # ── 404 means no victim record yet — treat as empty ──
        if r.status_code == 404:
            return {"incidents": [], "total": 0}
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to server.")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ API Error {e.response.status_code}: {e.response.text}")
        return None
    except Exception as e:
        st.error(f"❌ Error: {e}")
        return None

def get_user_incident_detail(user_id: int, incident_id: int):
    """GET /admin/users/{user_id}/incidents/{incident_id}."""
    return _get(f"/admin/users/{user_id}/incidents/{incident_id}")

def admin_update_incident(user_id: int, incident_id: int, data: dict):
    """PUT /admin/users/{user_id}/incidents/{incident_id}."""
    return _put(f"/admin/users/{user_id}/incidents/{incident_id}", data)

def admin_delete_incident(user_id: int, incident_id: int):
    """DELETE /admin/users/{user_id}/incidents/{incident_id}."""
    return _delete(f"/admin/users/{user_id}/incidents/{incident_id}")

def validate_station_count(incident_id: int, count: int):
    """GET /admin/incidents/{incident_id}/station-count."""
    return _get(f"/admin/incidents/{incident_id}/station-count",
                params={"count": count})

# ══════════════════════════════════════════
# ADMIN — Search
# ══════════════════════════════════════════

def admin_get_locations():
    return _get("/admin/search/locations")

def admin_get_categories():
    return _get("/admin/search/categories")

def admin_get_case_statuses():
    return _get("/admin/search/case-status")

def admin_get_police_stations():
    return _get("/admin/search/police-station")

def admin_search_incidents(
    all_cases=False, location_wise=False,
    category_wise=False, casestatus_wise=False,
    policestation_wise=False, area_name=None,
    city=None, category_name=None,
    status_name=None, station_name=None, limit=20
):
    params = {
        "all_cases":          all_cases,
        "location_wise":      location_wise,
        "category_wise":      category_wise,
        "casestatus_wise":    casestatus_wise,
        "policestation_wise": policestation_wise,
        "limit":              limit,
    }
    if area_name:     params["area_name"]     = area_name
    if city:          params["city"]          = city
    if category_name: params["category_name"] = category_name
    if status_name:   params["status_name"]   = status_name
    if station_name:  params["station_name"]  = station_name
    return _get("/admin/search/incidents", params=params)

# ══════════════════════════════════════════
# ADMIN — Logs
# ══════════════════════════════════════════

def admin_get_transaction_logs(user_id=None, table_name=None,
                                action_type=None, limit=100, offset=0):
    params = {"limit": limit, "offset": offset}
    if user_id:      params["user_id"]     = user_id
    if table_name:   params["table_name"]  = table_name
    if action_type:  params["action_type"] = action_type
    return _get("/admin/logs/transaction-logs", params=params)

def admin_get_audit_logs(user_id=None, event_type=None,
                          limit=100, offset=0):
    params = {"limit": limit, "offset": offset}
    if user_id:    params["user_id"]    = user_id
    if event_type: params["event_type"] = event_type
    return _get("/admin/logs/audit-logs", params=params)

def get_user_transaction_logs(user_id: int, action_type=None,
                               from_date=None, to_date=None):
    params = {}
    if action_type: params["action_type"] = action_type
    if from_date:   params["from_date"]   = from_date
    if to_date:     params["to_date"]     = to_date
    return _get(f"/admin/users/{user_id}/logs/transactions", params=params)

def get_user_audit_logs(user_id: int, event_type=None,
                         from_date=None, to_date=None):
    params = {}
    if event_type: params["event_type"] = event_type
    if from_date:  params["from_date"]  = from_date
    if to_date:    params["to_date"]    = to_date
    return _get(f"/admin/users/{user_id}/logs/audit", params=params)

# ── at the very bottom of utils/api.py ──

def _put(endpoint: str, data: dict = None):
    try:
        r = requests.put(
            f"{BASE_URL}{endpoint}",
            headers=_headers(), json=data, timeout=10
        )
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to server.")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ API Error {e.response.status_code}: {e.response.text}")
        return None
    except Exception as e:
        st.error(f"❌ Error: {e}")
        return None


def _delete(endpoint: str):
    try:
        r = requests.delete(
            f"{BASE_URL}{endpoint}",
            headers=_headers(), timeout=10
        )
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to server.")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ API Error {e.response.status_code}: {e.response.text}")
        return None
    except Exception as e:
        st.error(f"❌ Error: {e}")
        return None