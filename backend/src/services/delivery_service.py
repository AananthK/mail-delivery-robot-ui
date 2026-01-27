from models.delivery import Delivery, DeliveryCreateRequest, DeliveryUpdateView, DeliveryQuickView, DeliveryFullView
from persistence.delivery_dao import *
from datetime import datetime
from .utils import db_return

from typing import Optional

def create_delivery(ad_id: int, 
                    rec_id: int,
                    room: str,
                    del_time: datetime,
                    s_name: str, 
                    s_address: str, 
                    s_email: str,
                    s_phone: Optional[str]=None,
                    robot: Optional[int]=None):
    
    # initial delivery status is determined by whether a robot is assigned to delivery or not
    if robot is not None:
        status='ready'
    else:
        status='no_robot'

    new_delivery = create_delivery_dao(admin_id = ad_id, 
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

# helper method: turn dict_lists from sql cursor into JSON-value Pydantic Model_lists
def dict_list_to_model_list(model_type: str, d_list: list[dict]):

    model = [] # start with an empty list

    if model_type == 'quick_view':
        for dl in d_list: # for every row (dict: d1) in d_list

            # assigning dict_list values to Pydantic Model m
            m = DeliveryQuickView(delivery_id = dl['delivery_id'], 
                                  status = dl['status'], 
                                  delivery_time = dl['delivery_time'],
                                  created_at = dl['created_at'], 
                                  last_updated_at= dl['last_updated_at'])
            
            # updating the completed_at field using 'status' from record
            if m.status == 'complete':
                m.completed_at = dl['last_updated_at']

            model.append(m) # add model to model_list
        
        return model
            
    elif model_type == 'full_view':
           
        for dl in d_list:
            m = DeliveryFullView(delivery_id = dl['delivery_id'], 
                                 status = dl['status'],
                                 admin_user_id = dl['admin_user_id'],
                                 sender_name = dl['sender_name'],
                                 recipient_id = dl['recipient_user_id'],
                                 assigned_robot = dl['assigned_robot'],
                                 room_number = dl['room_number'],
                                 delivery_time = dl['delivery_time'],
                                 created_at = dl['created_at'], 
                                 last_updated_at= dl['last_updated_at'])
            
            if m.status == 'complete':
                m.completed_at = dl['last_updated_at']

            model.append(m)
            
        return model
    
    raise ValueError("Unkown delivery view type")


def get_all_deliveries(m_type: str):
    dlist = get_all_deliveries_dao()
    deliveries = dict_list_to_model_list(model_type = m_type, d_list = dlist)
    return deliveries

# Read Operations: Only Admins
def get_delivery_by_id(m_type: str, d_id: int):
    d_record = db_return(get_delivery_by_id_dao(delivery_id=d_id))

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

def get_deliveries_by_admin(m_type: str, ad_id: int):
    dlist = get_delivery_by_admin_dao(admin_id=ad_id)
    deliveries = dict_list_to_model_list(model_type = m_type, d_list = dlist)
    return deliveries

# Read Operations: All Users
def get_deliveries_by_recipient(m_type: str, r_id: int):
    dlist = get_delivery_by_recipient_dao(recipient_id = r_id)
    deliveries = dict_list_to_model_list(model_type = m_type, d_list = dlist)
    return deliveries

def get_deliveries_by_sender(m_type: str, s_name: str):
    dlist = get_delivery_by_sender_dao(sender_name=s_name)
    deliveries = dict_list_to_model_list(model_type = m_type, d_list = dlist)
    return deliveries

def get_deliveries_by_date(m_type: str, date_time: datetime):
    dlist = get_delivery_by_date_dao(date=date_time)
    deliveries = dict_list_to_model_list(model_type = m_type, d_list = dlist)
    return deliveries

# Update Operations: All Users
def update_delivery(d_id: int, 
                    u_room: Optional[str]=None, 
                    u_time: Optional[datetime]=None,
                    u_status: Optional[str]=None):
    
    updated_delivery = db_return(update_delivery_dao(delivery_id = d_id, 
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
     
# Delete Operations: Only Admin
def delete_delivery(d_id: int):
    deleted_delivery = db_return(delete_delivery_dao(delivery_id = d_id))
    dView = DeliveryUpdateView(delivery_id = deleted_delivery['delivery_id'],
                               admin_id = deleted_delivery['admin_user_id'],  
                               status = deleted_delivery['status'], 
                               room_number = deleted_delivery['room number'],
                               delivery_time = deleted_delivery['delivery_time'],
                               created_at = deleted_delivery['created_at'], 
                               last_updated_at= deleted_delivery['last_updated_at'],
                               completed_at=None,
                               deleted_at = datetime.now())
     
    if dView.status == 'complete':
                dView.completed_at = dView.last_updated_at   

    return dView