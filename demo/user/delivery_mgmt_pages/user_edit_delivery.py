import streamlit as st
import app_bootstrap

from datetime import datetime, date, time

from backend.src.services.user_service import (
    user_view_delivery_by_id,
    user_change_delivery_room,
    user_change_delivery_time,
)

# ---------------- PAGE GUARD ----------------

if not st.session_state.get("is_logged_in") or st.session_state.get("role") != "user":
    st.error("User access only. Please log in.")
    st.page_link("login.py", label="Go to Login")
    st.stop()

st.title("📝 Edit Deliveries")

user_id = st.session_state.get("user_id")
st.caption(f"User ID: {user_id}")

# ---------------- SESSION STATE ----------------

defaults = {
    "selected_delivery": None,
    "selected_delivery_id": None,
    "show_change_room": False,
    "show_change_time": False,
    "pending_room": None,
    "pending_time": None,
    "delivery_update_success": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ---------------- DIALOGS ----------------

@st.dialog("Confirm Room Change")
def confirm_room_change_dialog():
    st.warning("You are about to change the delivery room.")
    st.write(f"New room: **{st.session_state.get('pending_room', '')}**")

    c1, c2 = st.columns(2)

    with c1:
        if st.button("Cancel", use_container_width=True, key="cancel_room_change"):
            st.rerun()

    with c2:
        if st.button("Confirm", use_container_width=True, key="confirm_room_change"):
            try:
                updated = user_change_delivery_room(
                    user_id=st.session_state.get("user_id"),
                    d_id=st.session_state.get("selected_delivery_id"),
                    room=st.session_state.get("pending_room")
                )

                if hasattr(updated, "model_dump"):
                    st.session_state["selected_delivery"] = updated.model_dump()
                elif isinstance(updated, dict):
                    st.session_state["selected_delivery"] = updated

                st.session_state["show_change_room"] = False
                st.session_state["pending_room"] = None
                st.session_state["delivery_update_success"] = "Delivery room updated successfully."
                st.rerun()

            except Exception as e:
                st.error(str(e))


@st.dialog("Confirm Delivery Time Change")
def confirm_time_change_dialog():
    st.warning("You are about to change the delivery time.")
    st.write(f"New time: **{st.session_state.get('pending_time', '')}**")

    c1, c2 = st.columns(2)

    with c1:
        if st.button("Cancel", use_container_width=True, key="cancel_time_change"):
            st.rerun()

    with c2:
        if st.button("Confirm", use_container_width=True, key="confirm_time_change"):
            try:
                updated = user_change_delivery_time(
                    user_id=st.session_state.get("user_id"),
                    d_id=st.session_state.get("selected_delivery_id"),
                    time=st.session_state.get("pending_time")
                )

                if hasattr(updated, "model_dump"):
                    st.session_state["selected_delivery"] = updated.model_dump()
                elif isinstance(updated, dict):
                    st.session_state["selected_delivery"] = updated

                st.session_state["show_change_time"] = False
                st.session_state["pending_time"] = None
                st.session_state["delivery_update_success"] = "Delivery time updated successfully."
                st.rerun()

            except Exception as e:
                st.error(str(e))

# ---------------- TOP ACTIONS ----------------

col1, col2 = st.columns([1, 1])

with col1:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

with col2:
    st.page_link(
        "user/user_delivery_mgmt.py",
        label="⬅️ Back to Delivery Management",
        use_container_width=True
    )

st.divider()

# ---------------- SEARCH ----------------

st.subheader("Find Delivery by ID")

with st.form("find_delivery_form"):
    search_value = st.text_input(
        "Delivery ID",
        placeholder="Enter delivery ID..."
    )
    search_submitted = st.form_submit_button("Find Delivery")

if search_submitted:
    if not search_value.strip():
        st.warning("Please enter a delivery ID.")
    else:
        try:
            delivery = user_view_delivery_by_id(
                m_type="full_view",
                user_id=user_id,
                d_id=int(search_value.strip())
            )

            if delivery:
                if hasattr(delivery, "model_dump"):
                    delivery_data = delivery.model_dump()
                elif isinstance(delivery, dict):
                    delivery_data = delivery
                else:
                    delivery_data = {"value": str(delivery)}

                st.session_state["selected_delivery"] = delivery_data
                st.session_state["selected_delivery_id"] = (
                    delivery_data.get("delivery_id")
                    or delivery_data.get("d_id")
                )
                st.session_state["show_change_room"] = False
                st.session_state["show_change_status"] = False
                st.session_state["show_change_time"] = False
            else:
                st.session_state["selected_delivery"] = None
                st.session_state["selected_delivery_id"] = None
                st.info("No delivery found with that ID.")

        except ValueError:
            st.error("Delivery ID must be a number.")
        except Exception as e:
            st.error(str(e))

# ---------------- SUCCESS MESSAGE ----------------

if st.session_state.get("delivery_update_success"):
    st.success(st.session_state["delivery_update_success"])
    st.session_state["delivery_update_success"] = None

# ---------------- DELIVERY BLOCK ----------------

selected_delivery = st.session_state.get("selected_delivery")

if selected_delivery:
    st.divider()
    st.subheader("Delivery Details")

    with st.container(border=True):
        c1, c2 = st.columns(2)

        with c1:
            st.write(f"**Delivery ID:** {selected_delivery.get('delivery_id', selected_delivery.get('d_id', ''))}")
            st.write(f"**Created At:** {selected_delivery.get('created_at', '')}")
            st.write(f"**Recipient ID:** {selected_delivery.get('recipient_id', '')}")
            st.write(f"**Status:** {selected_delivery.get('status', '')}")

        with c2:
            st.write(f"**Delivery Time:** {selected_delivery.get('delivery_time', '')}")
            st.write(f"**Assigned Robot:** {selected_delivery.get('assigned_robot', '')}")
            st.write(f"**Room Number:** {selected_delivery.get('room_number', '')}")
            st.write(f"**Last Updated:** {selected_delivery.get('last_updated_at', '')}")

    st.markdown("### Delivery Actions")

    a1, a2, a3 = st.columns(3)

    with a1:
        if st.button("📍 Change Room", use_container_width=True):
            st.session_state["show_change_room"] = True
            st.session_state["show_change_status"] = False
            st.session_state["show_change_time"] = False
            st.rerun()

    with a2:
        if st.button("📦 Change Status", use_container_width=True):
            st.session_state["show_change_status"] = True
            st.session_state["show_change_room"] = False
            st.session_state["show_change_time"] = False
            st.rerun()

    with a3:
        if st.button("🕒 Change Delivery Time", use_container_width=True):
            st.session_state["show_change_time"] = True
            st.session_state["show_change_room"] = False
            st.session_state["show_change_status"] = False
            st.rerun()

    # ------------ CHANGE ROOM FORM ------------

    if st.session_state.get("show_change_room"):
        st.divider()
        st.subheader("Change Room")

        with st.form("change_room_form"):
            new_room = st.text_input("New Room Number")

            b1, b2 = st.columns(2)
            with b1:
                back_room = st.form_submit_button("Back")
            with b2:
                confirm_room = st.form_submit_button("Confirm")

        if back_room:
            st.session_state["show_change_room"] = False
            st.rerun()

        if confirm_room:
            if not new_room.strip():
                st.warning("Please enter a room number.")
            else:
                st.session_state["pending_room"] = new_room.strip()
                confirm_room_change_dialog()

    # ------------ CHANGE DELIVERY TIME FORM ------------

    if st.session_state.get("show_change_time"):
        st.divider()
        st.subheader("Change Delivery Time")

        with st.form("change_time_form"):
            new_date = st.date_input("New Delivery Date", value=date.today())
            new_clock_time = st.time_input("New Delivery Time", value=time(9, 0))

            d1, d2 = st.columns(2)
            with d1:
                back_time = st.form_submit_button("Back")
            with d2:
                confirm_time = st.form_submit_button("Confirm")

        if back_time:
            st.session_state["show_change_time"] = False
            st.rerun()

        if confirm_time:
            combined_dt = datetime.combine(new_date, new_clock_time)
            st.session_state["pending_time"] = combined_dt
            confirm_time_change_dialog()