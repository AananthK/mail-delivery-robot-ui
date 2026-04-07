import streamlit as st
import app_bootstrap

from backend.src.services.admin_service import admin_update_password, admin_update_email, admin_update_phone, admin_view_account

# ---------------- PAGE GUARD ----------------

if not st.session_state.get("is_logged_in") or st.session_state.get("role") != "admin":
    st.error("Admin access only. Please log in.")
    st.page_link("login.py", label="Go to Login")
    st.stop()

st.title("📄 Admin Settings")

admin_id = st.session_state.get("user_id")
st.caption(f"Admin ID: {admin_id}")

# ---------------- DIALOGS ----------------

@st.dialog("Confirm Password Change")
def confirm_password_change_dialog():
    st.warning("You are about to change your password.")
    st.write("This action will immediately replace your current password.")

    c1, c2 = st.columns(2)

    with c1:
        if st.button("Cancel", use_container_width=True):
            st.session_state["show_change_password"] = True
            st.rerun()

    with c2:
        if st.button("Confirm Password Change", use_container_width=True):
            try:
                target_user_id = admin_id
                new_password = st.session_state.get("pending_new_password")

                admin_update_password(admin_id = target_user_id, new_pword = new_password)

                st.session_state["show_change_password"] = False
                st.session_state["pending_new_password"] = None
                st.session_state["password_change_success"] = "Password changed successfully."
                st.rerun()

            except Exception as e:
                st.error(str(e))


@st.dialog("Confirm Contact Information Changes")
def confirm_contact_change_dialog(email: str, phone_number: str):
    st.error("You are about to change your contact information")
    st.write("This action will update the email and/or phone number associated with your account")

    c1, c2 = st.columns(2)

    with c1:
        if st.button("Cancel", use_container_width=True):
            st.session_state["show_change_contact_info"] = True
            st.rerun()

    with c2:
        if st.button("Confirm Change", use_container_width=True):
            try:
                target_user_id = admin_id

                if email is not None and email != "":
                    admin_update_email(admin_id = target_user_id, u_email = email)

                if phone_number is not None and phone_number != "":
                    admin_update_phone(admin_id = target_user_id, u_phone = phone_number)

                updated_account = admin_view_account(admin_id = st.session_state.get("user_id"))

                st.session_state["email"] = updated_account.email
                st.session_state["phone_number"] = updated_account.phone_number

                st.session_state["selected_user"] = None
                st.session_state["selected_user_id"] = None
                st.session_state["show_change_contact_info"] = False
                st.session_state["pending_new_email"] = None
                st.session_state["pending_new_phone"] = None
                st.session_state["change_contact_info_success"] = "Contact information updated successfully."
                st.rerun()

            except Exception as e:
                st.error(str(e))

# ---------------- SESSION STATE ----------------

if "selected_user" not in st.session_state:
    st.session_state["selected_user"] = None

if "selected_user_id" not in st.session_state:
    st.session_state["selected_user_id"] = None

if "show_change_password" not in st.session_state:
    st.session_state["show_change_password"] = False

if "show_change_contact_info" not in st.session_state:
    st.session_state["show_change_contact_info"] = False

if "pending_new_password" not in st.session_state:
    st.session_state["pending_new_password"] = None

if "pending_new_email" not in st.session_state:
    st.session_state["pending_new_email"] = None

if "pending_new_phone" not in st.session_state:
    st.session_state["pending_new_phone"] = None

if "password_change_success" not in st.session_state:
    st.session_state["password_change_success"] = None

if "change_contact_info_success" not in st.session_state:
    st.session_state["change_contact_info_success"] = None

# ---------------- TOP ACTIONS ----------------

col1, col2 = st.columns([1, 1])

with col1:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

with col2:
    st.page_link(
        "admin/admin_dashboard.py",
        label="⬅️ Back to Admin Dashboard",
        use_container_width=True
    )

st.divider()

# ---------------- SUCCESS MESSAGES ----------------

if st.session_state.get("password_change_success"):
    st.success(st.session_state["password_change_success"])
    st.session_state["password_change_success"] = None

if st.session_state.get("change_contact_info_success"):
    st.success(st.session_state["change_contact_info_success"])
    st.session_state["change_contact_info_success"] = None

# ---------------- ADMIN BLOCK ----------------

selected_user = {
    "user_id": st.session_state.get("user_id"),
    "first_name": st.session_state.get("first_name"),
    "last_name": st.session_state.get("last_name"),
    "username": st.session_state.get("username"),
    "email": st.session_state.get("email"),
    "phone_number": st.session_state.get("phone_number"),
    "role": st.session_state.get("role"),
}

if selected_user:
    st.divider()
    st.subheader("Admin Details")

    with st.container(border=True):
        c1, c2 = st.columns(2)

        with c1:
            st.write(f"**User ID:** {selected_user.get('user_id', '')}")
            st.write(f"**First Name:** {selected_user.get('first_name', '')}")
            st.write(f"**Last Name:** {selected_user.get('last_name', '')}")

        with c2:
            st.write(f"**Username:** {selected_user.get('username', '')}")
            st.write(f"**Email:** {selected_user.get('email', '')}")
            st.write(f"**Phone Number:** {selected_user.get('phone_number', '')}")

    st.markdown("### Account Actions")

    a1, a2 = st.columns(2)

    with a1:
        if st.button("🔐 Change Password", use_container_width=True):
            st.session_state["show_change_password"] = True
            st.session_state["show_change_contact_info"] = False
            st.rerun()

    with a2:
        if st.button("📲 Change Account Contact Information", use_container_width=True):
            st.session_state["show_change_contact_info"] = True
            st.session_state["show_change_password"] = False
            st.rerun()

    # ------------ CHANGE PASSWORD FORM ------------

    if st.session_state.get("show_change_password"):
        st.divider()
        st.subheader("Change Password")

        with st.form("change_password_form"):
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")

            b1, b2 = st.columns(2)
            with b1:
                back_password = st.form_submit_button("Back")
            with b2:
                confirm_password_btn = st.form_submit_button("Confirm")

        if back_password:
            st.session_state["show_change_password"] = False
            st.rerun()

        if confirm_password_btn:
            if not new_password or not confirm_password:
                st.warning("Please fill in both password fields.")
            elif new_password != confirm_password:
                st.error("Passwords do not match.")
            else:
                st.session_state["pending_new_password"] = new_password
                confirm_password_change_dialog()

    # ------------ CHANGE CONTACT INFO FORM ------------

    if st.session_state.get("show_change_contact_info"):
        st.divider()
        st.subheader("Change Contact Information")

        with st.form("contact_info_form"):
            new_email = st.text_input("New Email").strip()
            new_phone = st.text_input("New Phone Number").strip()

            b1, b2 = st.columns(2)
            with b1:
                back_change = st.form_submit_button("Back")
            with b2:
                confirm_change_btn = st.form_submit_button("Confirm")

        if back_change:
            st.session_state["show_change_contact_info"] = False
            st.rerun()

        if confirm_change_btn:
            if not new_email and not new_phone:
                st.warning("Please fill at least one field")
            else:
                st.session_state["pending_new_email"] = new_email
                st.session_state['pending_new_phone'] = new_phone
                confirm_contact_change_dialog(email = new_email, phone_number = new_phone)