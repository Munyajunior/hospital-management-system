from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from models.lab import LabTestStatus

class LabTestBase(BaseModel):
    patient_id: int
    test_type: str

class LabTestCreate(LabTestBase):
    requested_by: int
    additional_notes: Optional[str] = None
    

class LabTestUpdate(BaseModel):
    status: LabTestStatus
    results: Optional[str] = None
    additional_notes: Optional[str] = None

class LabTestResponse(LabTestBase):
    id: int
    requested_by: int
    status: LabTestStatus
    results: Optional[str] = None
    created_at: datetime
    completed_date: Optional[datetime] = None

    class Config:
        from_attributes = True
