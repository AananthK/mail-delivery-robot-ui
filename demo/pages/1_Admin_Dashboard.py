import streamlit as st
import demo.app_bootstrap

# Admin guard
if not st.session_state.get("is_logged_in") or st.session_state.get("role") != "admin":
    st.error("Admin access only. Please log in.")
    st.switch_page("streamlit_app.py")

st.set_page_config(page_title="Admin Dashboard", layout="wide")
st.title("🛠️ Admin Dashboard")

user_id = st.session_state.get("user_id")
st.caption(f"Logged in as admin (user_id: {user_id})")

c1, c2, c3 = st.columns(3)

with c1:
    if st.button("➕ Create User", use_container_width=True):
        st.switch_page("pages/2_Create_User.py")

with c2:
    if st.button("📦 Create Delivery", use_container_width=True):
        st.switch_page("pages/3_Create_Delivery.py")

with c3:
    if st.button("📄 View Deliveries", use_container_width=True):
        st.switch_page("pages/4_View_Deliveries.py")

st.divider()

if st.button("🚪 Logout"):
    # logs user out
    st.session_state.clear()
    # back to log-in page
    st.switch_page("streamlit_app.py")
