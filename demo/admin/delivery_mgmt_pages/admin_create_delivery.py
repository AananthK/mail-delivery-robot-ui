import streamlit as st
import app_bootstrap

from datetime import datetime, date, time, timedelta

from backend.src.services.admin_service import admin_create_delivery

# Admin guard
if not st.session_state.get("is_logged_in") or st.session_state.get("role") != "admin":
    st.error("Admin access only. Please log in.")
    st.switch_page("streamlit_app.py")

st.set_page_config(page_title="Create Delivery", layout="wide")
st.title("📨 Create Deliveryy")

admin_id = st.session_state.get("user_id")
st.caption(f"Admin ID: {admin_id}")

# Set defaults only once
if "create_delivery_date" not in st.session_state:
    st.session_state.create_delivery_date = date.today()

if "create_delivery_time" not in st.session_state:
    # Better default: at least 1 hour from now
    default_dt = datetime.now() + timedelta(hours=1)
    st.session_state.create_delivery_time = default_dt.time().replace(second=0, microsecond=0)

with st.form("create_delivery_form"):
    recipient_id = st.number_input("Recipient ID", min_value=1, step=1)
    room_number = st.text_input("Room Number")

    # Delivery time picker (date + time -> datetime)
    d_date = st.date_input(
        "Delivery Date",
        key="create_delivery_date"
    )

    d_time = st.time_input(
        "Delivery Time",
        key="create_delivery_time"
    )

    delivery_time = datetime.combine(d_date, d_time)

    st.subheader("Sender Information")
    sender_name = st.text_input("Sender Name")
    sender_address = st.text_input("Sender Address")
    sender_email = st.text_input("Sender Email")
    sender_phone = st.text_input("Sender Phone (optional)")

    robot = st.number_input("Robot ID (optional)", min_value=0, step=1, value=0)

    submitted = st.form_submit_button("Create Delivery")

if submitted:
    
    missing = []
    if not room_number: missing.append("Room Number")
    if not sender_name: missing.append("Sender Name")
    if not sender_address: missing.append("Sender Address")
    if not sender_email: missing.append("Sender Email")

    if missing:
        st.warning("Missing required fields: " + ", ".join(missing))
    else:
        try:
            result = admin_create_delivery(
                admin_id=int(admin_id),
                recipient_id=int(recipient_id),
                room_number=room_number,
                delivery_time=delivery_time,
                sender_name=sender_name,
                sender_address=sender_address,
                sender_email=sender_email,
                sender_phone=sender_phone if sender_phone else None,
                robot=int(robot) if robot > 0 else None
            )

            st.success("Delivery created successfully!")

            if hasattr(result, "model_dump"):
                st.json(result.model_dump())
            elif isinstance(result, dict):
                st.json(result)
            else:
                st.write(result)

        except Exception as e:
            st.error(str(e))

st.divider()
if st.button("⬅️ Back to Admin Delivery Management"):
    st.switch_page("admin/admin_delivery_mgmt.py")
