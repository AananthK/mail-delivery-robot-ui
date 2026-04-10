from fastapi import APIRouter, Query, HTTPException, Depends
from models.delivery import DeliveryRobotView
from services.admin_service import admin_assign_robot_deliveries

from api.api_security import verify_api_key

router = APIRouter(
    tags=["Admin API Endpoints"],
    dependencies=[Depends(verify_api_key)]
)

#----- Get endpoints -----
# GET = retrieve a resource

# GET robot's status at /robot/{robot_id}/status
@router.get("/admin/robot/{robot_id}/deliveries", response_model = list[DeliveryRobotView])

def get_robot_status_endpoint(admin_id: int, robot_id: int): 

    return admin_assign_robot_deliveries(admin_id = admin_id, robot_id = robot_id)