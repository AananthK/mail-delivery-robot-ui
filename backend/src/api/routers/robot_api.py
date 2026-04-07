from fastapi import APIRouter, Query, HTTPException, Depends
from models.room import RoomView
from services.robot_service import *
from services.room_service import get_room_by_number
from services.admin_service import get_robot_by_id
from services.delivery_recipient_service import get_delivery_pin

from api.api_security import verify_api_key

router = APIRouter(
    dependencies=[Depends(verify_api_key)]
)

#----- Get endpoints -----
# GET = retrieve a resource

# GET robot's status at /robot/{robot_id}/status
@router.get("/robot/{robot_id}/status", response_model = RobotFullView)

def get_robot_status_endpoint(robot_id: int): 

    return get_robot_by_id(robot_id = robot_id)

# GET robot's current room at /robot/{robot_id}/current_room
@router.get("/robot/{robot_id}/current_room", response_model = RoomView)
# Response from endpoint can be either view depending on query
def current_room_endpoint(robot_id: int): 

    robot = get_robot_by_id(robot_id)

    return get_room_by_number(robot.current_room)

# GET robot's next room at /robot/{robot_id}/next_room
@router.get("/robot/{robot_id}/next_room", response_model = RoomView)
# Response from endpoint can be either view depending on query
def next_room_endpoint(robot_id: int): 

    robot = get_robot_by_id(robot_id)

    return get_room_by_number(robot.next_room)

# GET robot's door command at /robot/{robot_id}/door
@router.get("/robot/{robot_id}/door")
# Response from endpoint can be either view depending on query
def robot_door_endpoint(robot_id: int): 
    return get_robot_door_status(robot_id=robot_id)

#----- Post endpoints -----
# POSt = create a resource/change API state

#----- UPDATE endpoints -----
# PATCH = modify parts of a resource
# PUT = replace entire resource

# PATCH robot's status at /robot/{robot_id}/status
@router.patch("/robot/{robot_id}/status", response_model = RobotStatusUpdate)

def update_robot_status_endpoint(robot_id: int, update: RobotStatusUpdate): 

    return update_robot_status(robot_id = robot_id, status = update.robot_status)

# PATCH robot's current room at /robot/{robot_id}/current_room
@router.patch("/robot/{robot_id}/current_room", response_model = RobotStatusUpdate)

def update_current_room_endpoint(robot_id: int, update: RobotStatusUpdate): 

    return update_robot_current_room(robot_id = robot_id, current_room = update.current_room)

# PATCH robot's next room at /robot/{robot_id}/next_room
@router.patch("/robot/{robot_id}/next_room", response_model = RobotNextRoomUpdate)

def update_next_room_endpoint(robot_id: int, update: RobotNextRoomUpdate): 

    return update_robot_next_room(robot_id = robot_id, next_room = update.next_room)

# PATCH unlock robot door command at /robot/{robot_id}/door (Used by user)
@router.patch("/robot/{robot_id}/door")
def unlock_robot_door_endpoint(robot_id: int, delivery_id: int, recipient_id: int, pin: str): 

    if pin == get_delivery_pin(r_id= recipient_id, d_id= delivery_id):
        update_robot_door_status(robot_id=robot_id, door_status="open")
        
    return get_robot_door_status(robot_id=robot_id)

# PATCH robot's door command at /robot/{robot_id}/door (Used by robot)
@router.patch("/robot/{robot_id}/door")
def lock_robot_door_endpoint(robot_id: int): 

    r_door = get_robot_door_status(robot_id=robot_id)

    if r_door['door_status'] == 'open':
        update_robot_door_status(robot_id=robot_id, door_status="closed")
        
    return r_door