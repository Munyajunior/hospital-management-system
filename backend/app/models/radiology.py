from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Enum
from enum import Enum as PythonEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base

class RadiologyScanStatus(PythonEnum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"

class RadiologyScan(Base):
    __tablename__ = "radiology_scans"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    requested_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    scan_type = Column(String, nullable=False)
    additional_notes = Column(String, nullable=True)
    results = Column(Text, nullable=True)
    status = Column(Enum(RadiologyScanStatus, name="radiology_scan_status"), default=RadiologyScanStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_date = Column(DateTime(timezone=True), onupdate=func.now())  # Track completion time

    # Relationships
    patient = relationship("Patient", back_populates="radiology_scan")
    doctor = relationship("User", foreign_keys=[requested_by])
