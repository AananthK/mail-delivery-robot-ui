import streamlit as st
import app_bootstrap
from backend.src.services.user_service import (
    user_view_ready_deliveries,
    user_confirm_presence,
    user_view_unloading_delivery,
    user_deny_delivery,
    user_unload_delivery,
    user_accept_delivery)
from backend.src.services.robot_service import (
    get_robot_by_id
)
# ------------------------------------------------------------
# NOTE:
# Do not worry about imports yet.
# Insert your own service/function imports where needed.
# Also insert your own dependent variable assignments where marked.
# ------------------------------------------------------------


# =========================
# Session-state initializer
# =========================
def init_global_modal_state():
    defaults = {
        # Presence modal
        "show_presence_modal": False,
        "presence_deliveries": [],              # list of deliveries for confirm presence
        "presence_handled_delivery_ids": [],

        # Pickup modal
        "show_pickup_modal": False,
        "pickup_step": 1,                       # 1=accept/deny, 2=enter pin, 3=final confirm
        "pickup_delivery": None,                # dict for current delivery
        "pickup_robot_id": None,
        "pickup_pin_input": "",
        "pickup_modal_handled_delivery_id": None,

        # Optional tracking
        "active_delivery_id": None,
    }

    # defaulting session state variables
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# =========================================
# Helpers to load state from backend / DB
# =========================================
def check_presence_modal_trigger():
    if not st.session_state.get("is_logged_in"):
        return

    if st.session_state.get("role") != "user":
        return

    user_id = st.session_state.get("user_id")
    if not user_id:
        return

    deliveries = user_view_ready_deliveries(user_id=user_id)

    if not deliveries:
        st.session_state["show_presence_modal"] = False
        st.session_state["presence_deliveries"] = []
        return

    handled_ids = set(st.session_state.get("presence_handled_delivery_ids", []))

    unhandled_deliveries = [
        delivery for delivery in deliveries
        if delivery.delivery_id not in handled_ids
    ]

    if unhandled_deliveries:
        st.session_state["presence_deliveries"] = unhandled_deliveries
        st.session_state["show_presence_modal"] = True
    else:
        st.session_state["presence_deliveries"] = []
        st.session_state["show_presence_modal"] = False

def check_pickup_modal_trigger():
    """
    Trigger Modal 2 if:
    - user is logged in
    - role is user
    - a delivery for this user is in unloading state
    - the robot for that delivery is idle

    Uses:
        user_view_delivery_by_id(user_id, d_id, m_type='quick_view')
        get_robot_by_id(robot_id).status

    IMPORTANT:
    This function needs a way to determine WHICH active delivery to inspect.
    You can do that by:
    - checking a current/pending delivery list for the user, OR
    - checking all relevant deliveries and finding one in unloading state, OR
    - using a backend helper that returns the active unloading delivery for the user
    """

    if not st.session_state.get("is_logged_in"):
        return

    if st.session_state.get("role") != "user":
        return

    user_id = st.session_state.get("user_id")
    if not user_id:
        return

    delivery = user_view_unloading_delivery(user_id = user_id)

    if not delivery:
        return

    delivery_id = delivery.delivery_id
    robot_id = delivery.assigned_robot

    # ------------------------------------------------------------
    # INSERT FUNCTION CALL:
    # delivery_quick = user_view_delivery_by_id(user_id, delivery_id, m_type='quick_view')
    # robot = get_robot_by_id(robot_id)
    # ------------------------------------------------------------
    robot = get_robot_by_id(robot_id = robot_id)

    # ------------------------------------------------------------
    # INSERT VARIABLE REFERENCES:
    # delivery_status = # insert variable reference from delivery_quick
    # robot_status    = # insert variable reference from robot
    # ------------------------------------------------------------
    delivery_status = delivery.status
    robot_status = robot.robot_status

    if delivery_status == "unloading" and robot_status == "idle":
        if st.session_state.get("pickup_modal_handled_delivery_id") != delivery_id:

            # Only initialize if this is a new active delivery
            if st.session_state.get("active_delivery_id") != delivery_id:
                st.session_state["pickup_step"] = 1
                st.session_state["pickup_pin_input"] = ""

            st.session_state["show_pickup_modal"] = True
            st.session_state["pickup_robot_id"] = robot_id
            st.session_state["active_delivery_id"] = delivery_id

            st.session_state["pickup_delivery"] = {
                "delivery_id": delivery_id,
                "admin_user_id": delivery.admin_user_id,
                "delivery_time": delivery.delivery_time,
                "sender_name": delivery.sender_name,
                "room_number": delivery.room_number
            }


