from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from models.admission import AdmissionCategory, AdmissionStatus


class AdmissionBase(BaseModel):
    patient_id: int
    category: AdmissionCategory
    department_id: Optional[int] = None
    ward_id: Optional[int] = None
    bed_id: Optional[int] = None
    assigned_doctor_id: Optional[int] = None 
    status: Optional[AdmissionStatus] = AdmissionStatus.ADMITTED


class AdmissionCreate(AdmissionBase):
    pass


class AdmissionResponse(AdmissionBase):
    id: int
    admitted_by: int
    admission_date: datetime
    discharge_date: Optional[datetime] = None

    class Config:
        from_attributes = True

class AdmissionTableResponse(BaseModel):
    """Response model for populating the admitted patients table."""
    id: int
    patient_id: int
    patient_name: str  # Name of the patient
    admitted_by: int
    admitted_by_name: str  # Name of the user who admitted the patient
    assigned_doctor_id: Optional[int] = None
    assigned_doctor_name: Optional[str] = None  # Name of the assigned doctor
    category: AdmissionCategory
    department_id: Optional[int] = None
    department_name: Optional[str] = None  # Name of the department
    ward_id: Optional[int] = None
    ward_name: Optional[str] = None  # Name of the ward
    bed_id: Optional[int] = None
    bed_number: Optional[str] = None  # Bed number
    status: Optional[AdmissionStatus] = AdmissionStatus.ADMITTED
    admission_date: datetime
    discharge_date: Optional[datetime] = None

    class Config:
        from_attributes = True

class ICUPatientBase(BaseModel):
    patient_id: int
    admission_id: int
    status: Optional[str] = "Stable"
    condition_evolution: Optional[str] = None
    medications: Optional[str] = None
    drips: Optional[str] = None
    treatment_plan: Optional[str] = None

class ICUPatientCreate(ICUPatientBase):
    pass

class ICUPatientResponse(ICUPatientBase):
    id: int
    updated_by: int
    updated_at: datetime

    class Config:
        from_attributes = True

class InpatientBase(BaseModel):
    patient_id: int
    status: Optional[str] = "Stable"
    condition_evolution: Optional[str] = None
    medications: Optional[str] = None
    treatment_plan: Optional[str] = None

class InpatientCreate(InpatientBase):
    pass

class InpatientResponse(InpatientBase):
    id: int
    updated_by: int
    updated_at: datetime

    class Config:
        from_attributes = True


class DepartmentBase(BaseModel):
    name: str
    category: AdmissionCategory


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentResponse(DepartmentBase):
    id: int

    class Config:
        from_attributes = True



class WardBase(BaseModel):
    name: str
    department_id: int


class WardCreate(WardBase):
    pass


class WardResponse(WardBase):
    id: int

    class Config:
        from_attributes = True


class BedBase(BaseModel):
    bed_number: str
    ward_id: int


class BedCreate(BedBase):
    pass


class BedResponse(BedBase):
    id: int
    is_occupied: bool

    class Config:
        from_attributes = True


class PatientVitalsBase(BaseModel):
    patient_id: int
    blood_pressure: float
    heart_rate: float
    temperature: float

class PatientVitalsCreate(PatientVitalsBase):
    pass

class PatientVitalsResponse(PatientVitalsBase):
    id: int
    recorded_by: int
    recorded_at: datetime
    

    class Config:
        from_attributes = True

class PatientVitalsResponseTable(BaseModel):
    patient_name: str
    recorded_by_name: str
    blood_pressure: float
    heart_rate: float
    temperature: float
    recorded_at: datetime

    class Config:
        from_attributes = True