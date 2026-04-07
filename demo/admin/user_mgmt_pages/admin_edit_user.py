import streamlit as st
import app_bootstrap

from backend.src.services.admin_service import get_user_by_id, admin_update_user_password, admin_delete_user
# Add these when your service methods exist:
# from backend.src.services.admin_service import admin_change_user_password, admin_delete_user

# ---------------- PAGE GUARD ----------------

if not st.session_state.get("is_logged_in") or st.session_state.get("role") != "admin":
    st.error("Admin access only. Please log in.")
    st.page_link("login.py", label="Go to Login")
    st.stop()

st.title("📄 Admin Edit Users")

admin_id = st.session_state.get("user_id")
st.caption(f"Admin ID: {admin_id}")

# ---------------- DIALOGS ----------------

@st.dialog("Confirm Password Change")
def confirm_password_change_dialog():
    st.warning("You are about to change this user's password.")
    st.write("This action will immediately replace the user's current password.")

    c1, c2 = st.columns(2)

    with c1:
        if st.button("Cancel", use_container_width=True):
            st.session_state["show_change_password"] = True
            st.rerun()

    with c2:
        if st.button("Confirm Password Change", use_container_width=True):
            try:
                target_user_id = st.session_state.get("selected_user_id")
                new_password = st.session_state.get("pending_new_password")

                admin_update_user_password(admin_id = admin_id, user_id= target_user_id, new_pword=new_password)

                st.session_state["show_change_password"] = False
                st.session_state["pending_new_password"] = None
                st.session_state["password_change_success"] = "Password changed successfully."
                st.rerun()

            except Exception as e:
                st.error(str(e))


@st.dialog("Confirm Account Deletion")
def confirm_delete_account_dialog():
    st.error("This action will permanently delete the selected user account.")
    st.write("This cannot be undone.")

    c1, c2 = st.columns(2)

    with c1:
        if st.button("Cancel", use_container_width=True):
            st.session_state["show_delete_account"] = True
            st.rerun()

    with c2:
        if st.button("Confirm Delete", use_container_width=True):
            try:
                target_user_id = st.session_state.get("selected_user_id")

                admin_delete_user(admin_id=admin_id, user_id=target_user_id)

                st.session_state["selected_user"] = None
                st.session_state["selected_user_id"] = None
                st.session_state["show_delete_account"] = False
                st.session_state["delete_success"] = "User account deleted successfully."
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

if "show_delete_account" not in st.session_state:
    st.session_state["show_delete_account"] = False

if "pending_new_password" not in st.session_state:
    st.session_state["pending_new_password"] = None

if "password_change_success" not in st.session_state:
    st.session_state["password_change_success"] = None

if "delete_success" not in st.session_state:
    st.session_state["delete_success"] = None

# ---------------- TOP ACTIONS ----------------

col1, col2 = st.columns([1, 1])

with col1:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

with col2:
    st.page_link(
        "admin/admin_user_mgmt.py",
        label="⬅️ Back to User Management",
        use_container_width=True
    )

st.divider()

# ---------------- SEARCH ----------------

st.subheader("Find User by ID")

with st.form("find_user_form"):
    search_value = st.text_input(
        "User ID",
        placeholder="Enter user ID..."
    )
    search_submitted = st.form_submit_button("Find User")

if search_submitted:
    if not search_value.strip():
        st.warning("Please enter a user ID.")
    else:
        try:
            user = get_user_by_id(
                admin_id=admin_id,
                user_id=int(search_value.strip())
            )

            if user:
                if hasattr(user, "model_dump"):
                    user_data = user.model_dump()
                elif isinstance(user, dict):
                    user_data = user
                else:
                    user_data = {
                        "value": str(user)
                    }

                st.session_state["selected_user"] = user_data
                st.session_state["selected_user_id"] = user_data.get("user_id")
                st.session_state["show_change_password"] = False
                st.session_state["show_delete_account"] = False
            else:
                st.session_state["selected_user"] = None
                st.session_state["selected_user_id"] = None
                st.info("No user found with that ID.")

        except ValueError:
            st.error("User ID must be a number.")
        except Exception as e:
            st.error(str(e))

# ---------------- SUCCESS MESSAGES ----------------

if st.session_state.get("password_change_success"):
    st.success(st.session_state["password_change_success"])
    st.session_state["password_change_success"] = None

if st.session_state.get("delete_success"):
    st.success(st.session_state["delete_success"])
    st.session_state["delete_success"] = None

# ---------------- USER BLOCK ----------------

selected_user = st.session_state.get("selected_user")

if selected_user:
    st.divider()
    st.subheader("User Details")

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
            st.session_state["show_delete_account"] = False
            st.rerun()

    with a2:
        if st.button("🗑️ Delete Account", use_container_width=True):
            st.session_state["show_delete_account"] = True
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

    # ------------ DELETE ACCOUNT FORM ------------

    if st.session_state.get("show_delete_account"):
        st.divider()
        st.subheader("Delete Account")

        with st.form("delete_account_form"):
            st.warning("Deleting this account is permanent.")
            delete_phrase = st.text_input('Type "DELETE" to continue')

            d1, d2 = st.columns(2)
            with d1:
                back_delete = st.form_submit_button("Back")
            with d2:
                confirm_delete_btn = st.form_submit_button("Confirm")

        if back_delete:
            st.session_state["show_delete_account"] = False
            st.rerun()

        if confirm_delete_btn:
            if delete_phrase.strip() != "DELETE":
                st.error('You must type "DELETE" exactly to continue.')
            else:
                confirm_delete_account_dialog()