from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class PrescriptionStatus(str, Enum):
    PENDING = "pending"
    DISPENSED = "dispensed"

class PrescriptionBase(BaseModel):
    patient_id: int
    prescribed_by: int  # Doctor ID
    drug_name: str
    dosage: str
    instructions: str

class PrescriptionCreate(PrescriptionBase):
    pass

class PrescriptionResponse(PrescriptionBase):
    id: int
    status: PrescriptionStatus
    created_at: datetime

    class Config:
        from_attributes = True