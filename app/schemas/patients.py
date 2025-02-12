from pydantic import BaseModel
from datetime import date
from typing import Optional

class PatientBase(BaseModel):
    full_name: str
    date_of_birth: date
    gender: str
    contact_number: str
    address: Optional[str] = None
    medical_history: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class PatientResponse(PatientBase):
    id: int
    assigned_doctor_id: Optional[int] = None

    class Config:
        from_attributes = True
