from pydantic import BaseModel, EmailStr
from typing import Optional

class DoctorBase(BaseModel):
    full_name: str
    specialization: str  # Ensure consistency with the database column name
    contact_number: str
    email: EmailStr

class DoctorCreate(DoctorBase):
    user_id: int  # Link the doctor to a user account

class DoctorResponse(DoctorBase):
    id: int
    user_id: Optional[int] = None  # Allow flexibility in responses

    class Config:
        from_attributes = True
