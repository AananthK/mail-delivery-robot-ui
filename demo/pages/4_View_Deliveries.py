import streamlit as st
import demo.app_bootstrap

from backend.src.services.account_service import admin_view_deliveries

# Admin guard
if not st.session_state.get("is_logged_in") or st.session_state.get("role") != "admin":
    st.error("Admin access only. Please log in.")
    st.switch_page("streamlit_app.py")

st.set_page_config(page_title="View Deliveries", layout="wide")
st.title("📄 View Deliveries")

admin_id = st.session_state.get("user_id")
st.caption(f"Admin ID: {admin_id}")

# Toggle between quick and full view
full_view = st.toggle("Full View", value=False)
m_type = "full_view" if full_view else "quick_view"
st.write(f"Showing: **{m_type}**")

col1, col2 = st.columns([1, 1])
with col1:
    if st.button("🔄 Refresh"):
        st.rerun()
with col2:
    if st.button("⬅️ Back to Dashboard"):
        st.switch_page("pages/1_Admin_Dashboard.py")

st.divider()

try:
    deliveries = admin_view_deliveries(admin_id=int(admin_id), m_type=m_type)

    if not deliveries:
        st.info("No deliveries found for this admin.")
    else:
        # normalize list elements to dicts if they are models
        normalized = []
        for d in deliveries:
            if hasattr(d, "model_dump"):
                normalized.append(d.model_dump())
            elif isinstance(d, dict):
                normalized.append(d)
            else:
                normalized.append({"value": str(d)})

        st.dataframe(normalized, use_container_width=True)

except Exception as e:
    st.error(str(e))
