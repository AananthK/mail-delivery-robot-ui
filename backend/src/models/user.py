# models/user.py
from pydantic import BaseModel, EmailStr, Field

from datetime import datetime
from typing import Optional
from typing import Literal

#***** input models: take in informaiton (requests) *****

# input values when user creates an account
class UserCreate(BaseModel):
    username: str
    password: str
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
class UserDashboardView(BaseModel):
    # immediate display on dashboard
    first_name: str
    last_name: str
    # personal information, visible from account overview
    email: EmailStr
    phone_number: Optional[str] = None

# output values that are visible to admins
class UserContactView(BaseModel):
    username: str
    first_name: str
    last_name: str
    role: Literal["admin", "user"]
    email: EmailStr
    phone_number: Optional[str] = None