# ======================
# Modal 1: Confirm Presence
# ======================
@st.dialog("Confirm Presence for Today's Deliveries")
def presence_modal():
    deliveries = st.session_state.get("presence_deliveries", [])
    user_id = st.session_state.get("user_id")

    st.write("Please confirm which deliveries you will be present to receive today.")

    if not deliveries:
        st.info("No deliveries to confirm.")
        if st.button("Close"):
            st.session_state["show_presence_modal"] = False
            st.rerun()
        return

    st.markdown("### Expected Deliveries")

    for delivery in deliveries:
        # ------------------------------------------------------------
        # INSERT VARIABLE REFERENCES:
        # delivery_id    = # insert variable reference
        # admin_user_id  = # insert variable reference
        # sender_name    = # insert variable reference
        # room_number    = # insert variable reference
        # ------------------------------------------------------------
        delivery_id = delivery.delivery_id      # insert variable reference
        admin_user_id = delivery.admin_user_id    # insert variable reference
        delivery_time = delivery.delivery_time.strftime("%Y-%m-%d %I:%M %p")
        sender_name = delivery.sender_name      # insert variable reference
        room_number = delivery.room_number      # insert variable reference

        checkbox_key = f"presence_delivery_{delivery_id}"

        # default all checked
        if checkbox_key not in st.session_state:
            st.session_state[checkbox_key] = True

        st.checkbox(
            f"Delivery #{delivery_id} | Admin: {admin_user_id} | Sender: {sender_name} | Room: {room_number} | Time: {delivery_time}",
            key=checkbox_key
        )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Confirm", use_container_width=True):
            try:
                handled_ids = set(st.session_state.get("presence_handled_delivery_ids", []))

                for delivery in deliveries:
                    delivery_id = delivery.delivery_id

                    if st.session_state.get(f"presence_delivery_{delivery_id}"):
                        user_confirm_presence(user_id=user_id, d_id=delivery_id)
                    else:
                        user_deny_delivery(user_id=user_id, d_id=delivery_id)

                    handled_ids.add(delivery_id)

                    # optional cleanup of checkbox key
                    st.session_state.pop(f"presence_delivery_{delivery_id}", None)

                st.session_state["presence_handled_delivery_ids"] = list(handled_ids)
                st.session_state["presence_deliveries"] = []
                st.session_state["show_presence_modal"] = False
                st.rerun()

            except Exception as e:
                st.error(str(e))

    with col2:
        if st.button("Cancel", use_container_width=True):
            try:
                handled_ids = set(st.session_state.get("presence_handled_delivery_ids", []))

                for delivery in deliveries:
                    delivery_id = delivery.delivery_id
                    user_deny_delivery(user_id=user_id, d_id=delivery_id)
                    handled_ids.add(delivery_id)

                    # optional cleanup of checkbox key
                    st.session_state.pop(f"presence_delivery_{delivery_id}", None)

                st.session_state["presence_handled_delivery_ids"] = list(handled_ids)
                st.session_state["presence_deliveries"] = []
                st.session_state["show_presence_modal"] = False
                st.rerun()

            except Exception as e:
                st.error(str(e))

    st.caption("Unchecked deliveries will not be delivered by robot when you press Confirm.")


