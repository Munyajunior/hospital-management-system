from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum
from enum import Enum as PyEnum
from sqlalchemy.orm import relationship
from datetime import datetime
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
    admitted_by = Column(Integer, ForeignKey("nurses.id", ondelete="SET NULL"))  # Nurse who admitted
    admission_date = Column(DateTime, default=datetime.utcnow)
    discharge_date = Column(DateTime, nullable=True)
    status = Column(Enum(ICUStatus,name="icu_status",), default=ICUStatus.ADMITTED)

    # Relationships
    assigned_nurse = relationship("Nurse", back_populates="icu_patients")
    patient = relationship("Patient", back_populates="icu_records")