from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base
from enum import Enum as PythonEnum

# Define the LabTestStatus enum
class LabTestStatus(PythonEnum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"

class LabTest(Base):
    __tablename__ = "lab_tests"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    requested_by = Column(Integer, ForeignKey("users.id"), nullable=False)  # Requesting doctor
    test_type = Column(String, nullable=False)
    additional_notes = Column(String, nullable=True)
    results = Column(Text, nullable=True)
    status = Column(Enum(LabTestStatus), default=LabTestStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_date = Column(DateTime, nullable=True)  # Track completion time

    # Relationships
    patient = relationship("Patient", back_populates="lab_tests")
    doctor = relationship("User", foreign_keys=[requested_by])
