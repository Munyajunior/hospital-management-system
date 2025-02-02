from pydantic import BaseModel
from typing import Optional
from models.user import UserRole

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: str
    role: Optional[UserRole] = None

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    role: UserRole

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: UserRole
