from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    role: str = Field(..., pattern="^(admin|nurse|doctor|pharmacy|lab|radiologist|icu)$")

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