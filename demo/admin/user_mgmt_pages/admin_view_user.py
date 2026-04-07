import streamlit as st
import app_bootstrap

from backend.src.services.admin_service import (
    get_all_users,
    get_user_by_id,
    get_user_by_username,
    get_user_by_name
)

# Admin guard
if not st.session_state.get("is_logged_in") or st.session_state.get("role") != "admin":
    st.error("Admin access only. Please log in.")
    st.page_link("login.py", label="Go to Login")
    st.stop()

st.title("📄 Admin View Users")

admin_id = st.session_state.get("user_id")
st.caption(f"Admin ID: {admin_id}")

# Session state for filter visibility
if "show_user_filter" not in st.session_state:
    st.session_state.show_user_filter = False

# Toggle between quick and full view
full_view = st.toggle("Full View", value=False)
m_type = "full_view" if full_view else "quick_view"
st.write(f"Showing: **{m_type}**")

col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button("🔄 Refresh"):
        st.rerun()

with col2:
    if st.button("🧰 Filter"):
        st.session_state.show_user_filter = not st.session_state.show_user_filter
        st.rerun()

with col3:
    st.page_link(
        "admin/admin_user_mgmt.py",
        label="⬅️ Back to User Management",
        use_container_width=True
    )

st.divider()

try:
    users = []

    if st.session_state.show_user_filter:
        st.subheader("Filter Users")

        filter_type = st.radio(
            "Select one filter type:",
            options=["id", "name", "username"],
            horizontal=True
        )

        input_col1, input_col2 = st.columns([1, 3])

        with input_col1:
            st.markdown(f"**Filter by:** `{filter_type}`")

        with input_col2:
            search_value = st.text_input(
                "Search value",
                label_visibility="collapsed",
                placeholder=f"Enter {filter_type}..."
            )

        action_col1, action_col2 = st.columns([1, 1])

        with action_col1:
            apply_filter = st.button("Apply Filter")

        with action_col2:
            clear_filter = st.button("Clear Filter")

        if clear_filter:
            st.session_state.show_user_filter = False
            st.rerun()

        if apply_filter:
            if not search_value.strip():
                st.warning("Please enter a value to search.")
            else:
                if filter_type == "id":
                    try:
                        user = get_user_by_id(
                            admin_id=admin_id,
                            user_id=int(search_value.strip())
                        )
                        users = [user] if user else []
                    except ValueError:
                        st.error("User ID must be a number.")
                        users = []

                elif filter_type == "username":
                    user = get_user_by_username(
                        admin_id=admin_id,
                        username=search_value.strip()
                    )
                    users = [user] if user else []

                elif filter_type == "name":
                    users = get_user_by_name(
                        admin_id=admin_id,
                        name=search_value.strip()
                    )

        else:
            users = get_all_users(admin_id=admin_id)

    else:
        users = get_all_users(admin_id=admin_id)

    if not users:
        st.info("No matching users found.")
    else:
        normalized = []
        for u in users:
            if hasattr(u, "model_dump"):
                normalized.append(u.model_dump())
            elif isinstance(u, dict):
                normalized.append(u)
            else:
                normalized.append({"value": str(u)})

        st.dataframe(normalized, use_container_width=True)

except Exception as e:
    st.error(str(e))