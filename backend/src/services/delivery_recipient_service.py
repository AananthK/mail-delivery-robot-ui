# This file contains service functions that handle delivery business logic for the recipient
# These functions also convert lists into Pydantic models for API

#**** RECIPIENT ONLY FUNCTIONS *****

from models.delivery import DeliveryUpdateView, DeliveryQuickView, DeliveryFullView
from persistence.delivery_recipient_dao import *
from persistence.delivery_general_dao import update_delivery_status_dao
from services.room_service import find_room
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

# service function when a recipient denies a delivery
def deny_delivery_recipient(r_id: int, d_id):

    # ensure delivery exists
    delivery = db_return(get_delivery_by_id_for_recipient(r_id = r_id, d_id = d_id))

    d_time = delivery['delivery_time']
    d_status = delivery['status']

    # ensure correct timezone
    if d_time.tzinfo is None:
        d_time = d_time.replace(tzinfo=TORONTO)
    else:
        d_time = d_time.astimezone(TORONTO)

    next_day =  d_time + timedelta(days = 1)

    # recipient can only deny a delivery in progress, otherwise update delivery time
    while d_status == "in_progress":
        try:
            # Set delivery time to next day (closest future day, same time, with no conflicts)
            delivery = change_delivery_time_recipient(r_id = r_id, d_id = d_id, time = next_day)

            # also set delivery status to ready
            update_delivery_status_dao("ready")
        except ValueError as e:

            # catch potential delivery conflicts
            if str(e) == "Time slot contains a delivery. Please select another":
                # increase future date by a day
                next_day += timedelta(days = 1)
            else:
                raise

    return delivery