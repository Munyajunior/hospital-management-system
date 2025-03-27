from pydantic import BaseModel, EmailStr, Field
from typing import Optional
class UserBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    role: str = Field(..., pattern="^(admin|nurse|doctor|pharmacist|lab_technician|radiologist|icu)$")

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserResponse(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True
        
class LoginRequest(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str 
    sub: int

class TokenData(BaseModel):
    email: str | None = None
    

class AllUserResponse(UserResponse):
    address: Optional[str] = None
    contact_number: Optional[str] = None
    
   
class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class IsActive(BaseModel):
    is_active: bool
    
class UserUpdate(BaseModel):
    password: str
    email: EmailStr