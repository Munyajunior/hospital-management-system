from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum

class AppointmentStatus(str, Enum):
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    COMPLETED = "Completed"
    CANCELED = "Canceled"
    RESCHEDULED = "Rescheduled Pending"

class AppointmentBase(BaseModel):
    doctor_id: int
    patient_id: int
    patient_name : str
    datetime: datetime
    reason: str

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(BaseModel):
    status: AppointmentStatus

class AppointmentReschedule(BaseModel):
    datetime: datetime
    status: AppointmentStatus

class AppointmentResponse(AppointmentBase):
    id: int
    status: AppointmentStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class DoctorAppointmentResponse(AppointmentBase):
    id: int  
    status: AppointmentStatus
    created_at: datetime
    updated_at: datetime
    pass

    
