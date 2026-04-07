import streamlit as st
import app_bootstrap

# Admin guard
if not st.session_state.get("is_logged_in") or st.session_state.get("role") != "admin":
    st.error("Admin access only. Please log in.")
    st.page_link("login.py", label="Go to Login")
    st.stop()

st.title("🛠️ Admin Dashboard")

user_id = st.session_state.get("user_id")
first_name = st.session_state.get("first_name", "")
st.caption(f"Logged in as admin: {first_name} (user_id: {user_id})")

c1, c2 = st.columns(2)

with c1:
    with st.container(border=True):
        st.subheader(f"{st.session_state.get('first_name', '')} "
                f"{st.session_state.get('last_name', '')}")
        st.divider()

        st.write(f"**Username:** {st.session_state.get('username', '')}")
        st.write(f"**Role:** {st.session_state.get('role', '')}")
        st.write(f"**Email:** {st.session_state.get('email', '')}")
        st.write(f"**Phone Number:** {st.session_state.get('phone_number', '')}")

with c2:
    with st.container(border=True):
        st.subheader("Actions")

        st.divider()

        st.page_link(
            "admin/admin_user_mgmt.py",
            label="👤 User Management",
            use_container_width=True
        )

        st.page_link(
            "admin/admin_delivery_mgmt.py",
            label="📦 Delivery Management",
            use_container_width=True
        )

        st.page_link(
            "admin/robot_mgmt_pages/admin_view_robot.py",
            label="🤖 Robot Management",
            use_container_width=True
        )

        st.page_link(
            "admin/admin_account_settings.py",
            label="👨‍💻👩‍💻 My Account",
            use_container_width=True
            )

st.divider()

if st.button("🚪 Logout"):
    keys_to_clear = [
        "is_logged_in",
        "user_id",
        "role",
        "first_name",
        "last_name",
        "username",
        "email",
        "phone_number",
    ]
    for key in keys_to_clear:
        st.session_state.pop(key, None)

    st.rerun()