# ======================
# Modal 2: Delivery Pickup
# ======================
@st.dialog("Delivery Pickup")
def pickup_modal():
    user_id = st.session_state.get("user_id")
    pickup_step = st.session_state.get("pickup_step", 1)
    delivery = st.session_state.get("pickup_delivery") or {}

    delivery_id = delivery.get("delivery_id")
    admin_user_id = delivery.get("admin_user_id")
    sender_name = delivery.get("sender_name")
    delivery_time = delivery.get("delivery_time").strftime("%Y-%m-%d %I:%M %p")
    room_number = delivery.get("room_number")

    # -------------------
    # Step 1: Accept / Deny
    # -------------------
    if pickup_step == 1:
        st.write("Your delivery is ready for pickup.")
        st.markdown(
            f"""
**Delivery ID:** {delivery_id}  
**Admin User ID:** {admin_user_id}  
**Sender:** {sender_name}  
**Delivery Time:** {delivery_time}  
**Room:** {room_number}
"""
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Accept", use_container_width=True):
                st.session_state["pickup_step"] = 2
                st.rerun()

        with col2:
            if st.button("Deny", use_container_width=True):
                try:
                    user_deny_delivery(user_id=user_id, d_id=delivery_id)

                    st.session_state["show_pickup_modal"] = False
                    st.session_state["pickup_step"] = 1
                    st.session_state["pickup_modal_handled_delivery_id"] = delivery_id
                    st.session_state["pickup_delivery"] = None
                    st.session_state["pickup_robot_id"] = None
                    st.session_state["pickup_pin_input"] = ""
                    st.session_state["active_delivery_id"] = None
                    st.rerun()

                except Exception as e:
                    st.error(str(e))

    # -------------------
    # Step 2: Enter pin
    # -------------------
    elif pickup_step == 2:
        st.write("Enter your delivery PIN to unlock pickup.")

        pin = st.text_input(
            "Delivery PIN",
            type="password",
            key="pickup_pin_input"
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Confirm PIN", use_container_width=True):
                try:
                    user_unload_delivery(user_id=user_id, d_id=delivery_id, pin=pin)

                    # if no exception, move to final step
                    st.session_state["pickup_step"] = 3
                    st.rerun()

                except Exception as e:
                    st.error(str(e))

        with col2:
            if st.button("Back", use_container_width=True):
                st.session_state["pickup_step"] = 1
                st.rerun()

    # -------------------
    # Step 3: Final confirm
    # -------------------
    elif pickup_step == 3:
        st.success("Please retrieve your mail and close the robot door before confirming.")

        # IMPORTANT:
        # Streamlit dialogs cannot be made truly non-closeable with full reliability.
        # So the practical workaround is:
        # - do not provide a cancel/close action
        # - if the user dismisses it manually, reopen it on the next rerun until confirm is pressed

        if st.button("Confirm Pickup Complete", use_container_width=True):
            try:
                user_accept_delivery(user_id=user_id, d_id=delivery_id)

                st.session_state["show_pickup_modal"] = False
                st.session_state["pickup_step"] = 1
                st.session_state["pickup_modal_handled_delivery_id"] = delivery_id
                st.session_state["pickup_delivery"] = None
                st.session_state["pickup_robot_id"] = None
                st.session_state["pickup_pin_input"] = ""
                st.session_state["active_delivery_id"] = None
                st.rerun()

            except Exception as e:
                st.error(str(e))


# ====================================
# Polling fragments for global checking
# ====================================
@st.fragment(run_every="5s")
def presence_monitor_fragment():
    check_presence_modal_trigger()


@st.fragment(run_every="5s")
def pickup_monitor_fragment():
    check_pickup_modal_trigger()


# ====================================
# Main render function to call globally
# ====================================
def render_global_delivery_modals():
    init_global_modal_state()

    # Run monitors globally on every page
    presence_monitor_fragment()
    pickup_monitor_fragment()

    # Render presence modal first
    if st.session_state.get("show_presence_modal"):
        presence_modal()

    # Then render pickup modal
    elif st.session_state.get("show_pickup_modal"):
        pickup_modal()