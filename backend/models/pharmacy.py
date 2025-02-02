from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database.base import Base

class Prescription(Base):
    __tablename__ = "prescriptions"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    drug_name = Column(String, nullable=False)
    dosage = Column(String, nullable=False)

    patient = relationship("Patient", back_populates="prescriptions")
    doctor = relationship("Doctor")
