#services/admin_service
# This file contains functional methods only executable by authenticated admins

from models.user import UserContactView, UserUpdateContactInfo
from persistence.account_dao import *
from services.delivery_admin_service import *
from services.robot_service import *
from services.room_service import *
from services.user_service import user_exists
from services.security import hash_password
from services.utils import db_return, account_to_user_contact_view

from typing import Optional
from typing import Literal

#----- Helper Functions -----
# Check if admin exists
def admin_exists(admin_id):
    user = get_account_by_id_dao(admin_id)
    return user is not None and user['user_role'] == "admin"

#----- User: Account Management -----

#** 1. View Account

# service function for user to view their own account
def admin_view_account(admin_id: int):

    if not admin_exists(admin_id):
        raise PermissionError("Only authorized persons can view their accounts")
    
    account = get_account_by_id_dao(id = admin_id)

    return account_to_user_contact_view(account = account)

#** 2. Update Account

# service function for admin to change password
def admin_update_password(admin_id: int, new_pword: str):

    if not admin_exists(admin_id):
        raise PermissionError("Only authorized persons can update passwords")
    
    account_id = update_account_password_dao(user_id = admin_id, new_password_hash = hash_password(new_pword))['user_id']

    return account_to_user_contact_view(get_account_by_id_dao(id = account_id))

# service function for user to change email
def admin_update_email(admin_id: int, u_email: str):

    if not admin_exists(admin_id):
        raise PermissionError("Only authorized persons can update emails")
    
    account = update_account_contact_info_dao(user_id = admin_id, email = u_email)

    updated_account = UserUpdateContactInfo(user_id = account['user_id'],
                                            email = account['email'])

    return updated_account

# service function for user to change phone number
def admin_update_phone(admin_id: int, u_phone: str):

    if not admin_exists(admin_id):
        raise PermissionError("Only authorized persons can update phone numbers")
    
    account = update_account_contact_info_dao(user_id = admin_id, phone_number = u_phone)

    updated_account = UserUpdateContactInfo(user_id = account['user_id'],
                                            phone_number = account['phone_number'])

    return updated_account

#----- Admin: User Management -----

#** 1. User Creation
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
    if (get_account_by_username_dao(uname)):
        raise ValueError(f"Account, {uname} already exists")
    
    account = create_account_dao(username = uname,
                            password_hash = hash_password(pword),
                            first_name = fname,
                            last_name = lname,
                            user_role = "user",
                            email = e_mail,
                            phone_number = p_number)
    
    return account_to_user_contact_view(account)

#** 2. User Viewing
# retrieve all recipients
def get_all_users(admin_id: int):

    all_users = []

    if not admin_exists(admin_id):
        raise PermissionError("Only Admin can view users")
    
    recipients = get_all_recipients_dao()

    for user in recipients:
        all_users.append(account_to_user_contact_view(user))

    return all_users

# retrieve account by id
def get_user_by_id(admin_id, user_id):
    if not admin_exists(admin_id):
        raise PermissionError("Only Admin can view users")

    account = get_account_by_id_dao(id = user_id)
    
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
    if not parts:   # if name is an empty string
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

#** 3. User Updates
def admin_update_user_password(admin_id: int, user_id: int, new_pword: str):

    if not admin_exists(admin_id):
        raise PermissionError("Only authorized persons can update passwords")
    
    if not user_exists(user_id):
        raise PermissionError("User does not exist")
    
    account = update_account_password_dao(user_id = user_id, new_password_hash = hash_password(new_pword))

    return account_to_user_contact_view(get_account_by_id_dao(id = account['user_id']))
    
#** 4. User Deletion
def admin_delete_user(admin_id: int, user_id: int):

    if not admin_exists(admin_id):
        raise PermissionError("Only admins persons can delete accounts")
    
    if get_deliveries_by_recipient_for_admin_dao(admin_id = admin_id, recipient_id = user_id) is not None or get_deliveries_for_admin_dao(admin_id = user_id) is not None:
        raise PermissionError("Cannot delete account involved in an ongoing delivery")
    
    return delete_account_dao(user_id = user_id)

#----- Admin: Delivery Management -----

#** 1. Delivery Creation
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

    return create_delivery( a_id = admin_id, 
                            rec_id = recipient_id,
                            room = room_number,
                            del_time = delivery_time,
                            s_name = sender_name, 
                            s_address = sender_address, 
                            s_email = sender_email,
                            s_phone = sender_phone,
                            robot = robot)


#** 2. Delivery Viewing

# admin to view all administered deliveries
def admin_view_deliveries(admin_id: int, m_type: Literal['quick_view', 'full_view']):

    if not admin_exists(admin_id):
        raise PermissionError("Only Admin can view all adminstered deliveries")
    
    return get_deliveries_for_admin(m_type, admin_id)

# admin to view delivery by id
def admin_view_delivery_by_id(admin_id: int, d_id: int, m_type: Literal['quick_view', 'full_view']):

    if not admin_exists(admin_id):
        raise PermissionError("Only Admin/User can view adminstered delivery by ID.")
    
    return get_delivery_by_id_for_admin(m_type, admin_id, d_id)

# admin to view deliveries by user (recipient)
def admin_view_deliveries_by_user(admin_id: int, user_id: int, m_type: Literal['quick_view', 'full_view']):

    if not admin_exists(admin_id):
        raise PermissionError("Only Admin/User can view adminstered delivery by user.")
    
    return get_deliveries_by_recipient_for_admin(m_type, admin_id, user_id)

