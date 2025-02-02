from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database.base import Base

class LabTest(Base):
    __tablename__ = "lab_tests"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    test_name = Column(String, nullable=False)
    result = Column(String, nullable=True)

    patient = relationship("Patient", back_populates="lab_tests")
    doctor = relationship("Doctor")
