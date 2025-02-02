from pydantic import BaseModel

class ICUAdmissionCreate(BaseModel):
    patient_id: int
    doctor_id: int
    condition: str
    bed_number: str

class ICUAdmissionResponse(ICUAdmissionCreate):
    id: int

    class Config:
        from_attributes = True
