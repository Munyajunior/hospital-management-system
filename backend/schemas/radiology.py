from pydantic import BaseModel

class RadiologyScanCreate(BaseModel):
    patient_id: int
    doctor_id: int
    scan_type: str

class RadiologyScanResponse(RadiologyScanCreate):
    id: int
    result: str | None = None

    class Config:
        from_attributes = True
