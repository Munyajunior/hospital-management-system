from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    role: str = Field(..., pattern="^(admin|nurse|doctor|pharmacist|lab_technician|radiologist|icu)$")

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    profile_picture: Optional[str] = None # URL to access the image
    contact_number: str
    address: str
    date_of_birth: Optional[datetime] = None
    
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
    
class ProfileUpdateResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    address: str
    contact_number: str
    class Config:
        from_attributes = True

class NotificationSettings(BaseModel):
    email: bool = True
    sms: bool = False
    push: bool = True
    appointment_reminders: bool = True
    medication_alerts: bool = True

class DisplaySettings(BaseModel):
    theme: str = "system"  # light/dark/system
    font_size: int = 14
    density: str = "normal"  # compact/normal/comfortable

class SecurityQuestion(BaseModel):
    question: str
    answer: str  # Will be hashed before storage

class UserSettingsUpdate(BaseModel):
    notifications: Optional[NotificationSettings] = None
    display: Optional[DisplaySettings] = None