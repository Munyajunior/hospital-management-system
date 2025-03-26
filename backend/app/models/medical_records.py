from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base

class MedicalRecord(Base):
    __tablename__ = "medical_records"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)  # Doctor who created the record
    visit_date = Column(DateTime(timezone=True), server_default = func.now())

    diagnosis = Column(Text, nullable=True)
    treatment_plan = Column(Text, nullable=True)
    medical_history = Column(Text, nullable=True)
    prescription = Column(Text, nullable=True)
    lab_tests_requested = Column(Text, nullable=True)
    scans_requested = Column(Text, nullable=True)
    lab_tests_results = Column(Text, nullable=True)
    scan_results = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default = func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    patient = relationship("Patient", back_populates="medical_records")
    doctor = relationship("User", foreign_keys=[created_by])
