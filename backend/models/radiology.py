from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database.base import Base

class RadiologyScan(Base):
    __tablename__ = "radiology_scans"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    scan_type = Column(String, nullable=False)
    result = Column(String, nullable=True)

    patient = relationship("Patient", back_populates="radiology_scans")
    doctor = relationship("Doctor")
