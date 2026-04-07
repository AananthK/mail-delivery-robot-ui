import streamlit as st
import app_bootstrap

from backend.src.services.admin_service import (
    admin_view_all_robots,
    admin_view_robot_by_id,
    admin_view_robots_by_current_room,
    admin_view_robots_by_next_room
)

# Admin guard
if not st.session_state.get("is_logged_in") or st.session_state.get("role") != "admin":
    st.error("Admin access only. Please log in.")
    st.page_link("login.py", label="Go to Login")
    st.stop()

st.title("📄 Admin View Robots")

admin_id = st.session_state.get("user_id")
st.caption(f"Admin ID: {admin_id}")

# Session state for filter visibility
if "show_robot_filter" not in st.session_state:
    st.session_state.show_robot_filter = False

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
        st.session_state.show_robot_filter = not st.session_state.show_robot_filter
        st.rerun()

with col3:
    st.page_link(
        "admin/admin_dashboard.py",
        label="⬅️ Back to Admin Dashboard",
        use_container_width=True
    )

st.divider()

try:
    robots = []

    if st.session_state.show_robot_filter:
        st.subheader("Filter robots")

        filter_type = st.radio(
            "Select one filter type:",
            options=["id", "current_room", "next_room"],
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
            st.session_state.show_robot_filter = False
            st.rerun()

        if apply_filter:
            if not search_value.strip():
                st.warning("Please enter a value to search.")
            else:
                if filter_type == "id":
                    try:
                        robots = admin_view_robot_by_id(
                            admin_id=admin_id,
                            r_id=int(search_value.strip())
                        )
                        robots = [robots] if robots else []
                    except ValueError:
                        st.error("Robot ID must be an integer.")
                        robots = []

                elif filter_type == "current_room":
                    robots = admin_view_robots_by_current_room(
                        admin_id=admin_id,
                        current_room=search_value.strip()
                    )

                elif filter_type == "next_room":
                    robots = admin_view_robots_by_next_room(
                        admin_id=admin_id,
                        next_room=search_value.strip()
                    )

        else:
            robots = admin_view_all_robots(admin_id=admin_id)

    else:
        robots = admin_view_all_robots(admin_id=admin_id)

    if not robots:
        st.info("No matching robots found.")
    else:
        normalized = []
        for r in robots:
            if hasattr(r, "model_dump"):
                normalized.append(r.model_dump())
            elif isinstance(r, dict):
                normalized.append(r)
            else:
                normalized.append({"value": str(r)})

        st.dataframe(normalized, use_container_width=True)

except Exception as e:
    st.error(str(e))