# This file contains service functions that handle room business logic for any users
# These functions also convert lists into Pydantic models for API

from models.room import *
from persistence.room_dao import *
from persistence.delivery_general_dao import get_all_deliveries_by_room_dao
from services.utils import db_return

# helper function to find room by number
def find_room(room_number: str):
    try:
        room = db_return(get_room_by_number_dao(room_number = room_number))
    except LookupError:
        raise LookupError("Room does not exist")
    
    return room

def create_room(room_num: str, floor_num: str):

    if len(room_num) > 10:
        raise ValueError("Room number too large: 10 characters MAX")
    
    if len(floor_num) > 3:
        raise ValueError("Floor number too large: 3 characters MAX")
    
    # Check if room already exists
    if get_room_by_number_dao(room_number = room_num) is not None:
        raise ValueError("Room already exists")
    
    r = create_room_dao(room_number = room_num, floor_number = floor_num)

    new_room = RoomCreate(room_number = r['room_number'], 
                          floor_number = r['floor_number'])
    
    return new_room

def get_room_by_number(room_num: str):

    r = find_room(room_num)

    room = RoomView(room_number = r['room_number'], 
                    floor_number = r['floor_number'])
    
    return room

def get_room_by_floor(floor_num: str):

    # empty list of Pydantic models to be returned: rooms
    rooms = []

    r_list = get_rooms_by_floor_dao(floor_number = floor_num)

    # insert modles into "rooms"
    for r in r_list:
        room = RoomView(room_number = r['room_number'], 
                        floor_number = r['floor_number'])
        
        rooms.append(room)
    
    return rooms

def delete_room(room_num: str):

    # check if room exists
    r = find_room(room_num)

    # ensure deletions cannot happen when a delivery is under progress to a particular room
    deliveries = get_all_deliveries_by_room_dao(room_num = room_num)

    for d in deliveries:
        if d['status'] != "completed":
            raise ValueError("Cannot delete room while a delivery is underway")

    r = delete_room_dao(room_number = room_num)

    d_room = RoomView(room_number = r['room_number'], 
                    floor_number = r['floor_number'])
    
    return d_room