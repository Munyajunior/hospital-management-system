from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class DoctorBase(BaseModel):
    full_name: str
    specialization: str
    contact_number: str = Field(..., pattern="^\+?[0-9\s-]{8,}$")
    email: EmailStr
    address: str 

class DoctorCreate(DoctorBase):
    password: str = Field(..., min_length=8)
    

class DoctorResponse(DoctorBase):
    id: int
    contact_number: int

    class Config:
        from_attributes = True