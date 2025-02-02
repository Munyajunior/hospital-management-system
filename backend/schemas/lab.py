from pydantic import BaseModel

class LabTestCreate(BaseModel):
    patient_id: int
    doctor_id: int
    test_name: str

class LabTestResponse(LabTestCreate):
    id: int
    result: str | None = None

    class Config:
        from_attributes = True
