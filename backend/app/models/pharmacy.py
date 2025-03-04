from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Enum
from enum import Enum as PyEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base

class PrescriptionStatus(str, PyEnum):
    PENDING = "pending"
    DISPENSED = "dispensed"

class Prescription(Base):
    __tablename__ = "prescriptions"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    prescribed_by = Column(Integer, ForeignKey("users.id"), nullable=False)  # Doctor who prescribed
    drug_name = Column(String, nullable=False)
    dosage = Column(String, nullable=False)
    instructions = Column(Text, nullable=False)
    status = Column(Enum(PrescriptionStatus, name="prescription_status"), default=PrescriptionStatus.PENDING, nullable=False)  
    created_at = Column(DateTime, server_default=func.now())
    dispensed_at = Column(DateTime, onupdate=func.now(),server_default=func.now())
    
    # Relationships
    patient = relationship("Patient", back_populates="prescriptions")
    doctor = relationship("User", foreign_keys=[prescribed_by])