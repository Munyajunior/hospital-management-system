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
    requested_by: int  # Doctor ID
    scan_type: str

class RadiologyTestCreate(RadiologyTestBase):
    pass

class RadiologyTestResponse(RadiologyTestBase):
    id: int
    status: RadiologyTestStatus
    scan_results: Optional[str] = None  # Matches model field name
    created_at: datetime  # Matches model timestamp field

    class Config:
        from_attributes = True