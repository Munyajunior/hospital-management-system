from pydantic import BaseModel, Field
from datetime import date

class PatientBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    date_of_birth: date
    gender: str = Field(..., pattern="^(Male|Female|Other)$")
    contact_number: str = Field(..., pattern="^\+?[0-9\s-]{8,}$")
    address: str = Field(..., min_length=5)  # Required (matches model)
    medical_history: str | None = None

class PatientCreate(PatientBase):
    assigned_doctor_id: int | None = None  # Allow assigning a doctor during registration
    pass

class PatientResponse(PatientBase):
    id: int
    assigned_doctor_id: int | None = None
    registered_by: int  # Added missing field from model

    class Config:
        from_attributes = True