from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base
import enum

class AdmissionCategory(str, enum.Enum):
    OUTPATIENT = "Outpatient"
    INPATIENT = "Inpatient"
    ICU = "ICU"

class AdmissionStatus(str, enum.Enum):
    ADMITTED = "Admitted"
    STABLE = "Stable"
    CRITICAL = "Critical"
    DISCHARGED = "Discharged"

class PatientAdmission(Base):
    __tablename__ = "patient_admissions"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    admitted_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    category = Column(Enum(AdmissionCategory, name="admission_category"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="SET NULL"))
    ward_id = Column(Integer, ForeignKey("wards.id", ondelete="SET NULL"))
    bed_id = Column(Integer, ForeignKey("beds.id", ondelete="SET NULL"))
    admission_date = Column(DateTime, default=func.now())
    discharge_date = Column(DateTime, onupdate=func.now(), nullable=True)
    status = Column(Enum(AdmissionStatus, name="admission_status"), default=AdmissionStatus.ADMITTED)

    # Relationships
    patient = relationship("Patient", back_populates="admissions")
    assigned_doctor = relationship("User", back_populates="admissions")
    department = relationship("Department")
    ward = relationship("Ward")
    bed = relationship("Bed", back_populates="patient_admission", uselist=False)  # Each bed has one active admission

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    category = Column(Enum(AdmissionCategory, name="department_category"), nullable=False)

    wards = relationship("Ward", back_populates="department")

class Ward(Base):
    __tablename__ = "wards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="CASCADE"), nullable=False)

    department = relationship("Department", back_populates="wards")
    beds = relationship("Bed", back_populates="ward")

class Bed(Base):
    __tablename__ = "beds"

    id = Column(Integer, primary_key=True, index=True)
    bed_number = Column(String, nullable=False)
    ward_id = Column(Integer, ForeignKey("wards.id", ondelete="CASCADE"), nullable=False)
    is_occupied = Column(Boolean, default=False)

    ward = relationship("Ward", back_populates="beds")
    patient_admission = relationship("PatientAdmission", back_populates="bed", uselist=False)
