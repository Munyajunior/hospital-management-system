from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class BillingStatus(str, Enum):
    PENDING = "Pending"
    PAID = "Paid"
    CANCELLED = "Cancelled"

class BillingCreate(BaseModel):
    patient_id: int
    amount: float

class BillingResponse(BaseModel):
    id: int
    patient_id: int
    amount: float
    status: BillingStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True