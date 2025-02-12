from pydantic import BaseModel, EmailStr
from typing import Optional

class NurseBase(BaseModel):
    full_name: str
    email: EmailStr
    phone_number: str
    department: str

class NurseCreate(NurseBase):
    pass

class NurseResponse(NurseBase):
    id: int

    class Config:
        from_attributes = True
