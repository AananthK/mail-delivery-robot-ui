from models.user import UserContactView
from persistence.account_dao import *
from services.delivery_service import *
from services.security import hash_password
from .utils import db_return

from typing import Optional
from typing import Literal

#----- Helper Functions -----
# Check if admin exists
def admin_exists(admin_id):
    user = get_account_by_id_dao(admin_id)
    return user is not None and user['user_role'] == "admin"

# Convert database results to UserContactView model
def account_to_user_contact_view(account: dict):
    return UserContactView(user_id = account['user_id'],
                           username = account['username'],
                           first_name = account['first_name'],
                           last_name = account['last_name'],
                           role = account['user_role'],
                           email = account['email'],
                           phone_number = account['phone_number'])

#----- Admin Functions -----
# service function to create user -- can only be done by an existing admin
def create_user( admin_id: int,
                 uname: str,
                 pword: str,
                 fname: str,
                 lname: str,
                 e_mail: str,
                 p_number: str
                 ):

    # check to see if admin exists
    if not admin_exists(admin_id):
        raise PermissionError("Only Admins can create users")
    
    # check to see if username is unique
    if (not get_account_by_username_dao(uname)):
        raise ValueError(f"Account, {uname} already exists")
    
    account = create_account_dao(username = uname,
                            password_hash = hash_password(pword),
                            first_name = fname,
                            last_name = lname,
                            user_role = "user",
                            email = e_mail,
                            phone_number = p_number)
    
    return account_to_user_contact_view(account)

#----- Admin: User Searching -----

# retrieve account by id
def get_user_by_id(admin_id, user_id):
    if not admin_exists(admin_id):
        raise PermissionError("Only Admin can view users")

    account = get_account_by_id_dao(user_id)
    
    if not account:
        raise ValueError("Account not found")

    return account_to_user_contact_view(account)

# retrieve account by username
def get_user_by_username(admin_id, username):

    if not admin_exists(admin_id):
        raise PermissionError("Only Admin can view users")
    
    account = get_account_by_username_dao(username)
    
    if not account:
        raise ValueError("Account not found")

    return account_to_user_contact_view(account)

# retrieve account by name
def get_user_by_name(admin_id: int, name: str):
    if not admin_exists(admin_id):
        raise PermissionError("Only Admin can view users")

    # when admin types a full name with a space
    # if no space, admin input is searched as a single term
    parts = name.strip().split()
    if not parts:
        return []

    # If admin types multiple names, search each term and merge results
    seen_ids = set() # set has no duplicates
    results = []

    for term in parts:
        for row in search_accounts_by_name_dao(term):
            uid = row["user_id"]
            if uid not in seen_ids:
                seen_ids.add(uid)
                results.append(account_to_user_contact_view(row))

    return results

#----- Admin: Delivery Management -----

# admin to create a delivery
def admin_create_delivery(admin_id: int,
                          recipient_id: int,
                          room_number: str,
                          delivery_time: datetime,
                          sender_name: str, 
                          sender_address: str, 
                          sender_email: str,
                          sender_phone: Optional[str]=None,
                          robot: Optional[int]=None):
    
    if not admin_exists(admin_id):
        raise PermissionError("Only Admin can create deliveries")

    return create_delivery( ad_id = admin_id, 
                            rec_id = recipient_id,
                            room = room_number,
                            del_time = delivery_time,
                            s_name = sender_name, 
                            s_address = sender_address, 
                            s_email = sender_email,
                            s_phone = sender_phone,
                            robot = robot)

# admin to view all administered deliveries
def admin_view_deliveries(admin_id: int, m_type: Literal['quick_view', 'full_view']):

    if not admin_exists(admin_id):
        raise PermissionError("Only Admin can view all adminstered deliveries")
    
    return get_deliveries_by_admin(m_type, admin_id)


     



