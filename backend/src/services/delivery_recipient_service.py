# This file contains service functions that handle delivery business logic for the recipient
# These functions also convert lists into Pydantic models for API

#**** RECIPIENT ONLY FUNCTIONS *****

from models.delivery import DeliveryUpdateView, DeliveryQuickView, DeliveryFullView
from persistence.delivery_recipient_dao import *
from persistence.delivery_general_dao import update_delivery_status_dao
from services.room_service import find_room
from services.robot_service import update_robot_door_status, get_robot_by_id, find_robot
from datetime import datetime
from .utils import db_return, dict_list_to_model_list

from typing import Optional

# Read Operations
def get_delivery_by_id_for_recipient(m_type: str, r_id: int, d_id: int):
    d_record = db_return(get_delivery_by_id_for_recipient_dao(recipient_id = r_id, delivery_id = d_id))

    if m_type =='quick_view':
        delivery = DeliveryQuickView(delivery_id = d_record['delivery_id'], 
                                     status = d_record['status'], 
                                     delivery_time = d_record['delivery_time'],
                                     created_at = d_record['created_at'], 
                                     last_updated_at= d_record['last_updated_at'])
    elif m_type == 'full_view':
        delivery = DeliveryFullView(delivery_id = d_record['delivery_id'], 
                                    status = d_record['status'],
                                    admin_user_id = d_record['admin_user_id'],
                                    sender_name = d_record['sender_name'],
                                    recipient_id = d_record['recipient_user_id'],
                                    assigned_robot = d_record['assigned_robot'],
                                    room_number = d_record['room_number'],
                                    delivery_time = d_record['delivery_time'],
                                    created_at = d_record['created_at'], 
                                    last_updated_at= d_record['last_updated_at'])
            
    if delivery.status == 'complete':
        delivery.completed_at = d_record['last_updated_at']

    return delivery

def get_deliveries_for_recipient(m_type: str, r_id: int):
    dlist = get_deliveries_for_recipient_dao(recipient_id = r_id)
    deliveries = dict_list_to_model_list(model_type = m_type, d_list = dlist)
    return deliveries

def get_deliveries_by_admin_for_recipient(m_type: str, r_id: int, a_id: int):
    dlist = get_deliveries_by_admin_for_recipient_dao(recipient_id = r_id, admin_id = a_id)
    deliveries = dict_list_to_model_list(model_type = m_type, d_list = dlist)
    return deliveries

def get_deliveries_by_sender_for_recipient(m_type: str, r_id: int, s_name: str):
    dlist = get_deliveries_by_sender_for_recipient_dao(recipient_id = r_id, sender_name=s_name)
    deliveries = dict_list_to_model_list(model_type = m_type, d_list = dlist)
    return deliveries

def get_deliveries_by_date_for_recipient(m_type: str, r_id: int, date_time: datetime):

    # normalize input time
    if date_time.tzinfo is None:
        date_time = date_time.replace(tzinfo=TORONTO)
    else:
        date_time = date_time.astimezone(TORONTO)

    dlist = get_deliveries_by_date_for_recipient_dao(recipient_id = r_id, day=date_time)
    deliveries = dict_list_to_model_list(model_type = m_type, d_list = dlist)
    return deliveries

def get_deliveries_by_room_for_recipient(m_type: str, r_id: int, room: str):
    dlist = get_deliveries_by_room_for_recipient_dao(recipient_id = r_id, room_number=room)
    deliveries = dict_list_to_model_list(model_type = m_type, d_list = dlist)
    return deliveries

def get_ready_deliveries_for_recipient(r_id: int):
    dlist = get_ready_deliveries_for_recipient_dao(recipient_id = r_id)
    deliveries = dict_list_to_model_list(model_type = "full_view", d_list = dlist)
    return deliveries

def get_unloading_delivery_for_recipient(r_id: int):
    d_record = get_unloadling_delivery_for_recipient_dao(recipient_id=r_id)
    
    if d_record is None:
        return None

    delivery = DeliveryFullView(delivery_id = d_record['delivery_id'], 
                                    status = d_record['status'],
                                    admin_user_id = d_record['admin_user_id'],
                                    sender_name = d_record['sender_name'],
                                    recipient_id = d_record['recipient_user_id'],
                                    assigned_robot = d_record['assigned_robot'],
                                    room_number = d_record['room_number'],
                                    delivery_time = d_record['delivery_time'],
                                    created_at = d_record['created_at'], 
                                    last_updated_at= d_record['last_updated_at'])
    return delivery

