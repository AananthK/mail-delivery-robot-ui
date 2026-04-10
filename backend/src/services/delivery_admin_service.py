# This file contains service functions that handle delivery business logic for the admin
# These functions also convert lists into Pydantic models for API

#**** ADMIN ONLY FUNCTIONS *****

from models.delivery import DeliveryUpdateView, DeliveryQuickView, DeliveryFullView
from persistence.delivery_admin_dao import *
from persistence.delivery_general_dao import get_all_deliveries_dao, update_delivery_status_dao
from services.room_service import find_room
from services.robot_service import find_robot
from services.user_service import user_exists
from datetime import datetime
from zoneinfo import ZoneInfo
from .utils import db_return, dict_list_to_model_list

from typing import Optional

TORONTO = ZoneInfo("America/Toronto")

def create_delivery(a_id: int, 
                    rec_id: int,
                    room: str,
                    del_time: datetime,
                    s_name: str, 
                    s_address: str, 
                    s_email: str,
                    s_phone: Optional[str]=None,
                    robot: Optional[int]=None):
    
    #--- User Constraints ---
    account = user_exists(user_id = rec_id)

    if not account:
        raise LookupError("Account does not exist. Must be an existing recipient account.")

    #--- Room Constraints ---
    # ensure delivery is assigned to a room that exists
    find_room(room)

    #--- Robot Constaints ---
    # initial delivery status is determined by whether a robot is assigned to delivery or not
    if robot is not None:
        # verify robot exists
        r = find_robot(robot_id = robot)
        
        if r['robot_status'] == "off" or r['robot_status'] == "charging":
            status ='ready'
        else:
            raise ValueError("Robot is busy. Select another Robot.")
    else:
        status='no_robot'

    #--- Timing Constraints ---
    # normalize input time
    if del_time.tzinfo is None:
        del_time = del_time.replace(tzinfo=TORONTO)
    else:
        del_time = del_time.astimezone(TORONTO)

    current_time = datetime.now(TORONTO)

    # to prevent creation of delivery to be done in under an hour from now: robot may need to charge
    if del_time - current_time <= timedelta(hours = 1):
        raise ValueError("Delviery must be scheduled atleast 1 hour from current time")

    # to prevent deliveries from coinciding (scheduled deliveries must not be within 5 minutes of another delivery) 
    deliveries_on_date = get_deliveries_by_date_for_admin_dao(admin_id = a_id, day =  del_time)
    
    for d in deliveries_on_date:
             
        d_time = d["delivery_time"]
        # normalize DB timestamp to Toronto time
        d_time = d_time.astimezone(TORONTO) if d_time.tzinfo else d_time.replace(tzinfo=TORONTO)

        if abs(del_time - d_time) <= timedelta(minutes = 5):
            raise ValueError("Time slot contains a delivery. Please select another")

    new_delivery = create_delivery_dao(admin_id = a_id, 
                                    recipient_id = rec_id,
                                    room_number = room,
                                    delivery_time = del_time,
                                    sender_name = s_name, 
                                    sender_address = s_address, 
                                    sender_email = s_email,
                                    delivery_status = status,
                                    sender_phone = s_phone,
                                    assigned_robot = robot)
    
    dView = DeliveryQuickView(delivery_id = new_delivery['delivery_id'], 
                         status = new_delivery['status'], 
                         delivery_time = new_delivery['delivery_time'],
                         created_at = new_delivery['created_at'], 
                         last_updated_at= new_delivery['last_updated_at'],
                         completed_at=None)
    
    return dView

# Read Operations
def get_delivery_by_id_for_admin(m_type: str, a_id: int, d_id: int):
    d_record = db_return(get_delivery_by_id_for_admin_dao(admin_id=a_id, delivery_id=d_id))

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

def get_deliveries_for_admin(m_type: str, ad_id: int):
    dlist = get_deliveries_for_admin_dao(admin_id = ad_id)
    deliveries = dict_list_to_model_list(model_type = m_type, d_list = dlist)
    return deliveries

def get_deliveries_by_recipient_for_admin(m_type: str, a_id: int, r_id: int):
    dlist = get_deliveries_by_recipient_for_admin_dao(admin_id = a_id, recipient_id = r_id)
    deliveries = dict_list_to_model_list(model_type = m_type, d_list = dlist)
    return deliveries

def get_deliveries_by_sender_for_admin(m_type: str, a_id: int, s_name: str):
    dlist = get_deliveries_by_sender_for_admin_dao(admin_id = a_id, sender_name=s_name)
    deliveries = dict_list_to_model_list(model_type = m_type, d_list = dlist)
    return deliveries

def get_deliveries_by_date_for_admin(m_type: str, a_id: int, date_time: datetime):
    
    # normalize input time
    if date_time.tzinfo is None:
        date_time = date_time.replace(tzinfo=TORONTO)
    else:
        date_time = date_time.astimezone(TORONTO)

    dlist = get_deliveries_by_date_for_admin_dao(admin_id = a_id, day=date_time)
    deliveries = dict_list_to_model_list(model_type = m_type, d_list = dlist)
    return deliveries

def get_deliveries_by_room_for_admin(m_type: str, a_id: int, room: str):
    dlist = get_deliveries_by_room_for_admin_dao(admin_id = a_id, room_number=room)
    deliveries = dict_list_to_model_list(model_type = m_type, d_list = dlist)
    return deliveries

