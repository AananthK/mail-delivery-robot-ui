from models.delivery import Delivery, DeliveryCreateRequest, DeliveryAddress, DeliveryUpdateRequest, DeliveryView
from persistence.delivery_dao import create_delivery_dao
from datetime import datetime

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
    
    dView = DeliveryView(delivery_id = new_delivery['delivery_id'], 
                         status = new_delivery['status'], 
                         created_at = new_delivery['created_at'], 
                         completed_at=None)
    
    return dView

