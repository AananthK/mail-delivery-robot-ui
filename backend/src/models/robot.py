# models/robot.py
from pydantic import BaseModel, Field
from typing import Literal, Optional

#***** input models: take in informaiton (requests) *****

# input from robot/output from robot
class RobotStatusUpdate(BaseModel):
    robot_id: int
    robot_status: Literal["off", "idle", "charging", "moving"]
    current_room: Optional[str] = Field(default = None, max_length = 10)

# input from admin/output from robot
class RobotNextRoomUpdate(BaseModel):
    robot_id: int
    next_room: str = Field(max_length = 10)

#***** ouput models: return information (what the client sees) *****

class RobotFullView(BaseModel):
    robot_id: int
    robot_status: Literal["off", "idle", "charging", "moving"]
    current_room: Optional[str] = Field(default = None, max_length = 10)
    next_room: Optional[str] = Field(default = None, max_length = 10)

class RobotDeletedView(BaseModel):
    robot_id: int
    