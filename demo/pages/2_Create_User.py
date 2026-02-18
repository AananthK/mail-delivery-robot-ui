import streamlit as st
import demo.app_bootstrap

from backend.src.services.account_service import create_user

# Admin guard
if not st.session_state.get("is_logged_in") or st.session_state.get("role") != "admin":
    st.error("Admin access only. Please log in.")
    st.switch_page("streamlit_app.py")

st.set_page_config(page_title="Create User", layout="wide")
st.title("➕ Create User")

with st.form("create_user_form"):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    email = st.text_input("Email")
    phone_number = st.text_input("Phone Number (optional)")

    submitted = st.form_submit_button("Create User")

if submitted:
    if not username or not password or not first_name or not last_name or not email:
        st.warning("Please fill in username, password, first/last name, and email.")
    else:
        try:
            result = create_user(
                admin_id = st.session_state.get("user_id"),
                uname=username,
                pword=password,
                fname=first_name,
                lname=last_name,
                e_mail=email,
                p_number=phone_number if phone_number else None
            )
            st.success("User created successfully!")
            # result might be dict or model:
            if hasattr(result, "model_dump"):
                st.json(result.model_dump())
            elif isinstance(result, dict):
                st.json(result)
            else:
                st.write(result)

        except Exception as e:
            st.error(str(e))

st.divider()
if st.button("⬅️ Back to Dashboard"):
    st.switch_page("pages/1_Admin_Dashboard.py")
