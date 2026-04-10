from models.delivery import DeliveryRobotView
from persistence.delivery_general_dao import (
    get_ready_deliveries_for_robot_dao,
    get_all_deliveries_by_robot_dao,
    get_delivery_by_id_for_robot_dao,
    update_delivery_status_dao
    )
from services.robot_service import find_robot
from services.utils import db_return

# service function to retrieve list of today's "ready" deliveries for robot
def get_ready_deliveries_for_robot(robot_id: int):

    # check if robot exists
    r = find_robot(robot_id = robot_id)

    deliveries = get_ready_deliveries_for_robot_dao(robot_id = robot_id)

    d_list = []
    for delivery in deliveries:
        d = DeliveryRobotView(delivery_id = delivery['delivery_id'],
                              status = delivery['status'],
                              room_number = delivery['room_number'],
                              recipient_confirmed = delivery['recipient_confirmed'])
        
        d_list.append(d)

    return d_list

# service function for robot to update delivery status
def robot_update_delivery_status(robot_id: int, delivery_id: int, status: str):

    # check if robot exists
    r = find_robot(robot_id = robot_id)

    # check if delivery exists for robot
    delivery = db_return(get_delivery_by_id_for_robot_dao(robot_id=r['robot_id'], 
                                                          delivery_id = delivery_id))
    
    if delivery['status'] not in {"ready", "in_progress"}:
        raise PermissionError("Robot can only update deliveries that are ready or in progress")
    
    # ensure status update by robot is a valid update
    if status not in {"in_progress", "unloading", "error"}:
        raise ValueError("Incorrect status update by robot. Accept only \"in_progress\", \"unloading\", \"error\"")

    updated_delivery = update_delivery_status_dao(delivery_id = delivery['delivery_id'], 
                                                  status = status)
    
    return DeliveryRobotView(delivery_id = updated_delivery['delivery_id'],
                              status = updated_delivery['status'],
                              room_number = updated_delivery['room_number'],
                              recipient_confirmed = updated_delivery['recipient_confirmed'])