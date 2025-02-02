from pydantic import BaseModel, EmailStr, constr
from datetime import date
from typing import Optional

class PatientBase(BaseModel):
    """
    Base schema for a patient.
    """
    first_name: constr(min_length=2, max_length=50)
    last_name: constr(min_length=2, max_length=50)
    date_of_birth: date
    gender: constr(min_length=1, max_length=10)
    phone: constr(min_length=7, max_length=15)
    email: Optional[EmailStr]
    address: str

class PatientCreate(PatientBase):
    """
    Schema for creating a patient.
    """
    pass

class PatientResponse(PatientBase):
    """
    Schema for returning patient data.
    """
    id: int
    assigned_doctor_id: Optional[int]

    class Config:
        orm_mode = True
