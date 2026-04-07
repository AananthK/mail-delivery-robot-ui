import streamlit as st
import app_bootstrap

# Admin guard
if not st.session_state.get("is_logged_in") or st.session_state.get("role") != "admin":
    st.error("Admin access only. Please log in.")
    st.page_link("login.py", label="Go to Login")
    st.stop()

st.title("📬 Admin Delivery Management")

user_id = st.session_state.get("user_id")
first_name = st.session_state.get("first_name", "")
st.caption(f"Logged in as admin: {first_name} (user_id: {user_id})")

c1, c2, c3 = st.columns(3)

with c1:
    st.page_link(
        "admin/delivery_mgmt_pages/admin_create_delivery.py",
        label="📨 Create Delivery",
        use_container_width=True
    )

with c2:
    st.page_link(
        "admin/delivery_mgmt_pages/admin_view_delivery.py",
        label="🔎 View Deliveries",
        use_container_width=True
    )

with c3:
    st.page_link(
        "admin/delivery_mgmt_pages/admin_edit_delivery.py",
        label="📝 Edit Deliveries",
        use_container_width=True
    )

st.divider()

st.page_link(
    "admin/admin_dashboard.py",
    label="⬅️ Back to Dashboard",
    use_container_width=False
)