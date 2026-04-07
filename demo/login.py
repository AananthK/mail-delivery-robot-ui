import streamlit as st
import app_bootstrap

from backend.src.services.auth_service import user_login

st.title("Mail Robot Delivery Demo")
st.subheader("Login")

uname = st.text_input("Username")
pword = st.text_input("Password", type="password")

if st.button("Login"):
    if not uname or not pword:
        st.warning("Please enter both username and password.")
    else:
        try:
            user = user_login(username=uname, password=pword)

            # Store login state
            st.session_state["is_logged_in"] = True
            st.session_state["user_id"] = user.user_id
            st.session_state["role"] = user.user_role
            st.session_state["first_name"] = user.first_name
            st.session_state["last_name"] = user.last_name
            st.session_state["username"] = user.username
            st.session_state["email"] = user.email
            st.session_state["phone_number"] = user.phone_number

            st.rerun()

        except Exception as e:
            st.error(str(e))