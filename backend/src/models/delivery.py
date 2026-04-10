# models/delivery.py
from pydantic import BaseModel, EmailStr, Field, field_validator

from datetime import datetime
from zoneinfo import ZoneInfo

local_tz = ZoneInfo("America/Toronto") # Application stores in ET (Toronto)
db_tz = ZoneInfo("UTC") # Supabase stores UTC timezone

from typing import Optional

# Handling timezones for each model
def ensure_datetime(dt):
    if dt is None:
        return None
    if not isinstance(dt, datetime):
        return dt
    return dt


def to_utc(dt):
    dt = ensure_datetime(dt)
    if dt is None or not isinstance(dt, datetime):
        return dt

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=local_tz)

    return dt.astimezone(db_tz)


def to_toronto(dt):
    dt = ensure_datetime(dt)
    if dt is None or not isinstance(dt, datetime):
        return dt

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=db_tz)

    return dt.astimezone(local_tz)


class UTCInputModel(BaseModel):
    @field_validator("*", mode="before")
    @classmethod
    def convert_datetimes_to_utc(cls, value):
        return to_utc(value)


class TorontoOutputModel(BaseModel):
    @field_validator("*", mode="before")
    @classmethod
    def convert_datetimes_to_toronto(cls, value):
        return to_toronto(value)

#input models: take in informaiton (requests)

# API-request models (pydantic)
class DeliveryCreateRequest(UTCInputModel):
    admin_id: int = Field(..., ge=1) 
    recipient_id: int = Field(..., ge=1) 
    room_number: str
    delivery_time: datetime
    sender_name: str
    sender_address: str
    sender_email: EmailStr #ensures correct email formatting (does not check legitness)
    sender_phone: Optional[str]=None
    assigned_robot: Optional[int]=None

    #delivery_id and created_at attributes are handled in database
    #delivery status is determined by the service

class DeliveryUpdateRequest(UTCInputModel):
    room_number: Optional[str] = None
    status: Optional[str] = None
    delivery_time: Optional[datetime] = None

class DeliveryAssignRobot(BaseModel):
    admin_id: int
    delivery_id: int
    robot_id:int

#ouput models: return information (what the client sees)

# API-Response Modules (pydantic)
class DeliveryUpdateView(TorontoOutputModel):
    delivery_id: int = Field(..., ge=1) 
    admin_id: int = Field(..., ge=1) 
    status: str
    room_number: str
    delivery_time: datetime
    created_at: datetime
    last_updated_at: datetime
    assigned_robot: Optional[int]=None
    completed_at: Optional[datetime]=None
    deleted_at: Optional[datetime]=None # this field will only be used for deletions

class DeliveryQuickView(TorontoOutputModel):
    delivery_id: int = Field(..., ge=1) 
    status: str
    delivery_time: datetime
    created_at: datetime
    last_updated_at: datetime
    completed_at: Optional[datetime]=None # can be time of delivery completion

class DeliveryFullView(TorontoOutputModel):
    delivery_id: int = Field(..., ge=1) 
    admin_user_id: int = Field(..., ge=1) 
    sender_name: str
    recipient_id: int
    room_number: str
    status: str
    delivery_time: datetime
    created_at: datetime
    last_updated_at: datetime
    assigned_robot: Optional[int]=None # can be assigned later
    completed_at: Optional[datetime]=None # can be time of delivery completion

# input/output model for robot to read delivery info
class DeliveryRobotView(BaseModel):
    delivery_id: int
    room_number: str
    status: str
    recipient_confirmed: Optional[bool] = None