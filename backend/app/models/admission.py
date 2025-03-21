from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime, Boolean, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base
from enum import Enum as PyEnum

class AdmissionCategory(str, PyEnum):
    OUTPATIENT = "Outpatient"
    INPATIENT = "Inpatient"
    ICU = "ICU"

class AdmissionStatus(str, PyEnum):
    ADMITTED = "Admitted"
    STABLE = "Stable"
    CRITICAL = "Critical"
    DISCHARGED = "Discharged"

class PatientAdmission(Base):
    __tablename__ = "patient_admissions" 

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    admitted_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    assigned_doctor_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)  # Added this field
    category = Column(Enum(AdmissionCategory, name="admission_category"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="SET NULL"))
    ward_id = Column(Integer, ForeignKey("wards.id", ondelete="SET NULL"))
    bed_id = Column(Integer, ForeignKey("beds.id", ondelete="SET NULL"))
    admission_date = Column(DateTime, default=func.now())
    discharge_date = Column(DateTime, onupdate=func.now(), nullable=True)
    status = Column(Enum(AdmissionStatus, name="admission_status"), default=AdmissionStatus.ADMITTED)

    # Relationships
    patient = relationship("Patient", back_populates="admissions")
    admitted_by_user = relationship("User", foreign_keys=[admitted_by])  # Renamed for clarity
    assigned_doctor = relationship("User", foreign_keys=[assigned_doctor_id])  # Corrected relationship
    department = relationship("Department")
    ward = relationship("Ward")
    bed = relationship("Bed", back_populates="patient_admission", uselist=False)  
    icu_patient = relationship("ICUPatient", back_populates="admission", uselist=False, cascade="all, delete-orphan")
    inpatient = relationship("Inpatient", back_populates="admission", uselist=False, cascade="all, delete-orphan")
    


class ICUPatient(Base):
    __tablename__ = "icu_patients"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    admission_id = Column(Integer, ForeignKey("patient_admissions.id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum("Stable", "Critical", "Improving", "Deteriorating", name="icu_status"), default="Stable")
    condition_evolution = Column(Text, nullable=True)  # Daily updates on patient condition
    medications = Column(Text, nullable=True)  # List of medications
    drips = Column(Text, nullable=True)  # Number and type of drips
    treatment_plan = Column(Text, nullable=True)  # Detailed treatment plan
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=False)  # Doctor or nurse who updated the record
    updated_at = Column(DateTime, default=func.now())

    # Relationships
    patient = relationship("Patient", back_populates="icu_records")
    admission = relationship("PatientAdmission", back_populates="icu_patient")
    updated_by_user = relationship("User", foreign_keys=[updated_by])

class Inpatient(Base):
    __tablename__ = "inpatients"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    admission_id = Column(Integer, ForeignKey("patient_admissions.id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum("Stable", "Recovering", "Discharged", name="inpatient_status"), default="Stable")
    condition_evolution = Column(Text, nullable=True)  # Daily updates on patient condition
    medications = Column(Text, nullable=True)  # List of medications
    treatment_plan = Column(Text, nullable=True)  # Detailed treatment plan
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=False)  # Doctor or nurse who updated the record
    updated_at = Column(DateTime, default=func.now())

    # Relationships
    patient = relationship("Patient", back_populates="inpatient_records")
    admission = relationship("PatientAdmission", back_populates="inpatient")
    updated_by_user = relationship("User", foreign_keys=[updated_by])

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


class PatientVitals(Base):
    __tablename__ = "patient_vitals"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    blood_pressure = Column(Float, nullable=True)
    heart_rate = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)
    recorded_by = Column(Integer, ForeignKey("users.id"), nullable=False)  # Nurse or doctor who recorded the vitals
    recorded_at = Column(DateTime, default=func.now())