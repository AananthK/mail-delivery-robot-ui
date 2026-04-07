# models/robot_event_log.py
from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

#***** input models: take in informaiton (requests) *****

# robot sends event to system
class RobotEventCreate(BaseModel):
    robot_id: int
    event_type: Literal["operation","warning","error","success"]
    event_time: datetime
    description: str = Field(max_length = 200)
    delivery_id: Optional[int] = None

#***** ouput models: return information (what the client sees) *****

# displayng robot event
class RobotEventMessage(BaseModel):
    event_id: int
    event_type: Literal["operation","warning","error","success"]
    robot_id: int
    event_time: datetime
    description: str = Field(max_length = 200)
    delivery_id: Optional[int] = None