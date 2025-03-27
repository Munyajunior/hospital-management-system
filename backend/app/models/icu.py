from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum, String
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from sqlalchemy.orm import relationship
from core.database import Base

class ICUStatus(str, PyEnum):
    ADMITTED = "Admitted"
    STABLE = "Stable"
    CRITICAL = "Critical"
    DISCHARGED = "Discharged"

class ICUPatient(Base):
    __tablename__ = "icu_admissions"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    admitted_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))  # Nurse who admitted
    department = Column(String, nullable = False)
    ward = Column(String, nullable=False)
    bed_number = Column(Integer, nullable=False)
    admission_date = Column(DateTime(timezone=True), server_default=func.now())
    discharge_date = Column(DateTime(timezone=True), onupdate=func.now())
    status = Column(Enum(ICUStatus,name="icu_status",), default=ICUStatus.ADMITTED)

    # Relationships
    #assigned_nurse = relationship("Nurse", back_populates="icu_patients")
    #patient = relationship("Patient", back_populates="icu_records")