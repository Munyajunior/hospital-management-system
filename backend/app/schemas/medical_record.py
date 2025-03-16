from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MedicalRecordBase(BaseModel):
    diagnosis: Optional[str] = None
    treatment_plan: Optional[str] = None
    prescription: Optional[str] = None
    lab_tests_requested: Optional[str] = None
    scans_requested: Optional[str] = None
    lab_tests_results: Optional[str] = None
    scan_results: Optional[str] = None
    notes: Optional[str] = None
    medical_history: Optional[str] = None

class MedicalRecordCreate(MedicalRecordBase):
    pass

class MedicalRecordUpdate(MedicalRecordCreate):
    pass

class MedicalRecordResponse(MedicalRecordBase):
    id: int
    patient_id: int
    created_by: int
    visit_date: datetime

    class Config:
        from_attributes = True
