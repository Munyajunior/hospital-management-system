from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Enum  # Import SQLAlchemy's Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base
from enum import Enum as PythonEnum

# Define the LabTestStatus enum
class LabTestStatus(PythonEnum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"

# Extract the enum values for SQLAlchemy
lab_test_status_values = [status.value for status in LabTestStatus]

class LabTest(Base):
    __tablename__ = "lab_tests"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    requested_by = Column(Integer, ForeignKey("users.id"), nullable=False)  # Doctor who requested
    test_type = Column(String, nullable=False)
    results = Column(Text, nullable=True)
    status = Column(Enum(LabTestStatus,name="lab_test_status",), default=LabTestStatus.PENDING)  # Use SQLAlchemy's Enum
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    patient = relationship("Patient", back_populates="lab_tests")
    doctor = relationship("User", foreign_keys=[requested_by])