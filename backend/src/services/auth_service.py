# auth_service.py: module to handle login and token generation

from persistence.account_dao import get_account_by_username_dao
from services.security import verify_password
from models.user import LoginResponse


def user_login(username:str, password:str):
    
    account = get_account_by_username_dao(username = username)

    if not account or not verify_password(password, account['password_hash']):
        raise ValueError("Invalid login credentials")

    verified_user = LoginResponse(user_id = account['user_id'],
                                  user_role = account['user_role'],
                                  first_name = account['first_name'],
                                  last_name = account['last_name'],
                                  username = account['username'],
                                  email = account['email'],
                                  phone_number = account['phone_number'])

    return verified_user