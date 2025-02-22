from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Enum
from enum import Enum as PyEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base

class RadiologyTestStatus(str, PyEnum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"

class RadiologyTest(Base):
    __tablename__ = "radiology_scans"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    requested_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    scan_type = Column(String, nullable=False)
    scan_results = Column(Text, nullable=True)
    status = Column(
    Enum(
        RadiologyTestStatus,
        name="radiology_test_status",
        native_enum=True,  
        create_type=True   
    ),
    default=RadiologyTestStatus.PENDING,
    nullable=False
)


    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="radiology_test")
    doctor = relationship("User", foreign_keys=[requested_by])
