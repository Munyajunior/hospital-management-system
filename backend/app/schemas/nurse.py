from pydantic import BaseModel, EmailStr, Field

class NurseBase(BaseModel):
    full_name: str
    email: EmailStr
    phone_number: str = Field(..., pattern="^\+?[0-9\s-]{8,}$")
    department: str

class NurseCreate(NurseBase):
    pass

class NurseResponse(NurseBase):
    id: int

    class Config:
        from_attributes = True