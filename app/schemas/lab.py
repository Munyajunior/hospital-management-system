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
    doctor_id: int
    test_name: str

class LabTestCreate(LabTestBase):
    pass

class LabTestResponse(LabTestBase):
    id: int
    status: LabTestStatus
    result: Optional[str] = None
    requested_date: datetime
    completed_date: Optional[datetime] = None

    class Config:
        from_attributes = True
