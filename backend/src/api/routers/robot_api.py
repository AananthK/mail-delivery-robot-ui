from fastapi import APIRouter, Query, HTTPException
from models.room import RoomView
from services.robot_service import *
from services.room_service import get_room_by_number
from services.admin_service import get_robot_by_id

router = APIRouter()

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