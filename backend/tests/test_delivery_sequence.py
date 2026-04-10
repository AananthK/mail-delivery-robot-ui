import os
import sys

# run this file from root (imported backend modules tied to src)
CURRENT_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "src"))
sys.path.insert(0, SRC_DIR)

from services.robot_delivery_service import robot_update_delivery_status, get_ready_deliveries_for_robot
from services.robot_service import update_robot_status, update_robot_door_status
from services.admin_service import update_delivery_by_admin, admin_view_delivery_by_id

from datetime import datetime, timedelta

admin_id = 5
delivery_id = 8 # already exists in the DB
recipient_id = 7
robot_id = 1
room_id = "ENG602"

d_list = []

test_d = admin_view_delivery_by_id(m_type = "quick_view", admin_id=admin_id, d_id=delivery_id)
test_d_time = test_d.delivery_time

update_time = test_d_time + timedelta(minutes=5)

# Before logging into Streamlit
def init_delivery():
    try:
        # incase robot is in-use during testing
        update_robot_status(robot_id=robot_id, status="off")

        # admin updates (delivery to a new time)
        update_delivery_by_admin(a_id=admin_id, d_id=delivery_id, u_time=update_time, u_status="ready")

        print(f"Delivery {delivery_id} ready! Log into {recipient_id}. Confirm you will be receiving delivery {delivery_id}.")
    except Exception as e:
        print(e)

# After User logs into Streamlit and confirms they will be recieving mail
def deploy_robot():
    try:
        d_list = get_ready_deliveries_for_robot(robot_id=robot_id)
        found = any(d.delivery_id == delivery_id for d in d_list)

        if not found:
            raise LookupError(f"Delivery {delivery_id} not found. Was not created + ready + recipient_confirmed = True")
        
        update_robot_door_status(robot_id=robot_id, door_status="close")
        update_robot_status(robot_id=robot_id, status="moving")
        robot_update_delivery_status(robot_id=robot_id, delivery_id=delivery_id, status="in_progress")
        print(f"Robot {robot_id} has been deployed!")
    except Exception as e:
        print(e)

def retrieve_mail():
    try:
        # robot reaches room
        update_robot_status(robot_id=robot_id, status="idle")
        robot_update_delivery_status(robot_id=robot_id, delivery_id=delivery_id, status="unloading")

        # Go to StreamLit and interact with Pick-up delivery module
        print(f"Robot {robot_id} has arrived! Retrieve Delivery {delivery_id}. Interact with the Modal.")
    except Exception as e:
        print(e)

def accept_mail():
    try:
        # After recipient enters pin and closes robot
        print(f"Recipient {recipient_id} accepts Delivery {delivery_id}!")
        d_list = get_ready_deliveries_for_robot(robot_id=robot_id)

        if len(d_list) > 0:
            update_robot_status(robot_id=robot_id, status="moving")
        else:
            update_robot_status(robot_id=robot_id, status="off")
        
    except Exception as e:
        print(e)