from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum

class ICUStatus(str, Enum):
    ADMITTED = "Admitted"
    STABLE = "Stable"
    CRITICAL = "Critical"
    DISCHARGED = "Discharged"

class ICUBase(BaseModel):
    patient_id: int
    admitted_by: int  # Nurse ID (matches model's `admitted_by` field)

class ICUCreate(ICUBase):
    pass

class ICUPatientResponse(ICUBase):
    id: int
    status: ICUStatus
    admission_date: datetime
    discharge_date: Optional[datetime] = None
    assigned_nurse_id: Optional[int] = None  # From relationship

    class Config:
        from_attributes = True