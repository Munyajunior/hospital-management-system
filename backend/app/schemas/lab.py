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
    requested_by: int  # Doctor ID
    test_type: str  # Matches model field name

class LabTestCreate(LabTestBase):
    pass

class LabTestResponse(LabTestBase):
    id: int
    status: LabTestStatus
    results: Optional[str] = None  # Matches model field name
    created_at: datetime  # Matches model timestamp field

    class Config:
        from_attributes = True