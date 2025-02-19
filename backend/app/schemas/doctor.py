from pydantic import BaseModel, EmailStr, Field

class DoctorBase(BaseModel):
    full_name: str
    specialization: str
    contact_number: str = Field(..., pattern="^\+?[0-9\s-]{8,}$")
    email: EmailStr

class DoctorCreate(DoctorBase):
    user_id: int  # Admin must link to existing User

class DoctorResponse(DoctorBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True