def get_delivery_pin(r_id: int, d_id: int):
    # check if delivery exists
    delivery = db_return(get_delivery_by_id_for_recipient_dao(recipient_id = r_id, delivery_id = d_id))

    record = get_delivery_pin_dao(recipient_id = delivery['recipient_user_id'], delivery_id = delivery['delivery_id'])

    return record['pin']

# Update Operations
def update_delivery_by_recipient(r_id:int,
                          d_id: int, 
                          u_room: Optional[str]=None, 
                          u_time: Optional[datetime]=None):
    
    # check delivery exists
    delivery = db_return(get_delivery_by_id_for_recipient_dao(recipient_id = r_id, delivery_id = d_id))
    # normalize DB timestamp to Toronto time
    delivery['delivery_time'] = delivery['delivery_time'].astimezone(TORONTO) if delivery['delivery_time'].tzinfo else delivery['delivery_time'].replace(tzinfo=TORONTO)

    # handle no update fields
    if u_room is None and u_time is None:
         raise ValueError("No updated fields")

    current_time = datetime.now(TORONTO)

    # time updates must be an hour before scheduled delivery
    if delivery['delivery_time'] - current_time <= timedelta(hours = 1):
                raise ValueError("Delivery can no longer be updated within 1 hour of its scheduled time.")

    if u_room:
        # ensure delivery is assigned to a room that exists
        find_room(room_number = u_room)

    if u_time:

        # ensure correct timezone
        if u_time.tzinfo is None:
            u_time = u_time.replace(tzinfo=TORONTO)
        else:
            u_time = u_time.astimezone(TORONTO)

        if u_time < current_time:
             raise ValueError("Updated time must be in future")

        # time updates must be at least an hour ahead of current time
        if u_time - current_time <= timedelta(hours = 1):
             raise ValueError("Update must be minimum one hour from current time")
        
        # to prevent deliveries from coinciding (time updates must not be within 5 minutes of another delivery) 
        deliveries_on_date = get_deliveries_by_date_for_recipient_dao(recipient_id = r_id, day =  u_time)
        for d in deliveries_on_date:
             
            d_time = d["delivery_time"]
            # normalize DB timestamp to Toronto time
            d_time = d_time.astimezone(TORONTO) if d_time.tzinfo else d_time.replace(tzinfo=TORONTO)
             
            # delivery being updated omits itself (if time update is on the same day)
            if d["delivery_id"] == d_id:
                continue

            if abs(u_time - d_time) <= timedelta(minutes = 5):
                raise ValueError("Time slot contains a delivery. Please select another")


    updated_delivery = db_return(update_delivery_by_recipient_dao(recipient_id = r_id,
                                                              delivery_id = d_id, 
                                                              room_number = u_room, 
                                                              delivery_time = u_time))

    dView = DeliveryUpdateView(delivery_id = updated_delivery['delivery_id'], 
                               admin_id = updated_delivery['admin_user_id'], 
                               status = updated_delivery['status'], 
                               room_number = updated_delivery['room_number'],
                               delivery_time = updated_delivery['delivery_time'],
                               created_at = updated_delivery['created_at'], 
                               last_updated_at = updated_delivery['last_updated_at'],
                               completed_at = None,
                               deleted_at = None)
    
    if updated_delivery['status'] == 'complete':
         dView.completed_at = updated_delivery['last_updated_at']

    return dView

def change_delivery_room_recipient(r_id: int, d_id: int, room_id: str):
    dView = update_delivery_by_recipient(r_id = r_id, d_id = d_id, u_room = room_id)
    return dView

def change_delivery_time_recipient(r_id: int, d_id: int, time: datetime):
    dView = update_delivery_by_recipient(r_id = r_id, d_id = d_id, u_time = time)
    return dView

def confirm_presence(r_id: int, d_id: int):
    # confirm delivery exists
    d = db_return(get_delivery_by_id_for_recipient_dao(recipient_id=r_id, delivery_id=d_id))

    # confirm delivery status is ready to confirm presence for
    if d['status'] != "ready":
        raise ValueError("Delivery not ready today. Try again later.")
    
    delivery = update_recipient_confirmed_status_dao(delivery_id=d_id, recipient_id= r_id, confirmed=True)
    return delivery

#---- Robot Interaction (During delivery) ----

