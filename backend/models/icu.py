from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database.base import Base

class ICUAdmission(Base):
    __tablename__ = "icu_admissions"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    condition = Column(String, nullable=False)
    bed_number = Column(String, nullable=False)

    patient = relationship("Patient", back_populates="icu_admissions")
    doctor = relationship("Doctor")
