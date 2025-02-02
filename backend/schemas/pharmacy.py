from pydantic import BaseModel

class PrescriptionCreate(BaseModel):
    patient_id: int
    doctor_id: int
    drug_name: str
    dosage: str

class PrescriptionResponse(PrescriptionCreate):
    id: int

    class Config:
        from_attributes = True
