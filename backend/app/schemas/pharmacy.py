from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PrescriptionBase(BaseModel):
    patient_id: int
    doctor_id: int
    medication_name: str
    dosage: str
    instructions: str

class PrescriptionCreate(PrescriptionBase):
    pass

class PrescriptionResponse(PrescriptionBase):
    id: int
    prescribed_date: datetime
    is_dispensed: bool

    class Config:
        from_attributes = True
