# models/user.py
from pydantic import BaseModel, EmailStr, Field

from datetime import datetime
from typing import Optional
from typing import Literal

#***** input models: take in informaiton (requests) *****

# input values when user creates an account
class UserCreate(BaseModel):
    username: str
    password: str = Field(min_length = 8, max_length = 128)
    # when creating a user, password must be minimum 8 characters, and max 128
    first_name: str
    last_name: str
    role: str
    email: EmailStr
    phone_number: Optional[str] = None

# input values when user wants to update contact info
class UserUpdateContactInfo(BaseModel):    
    # modifiable contact info
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None

# input values when user wants to update password
class UserNewPassword(BaseModel):
    old_password: str
    # new password
    new_password: str

# input values when user logs in
class LoginRequest(BaseModel):
    username: str
    password: str

#***** ouput models: return information (what the client sees) *****

# output values when user logs in
class LoginResponse(BaseModel):
    # important attributes for frontend behaviour
    user_id: int
    user_role: Literal["admin", "user"]
    # immediate display on dashboard
    first_name: str
    last_name: str
    # personal information, visible from account overview
    username: str
    email: EmailStr
    phone_number: Optional[str] = None

# output values that are visible to admins
class UserContactView(BaseModel):
    user_id: int
    username: str
    first_name: str
    last_name: str
    user_role: Literal["admin", "user"]
    email: EmailStr
    phone_number: Optional[str] = None
