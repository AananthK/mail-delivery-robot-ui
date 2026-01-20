# models/delivery.py

#input models: take in informaiton (requests)
class DeliveryCreateRequest:
    def __init__ (self, 
                  admin_id 
                 ):
        #delivery_id and created_at attributes are handled in database
        self.admin_id = admin_id

class DeliveryAddress:
    def __init__ (self,
                  sender_name,
                  sender_address,
                  sender_email,
                  sender_phone,

                  receiver_name,
                  receiver_room,
                  receiver_email,
                  receiver_phone
                ):

        self.sender_name = sender_name
        self.sender_address = sender_address
        self.sender_email = sender_email
        self.sender_phone = sender_phone

        self.receiver_name = receiver_name
        self.receiver_room = receiver_room
        self.receiver_email = receiver_email
        self.receiver_phone = receiver_phone

class DeliveryUpdateRequest:
    def __init__ (self,
                  status = None,  
                  delivery_time = None
                ):
        self.status = status
        self.delivery_time = delivery_time

#internal/domain model: used in backend
class Delivery:
    def __init__(self, delivery_id, admin_id, status, created_at, last_updated_at, delivery_time=None):
        self.delivery_id = delivery_id
        self.admin_id = admin_id
        self.status = status
        self.created_at = created_at
        self.last_updated_at = last_updated_at
        self.delivery_time = delivery_time

#ouput models: return information (what the client sees)
class DeliveryView:
    def __init__(self, delivery_id, status, created_at, completed_at=None):
        self.delivery_id = delivery_id
        self.status = status
        self.created_at = created_at
        self.completed_at = completed_at # can be time of delivery completion