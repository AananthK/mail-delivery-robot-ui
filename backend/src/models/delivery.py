# models/delivery.py
from pydantic import BaseModel, EmailStr

from datetime import datetime
from typing import Optional

#input models: take in informaiton (requests)

# API-request models (pydantic)
class DeliveryCreateRequest(BaseModel):
    admin_id: int 
    recipient_id: int
    room_number: str
    delivery_time: datetime
    sender_name: str
    sender_address: str
    sender_email: EmailStr #ensures correct email formatting (does not check legitness)
    sender_phone: Optional[str]=None
    assigned_robot: Optional[int]=None

    #delivery_id and created_at attributes are handled in database
    #delivery status is determined by the service

class DeliveryUpdateRequest(BaseModel):
    status: Optional[str] = None
    delivery_time: Optional[datetime] = None

#internal/domain model: used in backend
class Delivery:
    def __init__(self, delivery_id, admin_id, status, created_at, last_updated_at, delivery_time=None):
        self.delivery_id = delivery_id
        self.admin_id = admin_id
        self.status = status
        self.created_at = created_at
        self.last_updated_at = last_updated_at
        self.delivery_time = delivery_time

#ouput models: return information (what the client sees)

# API-Response Modules (pydantic)
class DeliveryView(BaseModel):
    delivery_id: int
    status: str
    delivery_time: datetime
    created_at: datetime
    last_updated_at: datetime
    completed_at: Optional[datetime]=None # can be time of delivery completion