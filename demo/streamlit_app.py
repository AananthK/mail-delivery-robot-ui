import streamlit as st
import app_bootstrap

st.set_page_config(
    page_title="Mail Delivery Robot Demo",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------- Public pages ----------
login_page = st.Page("login.py", title="Login", default=True)

# ---------- Admin pages ----------
admin_dashboard = st.Page("admin/admin_dashboard.py", title="Admin Dashboard", default=True)
admin_user_mgmt = st.Page("admin/admin_user_mgmt.py", title="User Management")
admin_robot_mgmt = st.Page("admin/admin_robot_mgmt.py", title="Robot Management")
admin_delivery_mgmt = st.Page("admin/admin_delivery_mgmt.py", title="Delivery Management")
admin_account_settings = st.Page("admin/admin_account_settings.py", title="My Account")

# User Management
admin_create_user = st.Page("admin/user_mgmt_pages/admin_create_user.py", title="Create User")
admin_view_user = st.Page("admin/user_mgmt_pages/admin_view_user.py", title="View Users")
admin_edit_user = st.Page("admin/user_mgmt_pages/admin_edit_user.py", title="Edit User")

# Delivery Management
admin_create_delivery = st.Page("admin/delivery_mgmt_pages/admin_create_delivery.py", title="Create Delivery")
admin_view_delivery = st.Page("admin/delivery_mgmt_pages/admin_view_delivery.py", title="View Deliveries")
admin_edit_delivery = st.Page("admin/delivery_mgmt_pages/admin_edit_delivery.py", title="Edit Delivery")

# Robot Management
admin_view_robot = st.Page("admin/robot_mgmt_pages/admin_view_robot.py", title="View Robots")

# ---------- User pages ----------
user_dashboard = st.Page("user/user_dashboard.py", title="User Dashboard", default=True)
user_delivery_mgmt = st.Page("user/user_delivery_mgmt.py", title="My Deliveries")
user_account_mgmt = st.Page("user/user_account_mgmt.py", title="My Account")

# Delivery Management
user_view_delivery = st.Page("user/delivery_mgmt_pages/user_view_delivery.py", title="View Deliveries")
user_edit_delivery = st.Page("user/delivery_mgmt_pages/user_edit_delivery.py", title="Edit Delivery")

# ---------- Role-based navigation ----------
if not st.session_state.get("is_logged_in"):
    pg = st.navigation(
        [login_page],
        position="hidden"
    )
elif st.session_state.get("role") == "admin":
    pg = st.navigation(
        [
            admin_dashboard,
            admin_user_mgmt,
            admin_robot_mgmt,
            admin_delivery_mgmt,
            admin_account_settings,
            admin_create_user,
            admin_view_user,
            admin_edit_user,
            admin_view_robot,
            admin_create_delivery,
            admin_view_delivery,
            admin_edit_delivery,
        ],
        position="hidden"
    )
else:
    pg = st.navigation(
        [
            user_dashboard,
            user_delivery_mgmt,
            user_account_mgmt,
            user_view_delivery,
            user_edit_delivery,
        ],
        position="hidden"
    )

pg.run()