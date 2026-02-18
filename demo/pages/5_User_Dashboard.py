import streamlit as st
import demo.app_bootstrap

# User guard
if not st.session_state.get("is_logged_in") or st.session_state.get("role") != "user":
    st.error("User access only. Please log in.")
    st.switch_page("streamlit_app.py")

st.set_page_config(page_title="User Dashboard", layout="wide")
st.title("👤 User Dashboard")

st.caption(
    f"Logged in as: {st.session_state.get('first_name')} {st.session_state.get('last_name')} "
    f"(user_id: {st.session_state.get('user_id')})"
)

c1, c2 = st.columns([2, 1])

with c1:
    if st.button("📦 View My Deliveries", use_container_width=True):
        st.switch_page("pages/6_User_View_Deliveries.py")

with c2:
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()
        st.switch_page("streamlit_app.py")
