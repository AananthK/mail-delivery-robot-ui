# This file contains service functions that handle room business logic for any users
# These functions also convert lists into Pydantic models for API

from models.robot import *
from persistence.robot_dao import *
from persistence.room_dao import get_room_by_number_dao
from persistence.delivery_general_dao import get_all_deliveries_by_robot_dao
from services.utils import db_return

# helper function to find robot by ID
def find_robot(robot_id: int):
    try:
        robot = db_return(get_robot_by_id_dao(robot_id = robot_id))
    except LookupError:
        raise LookupError("Robot does not exist")
    
    return robot

# service function to create a robot
def create_robot(current_room: str):
    
    # ensure current room is valid and exists
    try:
        db_return(get_room_by_number_dao(current_room))
    except LookupError:
        raise LookupError("Room does not exist")

    r = create_robot_dao(current_room = current_room)

    new_robot = RobotStatusUpdate(robot_id = r['robot_id'], 
                          robot_status = r['robot_status'],
                          current_room = r['current_room'])
    
    return new_robot

# service function to get all robots
def get_all_robots():

    robot_list = []

    robots = get_all_robots_dao()

    for r in robots:
        print(type(r))
        robot = RobotFullView(robot_id = r['robot_id'], 
                            robot_status = r['robot_status'],
                            current_room = r['current_room'],
                            next_room = r['next_room'])
        
        robot_list.append(robot)
    
    return robot_list

# service funciton to get a robot by id
def get_robot_by_id(robot_id: int):

    r = find_robot(robot_id = robot_id)
    
    robot = RobotFullView(robot_id = r['robot_id'], 
                          robot_status = r['robot_status'],
                          current_room = r['current_room'],
                          next_room = r['next_room'])
    
    return robot

def get_robots_by_status(status: str):

    robot_list = []
    status_list = ["off", "idle", "charging", "moving"]

    # check for valid status input
    if not (status in status_list):
        raise ValueError("Invalid robot status input")

    robots = get_robots_by_status_dao(status = status)

    for r in robots:

        robot = RobotFullView(robot_id = r['robot_id'], 
                            robot_status = r['robot_status'],
                            current_room = r['current_room'],
                            next_room = r['next_room'])
        
        robot_list.append(robot)
    
    return robot_list

# service function to get robots by current room
def get_robots_by_current_room(current_room: str):

    robot_list = []
    
    # check if room exists
    room = db_return(get_room_by_number_dao(room_number = current_room))

    robots = get_robots_by_current_room_dao(current_room = room['room_number'])

    for r in robots:

        robot = RobotFullView(robot_id = r['robot_id'], 
                            robot_status = r['robot_status'],
                            current_room = r['current_room'],
                            next_room = r['next_room'])
        
        robot_list.append(robot)
    
    return robot_list

# service function to get robots by next room
def get_robots_by_next_room(next_room: str):

    robot_list = []
    
    # check if room exists
    room = db_return(get_room_by_number_dao(room_number = next_room))

    robots = get_robots_by_next_room_dao(next_room = room['room_number'])

    for r in robots:

        robot = RobotFullView(robot_id = r['robot_id'], 
                            robot_status = r['robot_status'],
                            current_room = r['current_room'],
                            next_room = r['next_room'])
        
        robot_list.append(robot)
    
    return robot_list

# service function to update robot status (robot will use this)
def update_robot_status(robot_id: int, status: str):

    status_list = ["off", "idle", "charging", "moving"]
    
    # check if robot exists
    r = find_robot(robot_id = robot_id)

    # check for valid status input
    if not (status in status_list):
        raise ValueError("Invalid robot status input")
    
    u_r = update_robot_status_dao(robot_id = robot_id, robot_new_status = status)

    # next_room is only set when robot is in moving status
    if status == "moving": 
        robot_current_room_null_dao(robot_id = robot_id)
    # all three states have robot stationary, hence it is at a current room
    else:
        robot_next_room_null_dao(robot_id = robot_id)

    updated_robot = RobotStatusUpdate(robot_id = u_r['robot_id'], 
                          robot_status = u_r['robot_status'],
                          current_room = u_r['current_room'])
    
    return updated_robot

# service function to update robot current room (robot will use this)
def update_robot_current_room(robot_id: int, current_room: str):

    # check if robot exists
    r = find_robot(robot_id = robot_id)

    # check if room exists
    room = get_room_by_number_dao(room_number = current_room)
    
    u_r = update_robot_current_room_dao(robot_id = robot_id, new_current_room = room['room_number'])

    updated_robot = RobotStatusUpdate(robot_id = u_r['robot_id'], 
                          robot_status = u_r['robot_status'],
                          current_room = u_r['current_room'])
    
    return updated_robot

# service function to update robot next room
def update_robot_next_room(robot_id: int, next_room: str):

    # check if robot exists
    r = find_robot(robot_id = robot_id)

    # check if room exists
    room = get_room_by_number_dao(room_number = next_room)
    
    r = update_robot_next_room_dao(robot_id = robot_id, new_next_room = room['room_number'])

    updated_robot = RobotNextRoomUpdate(robot_id = r['robot_id'], 
                          next_room = r['next_room'])
    
    return updated_robot

# service function to delete a robot
def delete_robot(robot_id: int):

    # check if robot exists
    r = find_robot(robot_id = robot_id)

    # ensure deletions cannot happen when a delivery is under progress by the robot
    deliveries = get_all_deliveries_by_robot_dao(robot_id = robot_id)

    for d in deliveries:
        if d['status'] != "completed":
            raise ValueError("Cannot delete robot while a delivery is underway")

    r = delete_robot_dao(robot_id = robot_id)

    d_robot = RobotDeletedView(robot_id = r['robot_id'])
    
    return d_robot