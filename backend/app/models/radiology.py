from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from enum import Enum as PyEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class RadiologyTestStatus(str, PyEnum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"

class RadiologyTest(Base):
    __tablename__ = "radiology_scans"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    requested_by = Column(Integer, ForeignKey("users.id"), nullable=False)  # Doctor who requested
    scan_type = Column(String, nullable=False)
    scan_results = Column(Text, nullable=True)
    status = Column(Enum(RadiologyTestStatus), default=RadiologyTestStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    patient = relationship("Patient", back_populates="radiology_tests")
    doctor = relationship("User", foreign_keys=[requested_by])