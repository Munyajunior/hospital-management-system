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
    assigned_nurse_id: int
    bed_number: str

class ICUCreate(ICUBase):
    pass

class ICUPatientResponse(ICUBase):
    id: int
    status: ICUStatus
    admission_date: datetime
    discharge_date: Optional[datetime] = None

    class Config:
        from_attributes = True
