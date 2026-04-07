from models.delivery import DeliveryQuickView, DeliveryFullView
from models.user import UserContactView

# Helper functions used throughout services

# checks if a DB query returns a record
# only for single-record DAO functions, those that return lists are handled in the API-layer
def db_return(db_query_result):
    if db_query_result is None:
        raise LookupError("Not found in database.")
    return db_query_result

# turn dict_lists from sql cursor into JSON-value Pydantic Model_lists
def dict_list_to_model_list(model_type: str, d_list: list[dict]):

    model = [] # start with an empty list

    if model_type == 'quick_view':
        for dl in d_list: # for every row (dict: d1) in d_list

            # assigning dict_list values to Pydantic Model m
            m = DeliveryQuickView(delivery_id = dl['delivery_id'], 
                                  status = dl['status'], 
                                  delivery_time = dl['delivery_time'],
                                  created_at = dl['created_at'], 
                                  last_updated_at= dl['last_updated_at'])
            
            # updating the completed_at field using 'status' from record
            if m.status == 'complete':
                m.completed_at = dl['last_updated_at']

            model.append(m) # add model to model_list
        
        return model
            
    elif model_type == 'full_view':
           
        for dl in d_list:
            m = DeliveryFullView(delivery_id = dl['delivery_id'], 
                                 status = dl['status'],
                                 admin_user_id = dl['admin_user_id'],
                                 sender_name = dl['sender_name'],
                                 recipient_id = dl['recipient_user_id'],
                                 assigned_robot = dl['assigned_robot'],
                                 room_number = dl['room_number'],
                                 delivery_time = dl['delivery_time'],
                                 created_at = dl['created_at'], 
                                 last_updated_at= dl['last_updated_at'])
            
            if m.status == 'complete':
                m.completed_at = dl['last_updated_at']

            model.append(m)
            
        return model
    
    raise ValueError("Unkown delivery view type")

# Convert database results to UserContactView model
def account_to_user_contact_view(account: dict):
    return UserContactView(user_id = account['user_id'],
                           username = account['username'],
                           first_name = account['first_name'],
                           last_name = account['last_name'],
                           user_role = account['user_role'],
                           email = account['email'],
                           phone_number = account['phone_number'])