# Update Operations

def update_delivery_by_admin(a_id:int,
                          d_id: int, 
                          u_room: Optional[str]=None, 
                          u_time: Optional[datetime]=None,
                          u_status: Optional[str]=None):
    
    # check delivery exists
    delivery = db_return(get_delivery_by_id_for_admin_dao(admin_id = a_id, delivery_id = d_id))

    # normalize DB timestamp to Toronto time
    delivery['delivery_time'] = delivery['delivery_time'].astimezone(TORONTO) if delivery['delivery_time'].tzinfo else delivery['delivery_time'].replace(tzinfo=TORONTO)

    # handle no update fields
    if u_room is None and u_time is None and u_status is None:
         raise ValueError("No updated fields")

    current_time = datetime.now(TORONTO)

    # time updates must be an hour before scheduled delivery
    if delivery['delivery_time'] - current_time <= timedelta(hours = 1):
        raise ValueError("Delivery can no longer be updated within 1 hour of its scheduled time.")

    if u_room is not None:
        # ensure delivery is assigned to a room that exists
        find_room(room_number = u_room)

    if u_time is not None:

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
        deliveries_on_date = get_deliveries_by_date_for_admin_dao(admin_id = a_id, day =  u_time)
        for d in deliveries_on_date:
             
            d_time = d["delivery_time"]
            # normalize DB timestamp to Toronto time
            d_time = d_time.astimezone(TORONTO) if d_time.tzinfo else d_time.replace(tzinfo=TORONTO)
             
            # delivery being updated omits itself (if time update is on the same day)
            if d["delivery_id"] == d_id:
                continue

            if abs(u_time - d_time) <= timedelta(minutes = 5):
                raise ValueError("Time slot contains a delivery. Please select another")


    updated_delivery = db_return(update_delivery_by_admin_dao(admin_id = a_id,
                                                              delivery_id = d_id, 
                                                              room_number = u_room, 
                                                              delivery_time = u_time,
                                                              status = u_status))

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

def update_delivery_robot(a_id: int, d_id: int, r_id: int):

    # ensure delivery exists
    try:
        delivery = db_return(get_delivery_by_id_for_admin_dao(admin_id = a_id, delivery_id = d_id))
    except LookupError:
        raise LookupError("Delivery does not exist")
    
    # ensure robot exists
    r = find_robot(robot_id = r_id)
    
    # ensure robot is not busy
    if r['robot_status'] != "off" and r['robot_status'] != "charging":
        raise ValueError("Robot is busy. Select another Robot.")

    if delivery:

        modifiable_status = ["no_robot", "ready", "error"]

        if delivery['status'] not in modifiable_status:
            raise ValueError("Cannot modify robot for an underway or completed delivery")
    
    updated_delivery = update_delivery_robot_dao(admin_id = a_id, delivery_id = d_id, robot_id = r_id)

    dView = DeliveryUpdateView(delivery_id = updated_delivery['delivery_id'], 
                               admin_id = updated_delivery['admin_user_id'], 
                               status = updated_delivery['status'], 
                               room_number = updated_delivery['room_number'],
                               delivery_time = updated_delivery['delivery_time'],
                               created_at = updated_delivery['created_at'], 
                               last_updated_at = updated_delivery['last_updated_at'],
                               assigned_robot = updated_delivery['assigned_robot'],
                               completed_at = None,
                               deleted_at = None)

    return dView

# persistence function to check for late deliveries: should always be running on application
def check_late_deliveries():

    late_deliveries = []

    # statues where a delivery cannot be labelled late (late refers to when the delivery has been deployed)
    acceptable_states = ['in_progress','error','unloading','complete']

    deliveries = get_all_deliveries_dao()

    current_time = datetime.now(TORONTO)

    for d in deliveries:
        
        due_time = d['delivery_time']

        # ensure correct timezone
        if due_time.tzinfo is None:
            due_time = due_time.replace(tzinfo=TORONTO)
        else:
            due_time = due_time.astimezone(TORONTO)

        if d['status'] == 'late':
            late_deliveries.append(d)

        elif due_time < current_time and d['status'] not in acceptable_states:
            # update the database
            update_delivery_status_dao(delivery_id= d['delivery_id'], status = 'late')
            # update for viewing
            d['status'] = 'late'
            late_deliveries.append(d)

    return dict_list_to_model_list(model_type = "quick_view", d_list = late_deliveries)

# Delete Operations: Only Admin
def delete_delivery(a_id: int, d_id: int):
    deleted_delivery = db_return(delete_delivery_dao(admin_id = a_id, delivery_id = d_id))
    dView = DeliveryUpdateView(delivery_id = deleted_delivery['delivery_id'],
                               admin_id = deleted_delivery['admin_user_id'],  
                               status = deleted_delivery['status'], 
                               room_number = deleted_delivery['room_number'],
                               delivery_time = deleted_delivery['delivery_time'],
                               created_at = deleted_delivery['created_at'], 
                               last_updated_at= deleted_delivery['last_updated_at'],
                               completed_at=None,
                               deleted_at = datetime.now())
     
    if dView.status == 'complete':
                dView.completed_at = dView.last_updated_at   

    return dView