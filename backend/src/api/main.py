from fastapi import FastAPI
from models.delivery import DeliveryCreateRequest, DeliveryView
from services.delivery_service import create_delivery

app = FastAPI()

# POST method to create deliveries using pydantic model (DeliveryCreateRequest)
@app.post("/deliveries")
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

    return created_delivery # DeliveryView object returned after this API call