# admin to view deliveries by sender
def admin_view_deliveries_by_sender(admin_id: int, sender: str, m_type: Literal['quick_view', 'full_view']):

    if not admin_exists(admin_id):
        raise PermissionError("Only Admin/User can view adminstered delivery by sender.")
    
    return get_deliveries_by_sender_for_admin(m_type, admin_id, sender)

# admin to view deliveries by date
def admin_view_deliveries_by_date(admin_id: int, day: datetime, m_type: Literal['quick_view', 'full_view']):

    if not admin_exists(admin_id):
        raise PermissionError("Only Admin/User can view adminstered delivery by date.")
    
    return get_deliveries_by_date_for_admin(m_type, admin_id, day)

# admin to view deliveries by room
def admin_view_deliveries_by_room(admin_id: int, room: str, m_type: Literal['quick_view', 'full_view']):

    if not admin_exists(admin_id):
        raise PermissionError("Only Admin/User can view adminstered delivery by room.")
    
    return get_deliveries_by_room_for_admin(m_type, admin_id, room)


#** 3. Delivery Updates

#admin to change delivery status
def admin_change_delivery_status(admin_id: int, d_id: int, status: str):

    if not admin_exists(admin_id):
        raise PermissionError("Only Admin can change delivery rooms")

    return update_delivery_by_admin(a_id = admin_id, d_id = d_id, u_status = status)

# admin to change delivery room
def admin_change_delivery_room(admin_id: int, d_id: int, room: str):

    if not admin_exists(admin_id):
        raise PermissionError("Only Admin can change delivery rooms")

    return update_delivery_by_admin(a_id = admin_id, d_id = d_id, u_room = room)

# admin to change the time of delivery
def admin_change_delivery_time(admin_id: int, d_id: int, time: datetime):

    if not admin_exists(admin_id):
        raise PermissionError("Only Admin/User can change delivery times")
    
    return update_delivery_by_admin(a_id = admin_id, d_id = d_id, u_time = time)

# admin to mark delivery as complete
def admin_mark_as_complete(admin_id: int, d_id: int,):
    if not admin_exists(admin_id):
        raise PermissionError("Only Admin/Robot can change the status of adminstered deliveries")
    
    return update_delivery_by_admin(a_id = admin_id, d_id = d_id, u_status = "complete")

# admin to assign robot to delivery
def admin_assign_robot(admin_id: int, d_id: int, r_id):

    if not admin_exists(admin_id):
        raise PermissionError("Only Admin can assign robots to adminstered deliveries")
    
    return update_delivery_robot(a_id = admin_id, d_id = d_id, r_id = r_id)


#** 4. Delivery Deletion
def admin_delete_delivery(admin_id: int, d_id: int):
    if not admin_exists(admin_id):
        raise PermissionError("Only Admin can view all adminstered deliveries")
    
    return delete_delivery(a_id = admin_id, d_id = d_id)

#----- Admin: Robot Management ----- 

#** 1. Robot Creation
def admin_create_robot(admin_id: int, current_room: str):

    if not admin_exists(admin_id):
        raise PermissionError("Only Admin can view all adminstered deliveries")
    
    return create_robot(current_room = current_room)

#** 2. Robot Viewing
def admin_view_all_robots(admin_id: int):

    if not admin_exists(admin_id):
        raise PermissionError("Only Admin can view robots")
    
    return get_all_robots()

def admin_view_robot_by_id(admin_id: int, r_id: int):

    if not admin_exists(admin_id):
        raise PermissionError("Only Admin can view robots")
    
    return get_robot_by_id(robot_id = r_id)

def admin_view_robots_by_current_room(admin_id: int, current_room: str):

    if not admin_exists(admin_id):
        raise PermissionError("Only Admin can view robots")
    
    return get_robots_by_current_room(current_room = current_room)

def admin_view_robots_by_next_room(admin_id: int, next_room: str):

    if not admin_exists(admin_id):
        raise PermissionError("Only Admin can view robots")
    
    return get_robots_by_next_room(next_room = next_room)

#** 3. Robot Updates
# service function to assign delivery to a robot
def admin_assign_robot_next_delivery(admin_id: int, robot_id: int):

    if not admin_exists(admin_id):
        raise PermissionError("Only Admin can assign delivery to robots")

    delivery = get_ready_deliveries_dao(admin_id)[0] # get first item in the python list

    admin_change_delivery_status(admin_id = admin_id, d_id= delivery['delivery_id'], status = "in_progress")

    update_robot_next_room(robot_id= robot_id, new_next_room = delivery['room_number'])

    dView = DeliveryQuickView(delivery_id = delivery['delivery_id'], 
                         status = delivery['status'], 
                         delivery_time = delivery['delivery_time'],
                         created_at = delivery['created_at'], 
                         last_updated_at= delivery['last_updated_at'],
                         completed_at=None)
    
    return dView

#** Robot Deletion
# service function to delete robot
def admin_delete_robot(admin_id: int, robot_id: int):

    if not admin_exists(admin_id):
        raise PermissionError("Only Admin can delete robots")

    return delete_robot(robot_id= robot_id)

#----- Admin: Room Management -----

#** 1. Room Creation
def admin_create_room(admin_id: int, room_number: str, floor_number: str):

    if not admin_exists(admin_id):
        raise PermissionError("Only Admin can create rooms")
    
    return create_room(room_num = room_number, floor_num = floor_number)

#** 2. Room Deletion
def admin_delete_room(admin_id: int, room_number):

    if not admin_exists(admin_id):
        raise PermissionError("Only Admin can delete rooms")
    
    return delete_room(room_num = room_number)



