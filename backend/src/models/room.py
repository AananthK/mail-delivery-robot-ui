# models/room.py
from pydantic import BaseModel, Field
from typing import Literal, Optional

#***** input models: take in informaiton (requests) *****

# admin creates room
class RoomCreate(BaseModel):
    room_number: str = Field(max_length = 10)
    floor_number: str = Field(max_length = 3)

#***** ouput models: return information (what the client sees) *****

class RoomView(BaseModel):
    room_number: str = Field(max_length = 10)
    floor_number: str = Field(max_length = 3)