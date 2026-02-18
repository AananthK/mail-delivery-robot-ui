import streamlit as st
import demo.app_bootstrap

from backend.src.services.delivery_service import get_deliveries_by_recipient

# User guard
if not st.session_state.get("is_logged_in") or st.session_state.get("role") != "user":
    st.error("User access only. Please log in.")
    st.switch_page("streamlit_app.py")

st.set_page_config(page_title="My Deliveries", layout="wide")
st.title("📦 My Deliveries")

r_id = int(st.session_state.get("user_id"))
st.caption(f"Recipient (user) ID: {r_id}")

# Default quick view; toggle for full view
full_view = st.toggle("Full View", value=False)
m_type = "full_view" if full_view else "quick_view"
st.write(f"Showing: **{m_type}**")

col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    if st.button("🔄 Refresh"):
        st.rerun()

with col2:
    if st.button("⬅️ Back"):
        st.switch_page("pages/5_User_Dashboard.py")

st.divider()

try:
    deliveries = get_deliveries_by_recipient(m_type=m_type, r_id=r_id)

    if not deliveries:
        st.info("No deliveries found.")
    else:
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
