from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum

class RadiologyTestStatus(str, Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"

class RadiologyTestBase(BaseModel):
    patient_id: int
    doctor_id: int
    scan_type: str

class RadiologyTestCreate(RadiologyTestBase):
    pass

class RadiologyTestResponse(RadiologyTestBase):
    id: int
    status: RadiologyTestStatus
    report: Optional[str] = None
    requested_date: datetime
    completed_date: Optional[datetime] = None

    class Config:
        from_attributes = True
