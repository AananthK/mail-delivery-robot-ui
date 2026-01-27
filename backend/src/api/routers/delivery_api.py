from fastapi import APIRouter, Query, HTTPException
from models.delivery import DeliveryCreateRequest, DeliveryUpdateRequest, DeliveryQuickView, DeliveryFullView
from services.delivery_service import *
from datetime import datetime
from typing import Union

router = APIRouter()

#----- GET endpoints -----
@router.get("/", response_model=Union[list[DeliveryQuickView],list[DeliveryFullView]]) # GET all deliveries at address: /deliveries
# Response from endpoint can be either view depending on query
def get_all_deliveries_endpoint(
    view: str = Query("quick_view", enum=["quick_view", "full_view"])): # User can specify view type with query (quick_view by default): Ex. /deliveries?view=quick_view

    return get_all_deliveries(view)

@router.get("/admin/{admin_id}", response_model=Union[list[DeliveryQuickView],list[DeliveryFullView]]) 
def get_delivery_by_admin_endpoint(
    admin_id: int,
    view: str = Query("quick_view", enum=["quick_view", "full_view"])
    ):
    return get_deliveries_by_admin(view, ad_id = admin_id)

@router.get("/recipient/{recipient_id}", response_model=Union[list[DeliveryQuickView],list[DeliveryFullView]]) 
def get_delivery_by_recipient_endpoint(
    recipient_id: int,
    view: str = Query("quick_view", enum=["quick_view", "full_view"])
    ):
    return get_deliveries_by_recipient(view, r_id = recipient_id)

@router.get("/sender/{sender_name}", response_model=Union[list[DeliveryQuickView],list[DeliveryFullView]]) 
def get_delivery_by_sender_endpoint(
    sender_name: str,
    view: str = Query("quick_view", enum=["quick_view", "full_view"])
    ):
    return get_deliveries_by_sender(view, s_name = sender_name)

@router.get("/date/", response_model=Union[list[DeliveryQuickView],list[DeliveryFullView]]) 
def get_delivery_by_date_endpoint(
    date: datetime | None = Query(None),
    view: str = Query("quick_view", enum=["quick_view", "full_view"])
    ): #/deliveries/date?date=**insert date**

    if date is None:
        raise HTTPException(status_code=400, detail="date query parameter is required: /deliveries/date/?date=**insert date**")

    return get_deliveries_by_date(view, date_time = date)

@router.get("/{delivery_id}", response_model=Union[DeliveryQuickView, DeliveryFullView]) # GET delivery via delivery_id as input: Ex. /delivery/01
def get_delivery_by_id_endpoint(
    delivery_id: int,
    view: str = Query("quick_view", enum=["quick_view", "full_view"])
    ):
    return get_delivery_by_id(view, d_id = delivery_id)

#----- POST endpoints ----
# POST function to create deliveries using pydantic model (DeliveryCreateRequest)
@router.post("/", response_model=DeliveryQuickView)
def create_delivery_endpoint(new_delivery_json: DeliveryCreateRequest):
    
    # call create_delivery method from services layer
    created_delivery = create_delivery(
        ad_id = new_delivery_json.admin_id,
        rec_id = new_delivery_json.recipient_id,
        room = new_delivery_json.room_number,
        del_time = new_delivery_json.delivery_time,
        s_name = new_delivery_json.sender_name,
        s_address = new_delivery_json.sender_address,
        s_email = new_delivery_json.sender_email,
        s_phone = new_delivery_json.sender_phone,
        robot = new_delivery_json.assigned_robot
    )

    return created_delivery # DeliveryQuickView object returned after this API call

#----- DELETE endpoints ------
@router.delete("/{delivery_id}", response_model=DeliveryUpdateView)
def delete_delivery_endpoint(delivery_id: int):
    return delete_delivery(d_id = delivery_id)

#----- UPDATE endpoint -----
@router.patch("/{delivery_id}", response_model=DeliveryUpdateView)
def update_delivery_time_endpoint(delivery_id: int, update_json: DeliveryUpdateRequest):
    return update_delivery(d_id = delivery_id, 
                           u_room = update_json.room_number,
                           u_time = update_json.delivery_time,
                           u_status = update_json.status)
