from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum

class LabTestStatus(str, Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"

class LabTestBase(BaseModel):
    patient_id: int
    test_type: str

class LabTestCreate(LabTestBase):
    requested_by: int
    additional_notes: str | None = None
    

class LabTestUpdate(BaseModel):
    status: LabTestStatus
    results: Optional[str] = None

class LabTestResponse(LabTestBase):
    id: int
    requested_by: int
    status: LabTestStatus
    results: Optional[str] = None
    created_at: datetime
    completed_date: Optional[datetime] = None

    class Config:
        from_attributes = True
