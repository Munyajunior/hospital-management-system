from pydantic import BaseModel, EmailStr

class DoctorCreate(BaseModel):
    name: str
    specialty: str
    phone: str
    email: EmailStr

class DoctorResponse(DoctorCreate):
    id: int

    class Config:
        from_attributes = True
