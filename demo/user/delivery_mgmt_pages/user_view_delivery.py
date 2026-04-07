import streamlit as st
import app_bootstrap

from datetime import date, datetime, time

from backend.src.services.user_service import (
    user_view_deliveries,
    user_view_delivery_by_id,
    user_view_deliveries_by_admin,
    user_view_deliveries_by_sender,
    user_view_deliveries_by_date,
    user_view_deliveries_by_room
    
)

# User guard
if not st.session_state.get("is_logged_in") or st.session_state.get("role") != "user":
    st.error("User access only. Please log in.")
    st.page_link("login.py", label="Go to Login")
    st.stop()

st.title("🔎 View Deliveries")

user_id = st.session_state.get("user_id")
st.caption(f"User ID: {user_id}")

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
        "user/user_delivery_mgmt.py",
        label="⬅️ Back to Delivery Management",
        use_container_width=True
    )

st.divider()

try:
    deliveries = []

    if st.session_state.show_user_filter:
        st.subheader("Filter Deliveries")

        filter_type = st.radio(
            "Select one filter type:",
            options=["id", "admin", "sender", "date", "room"],
            horizontal=True
        )

        input_col1, input_col2 = st.columns([1, 3])

        with input_col1:
            st.markdown(f"**Filter by:** `{filter_type}`")

        with input_col2:
            if filter_type == "date":
                search_value = st.date_input("Date", value=date.today())
            else:
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
            is_empty_text = filter_type != "date" and not str(search_value).strip()

            if is_empty_text:
                st.warning("Please enter a value to search.")
            else:
                if filter_type == "id":
                    try:
                        delivery = user_view_delivery_by_id(
                            m_type=m_type,
                            user_id=user_id,
                            d_id=int(search_value.strip())
                        )
                        deliveries = [delivery] if delivery else []
                    except ValueError:
                        st.error("Delivery ID must be a number.")
                        deliveries = []

                elif filter_type == "admin":
                    delivery = user_view_deliveries_by_admin(
                        m_type=m_type,
                        user_id=user_id,
                        admin_id=search_value.strip()
                    )

                elif filter_type == "sender":
                    deliveries = user_view_deliveries_by_sender(
                        m_type=m_type,
                        user_id=user_id,
                        sender=search_value.strip()
                    )

                elif filter_type == "date":
                    selected_datetime = datetime.combine(search_value, time.min)
                    deliveries = user_view_deliveries_by_date(
                        m_type=m_type,
                        user_id=user_id,
                        day=selected_datetime
                    )

                elif filter_type == "room":
                    deliveries = user_view_deliveries_by_room(
                        m_type=m_type,
                        user_id=user_id,
                        room=search_value.strip()
                    )

        else:
            deliveries = user_view_deliveries(m_type = m_type, user_id=user_id)

    else:
        deliveries = user_view_deliveries(m_type = m_type, user_id=user_id)

    if not deliveries:
        st.info("No matching deliveries found.")
    else:
        normalized = []
        for u in deliveries:
            if hasattr(u, "model_dump"):
                normalized.append(u.model_dump())
            elif isinstance(u, dict):
                normalized.append(u)
            else:
                normalized.append({"value": str(u)})

        st.dataframe(normalized, use_container_width=True)

except Exception as e:
    st.error(str(e))