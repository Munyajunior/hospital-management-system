from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import Optional

class PatientBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    date_of_birth: date
    gender: str = Field(..., pattern="^(Male|Female|Other)$")
    contact_number: str = Field(..., pattern="^\+?[0-9\s-]{8,}$")
    address: str
    email: EmailStr

class PatientCreate(PatientBase):
    assigned_doctor_id: Optional[int] = None
    emergency: bool = False  # Default is false, true for emergency cases
    
class PatientUpdate(BaseModel):
    category: str

class PatientResponse(PatientBase):
    id: int
    assigned_doctor_id: Optional[int] = None
    registered_by: int
    category: str
    emergency: bool
    
class PatientCreateResponse(PatientBase):
    id: int
    assigned_doctor_id: Optional[int] = None
    registered_by: int
    category: str
    emergency: bool
    password: str
    class Config:
        from_attributes = True
