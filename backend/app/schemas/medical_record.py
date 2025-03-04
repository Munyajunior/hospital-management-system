from pydantic import BaseModel
from datetime import datetime

class MedicalRecordBase(BaseModel):
    notes: str | None = None
    diagnoses: str | None = None
    prescriptions: str | None = None
    lab_results: str | None = None
    scans: str | None = None

class MedicalRecordCreate(MedicalRecordBase):
    pass

class MedicalRecordResponse(MedicalRecordBase):
    id: int
    patient_id: int
    created_at: datetime

    class Config:
        from_attributes = True