def unload_mail_recipient(d_id: int, r_id: int, pin: str):

    # confirm delivery exists
    d = db_return(get_delivery_by_id_for_recipient_dao(recipient_id=r_id, delivery_id=d_id))

    # confirm delivery status is unloading (delivery has reached recipient's room)
    if d['status'] != "unloading":
        raise ValueError("Delivery has not arrived yet. Cannot unload.")
    
    # confirm recipient is available to unload delivery
    if not d['recipient_confirmed']:
        raise ValueError("Recipient not available. Cannot unload.")

    # confirm delivery robot exists
    r = find_robot((d['assigned_robot']))
    # confirm robot is idle (stopped infront of door)
    if r['robot_status'] != "idle":
        raise ValueError("Robot is not idle. Delivery cannot be accepted.")

    d_pin = get_delivery_pin(r_id= d['recipient_user_id'], d_id=d['delivery_id'])

    if pin == d_pin: # recipient enters correct pin
        # mark robot door as open
        # robot reads door_status API and opens door
        # assume robot door is always closed 
        update_robot_door_status(robot_id = d['assigned_robot'], door_status = 'open')
    else:
        raise ValueError("Pin is incorrect. Please try again.")
    
    return {"message": "door opened successfully!"}

# service function for admin to accept delivery
def accept_delivery_recipient(r_id: int, d_id: int):

    # confirm delivery exists
    d = db_return(get_delivery_by_id_for_recipient_dao(recipient_id=r_id, delivery_id=d_id))

    # confirm delivery status is unloading (delivery has reached recipient's room)
    if d['status'] != "unloading":
        raise ValueError("Delivery has not arrived yet. Cannot unload.")

    # confirm recipient is available to accept delivery
    if not d['recipient_confirmed']:
        raise ValueError("Recipient not available. Delivery not accepted.")

    # confirm delivery robot exists
    r = find_robot((d['assigned_robot']))
    # confirm robot is idle (stopped infront of door)
    if r['robot_status'] != "idle":
        raise ValueError("Robot is not idle. Delivery cannot be accepted.")

    # mark delivery as complete
    updated_delivery = update_delivery_status_dao(delivery_id = d['delivery_id'], status = "complete")
    # close robot door
    update_robot_door_status(robot_id = d['assigned_robot'], door_status = 'close')

    dView = DeliveryUpdateView(delivery_id = updated_delivery['delivery_id'], 
                               admin_id = updated_delivery['admin_user_id'], 
                               status = updated_delivery['status'], 
                               room_number = updated_delivery['room_number'],
                               delivery_time = updated_delivery['delivery_time'],
                               created_at = updated_delivery['created_at'], 
                               last_updated_at = updated_delivery['last_updated_at'],
                               completed_at = updated_delivery['last_updated_at'],
                               deleted_at = None)
    
    return dView

# service function when a recipient denies a delivery
def deny_delivery_recipient(r_id: int, d_id: int):

    # ensure delivery exists
    delivery = db_return(get_delivery_by_id_for_recipient_dao(recipient_id=r_id, delivery_id=d_id))

    d_time = delivery["delivery_time"]
    d_status = delivery["status"]

    # only allow denial while delivery is active
    if d_status not in {"ready", "in_progress", "unloading"}:
        raise ValueError("Delivery can only be denied while it is ready, in-progress or unloading.")
    
    # confirm delivery robot exists
    r = find_robot((delivery['assigned_robot']))
    # confirm robot is idle (stopped infront of door)
    if r['robot_status'] == "moving":
        raise ValueError("Robot is not in operation. Delivery cannot be denied.")

    # ensure correct timezone
    if d_time.tzinfo is None:
        d_time = d_time.replace(tzinfo=TORONTO)
    else:
        d_time = d_time.astimezone(TORONTO)

    next_day = d_time + timedelta(days=1)

    while True:
        try:
            # move delivery to next valid same-time slot
            change_delivery_time_recipient(
                r_id=r_id,
                d_id=d_id,
                time=next_day
            )

            # reset status for future delivery attempt
            update_delivery_status_dao(delivery_id=d_id, status="ready")
            update_recipient_confirmed_status_dao(delivery_id=d_id, recipient_id=r_id,confirmed=False)

            return get_delivery_by_id_for_recipient(m_type="full_view", r_id=r_id, d_id=d_id)

        except ValueError as e:
            if str(e) == "Time slot contains a delivery. Please select another":
                next_day += timedelta(days=1)
            else:
                raise