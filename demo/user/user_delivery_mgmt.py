import streamlit as st
import app_bootstrap

# Admin guard
if not st.session_state.get("is_logged_in") or st.session_state.get("role") != "user":
    st.error("User access only. Please log in.")
    st.page_link("login.py", label="Go to Login")
    st.stop()

st.title("📬 User Delivery Management")

user_id = st.session_state.get("user_id")
first_name = st.session_state.get("first_name", "")
st.caption(f"Logged in as admin: {first_name} (user_id: {user_id})")

c1, c2 = st.columns(2)

with c1:
    st.page_link(
        "user/delivery_mgmt_pages/user_view_delivery.py",
        label="🔎 View Deliveries",
        use_container_width=True
    )

with c2:
    st.page_link(
        "user/delivery_mgmt_pages/user_edit_delivery.py",
        label="📝 Edit Deliveries",
        use_container_width=True
    )

st.divider()

st.page_link(
    "user/user_dashboard.py",
    label="⬅️ Back to Dashboard",
    use_container_width=False
)