from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum

class RadiologyScanStatus(str, Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"

class RadiologyScanBase(BaseModel):
    patient_id: int
    scan_type: str

class RadiologyScanCreate(RadiologyScanBase):
    requested_by: int  # Doctor ID
    additional_notes: str | None = None

class RadiologyScanUpdate(BaseModel):
    status: RadiologyScanStatus
    report : Optional[str] = None
    
    
class RadiologyScanResponse(RadiologyScanBase):
    id: int
    requested_by: int
    status: RadiologyScanStatus
    results: Optional[str] = None  # Matches model field name
    created_at: datetime  # Matches model timestamp field
    completed_date: Optional[datetime] = None
    

    class Config:
        from_attributes = True