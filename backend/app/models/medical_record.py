from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base

class MedicalRecord(Base):
    __tablename__ = "medical_records"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), unique=True, nullable=False)
    notes = Column(Text, nullable=True)
    diagnoses = Column(Text, nullable=True)
    prescriptions = Column(Text, nullable=True)
    lab_results = Column(Text, nullable=True)
    scans = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())

    # Relationship
    patient = relationship("Patient", back_populates="medical_record")
