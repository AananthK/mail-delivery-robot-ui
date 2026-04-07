#services/user_service
# This file contains functional methods only executable by authenticated users (recipients)

from models.user import UserContactView, UserUpdateContactInfo
from persistence.account_dao import *
from services.delivery_recipient_service import *
from services.robot_service import *
from services.room_service import *
from services.security import hash_password
from .utils import db_return, account_to_user_contact_view

from typing import Optional, Literal

#----- Helper Functions -----
# Check if admin exists
def user_exists(user_id: int):
    user = get_account_by_id_dao(id=user_id)
    return user is not None and user['user_role'] == "user"

#----- User: Account Management -----

#** 1. View Account

# service function for user to view their own account
def user_view_account(user_id: int):

    if not user_exists(user_id):
        raise PermissionError("Only authorized persons can view their accounts")
    
    account = get_account_by_id_dao(id = user_id)

    return account_to_user_contact_view(account = account)

# service function for user to view an admin account
def user_view_admin(user_id: int, admin_id: int):
    if not user_exists(user_id):
        raise PermissionError("Only authorized persons can view other accounts")
    
    account = get_account_by_id_dao(id = admin_id)

    return account_to_user_contact_view(account = account)

#** 2. Update Account

# service function for user to change password
def user_update_user_password(user_id: int, new_pword: str):

    if not user_exists(user_id):
        raise PermissionError("Only authorized persons can update passwords")
    
    account_id = update_account_password_dao(user_id = user_id, new_password_hash = hash_password(new_pword))['user_id']

    return account_to_user_contact_view(get_account_by_id_dao(id = account_id))

# service function for user to change email
def user_update_email(user_id: int, u_email: str):

    if not user_exists(user_id):
        raise PermissionError("Only authorized persons can update emails")
    
    account = update_account_contact_info_dao(user_id = user_id, email = u_email)

    updated_account = UserUpdateContactInfo(user_id = account['user_id'],
                                            email = account['email'])

    return updated_account

# service function for user to change phone number
def user_update_phone(user_id: int, u_phone: str):

    if not user_exists(user_id):
        raise PermissionError("Only authorized persons can update phone numbers")
    
    account = update_account_contact_info_dao(user_id = user_id, phone_number = u_phone)

    updated_account = UserUpdateContactInfo(user_id = account['user_id'],
                                            phone_number = account['phone_number'])

    return updated_account

#----- User: Delivery Management -----

#** 1. View Delvieries
def user_view_deliveries(user_id: int, m_type: Literal['quick_view', 'full_view']):

    if not user_exists(user_id):
        raise PermissionError("Only authorized persons can view their deliveries")
    
    return get_deliveries_for_recipient(m_type, user_id)

# user to view delivery by id
def user_view_delivery_by_id(user_id: int, d_id: int, m_type: Literal['quick_view', 'full_view']):

    if not user_exists(user_id):
        raise PermissionError("Only Admin/User can view adminstered delivery by ID.")
    
    return get_delivery_by_id_for_recipient(m_type, user_id, d_id)

# user to view deliveries by admin 
def user_view_deliveries_by_admin(user_id: int, admin_id: int, m_type: Literal['quick_view', 'full_view']):

    if not user_exists(user_id):
        raise PermissionError("Only Admin/User can view adminstered delivery by admin.")
    
    return get_deliveries_by_admin_for_recipient(m_type = m_type, r_id = user_id, a_id = admin_id)

# user to view deliveries by sender
def user_view_deliveries_by_sender(user_id: int, sender: str, m_type: Literal['quick_view', 'full_view']):

    if not user_exists(user_id):
        raise PermissionError("Only Admin/User can view adminstered delivery by sender.")
    
    return get_deliveries_by_sender_for_recipient(m_type = m_type, r_id = user_id, s_name = sender)

# user to view deliveries by date
def user_view_deliveries_by_date(user_id: int, day: datetime, m_type: Literal['quick_view', 'full_view']):

    if not user_exists(user_id):
        raise PermissionError("Only Admin/User can view adminstered delivery by date.")
    
    return get_deliveries_by_date_for_recipient(m_type, user_id, day)

# user to view deliveries by room
def user_view_deliveries_by_room(user_id: int, room: str, m_type: Literal['quick_view', 'full_view']):

    if not user_exists(user_id):
        raise PermissionError("Only Admin/User can view adminstered delivery by room.")
    
    return get_deliveries_by_room_for_recipient(m_type = m_type, r_id= user_id, room = room)

# user to get delivery pin
def user_get_delivery_pin(user_id: int, delivery_id: int):

    if not user_exists(user_id):
        raise PermissionError("Only User can retrieve their delivery pin.")
    
    return get_delivery_pin(r_id = user_id, d_id = delivery_id)

#** 3. Delivery Updates

# user to change delivery room
def user_change_delivery_room(user_id: int, d_id: int, room: str):

    if not user_exists(user_id):
        raise PermissionError("Only Admin/User can change delivery rooms")

    return change_delivery_room_recipient(r_id = user_id, d_id = d_id, room_id = room)

# user to change the time of delivery
def user_change_delivery_time(user_id: int, d_id: int, time: datetime):

    if not user_exists(user_id):
        raise PermissionError("Only Admin/User can change delivery times")
    
    return change_delivery_time_recipient(r_id = user_id, d_id = d_id, time = time)

# user to deny a delivery
def user_deny_delivery(user_id: int, d_id: int):

    if not user_exists(user_id):
        raise PermissionError("Only User can deny a delivery")
    
    return deny_delivery_recipient(r_id = user_id, d_id = d_id)