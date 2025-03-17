from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, Date, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base

 
class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(Enum("Male", "Female", "Other", name="gender_enum"), nullable=False)
    contact_number = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)  # Authentication for mobile app
    address = Column(Text, nullable=False)

    # Patient categorization
    category = Column(Enum("outpatient", "inpatient", "ICU", name="patient_category"), default="outpatient", nullable=False)
    emergency = Column(Boolean, default=False)  # Emergency flag

    assigned_doctor_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    registered_by = Column(Integer, ForeignKey("users.id"), nullable=False)  # Nurse who registered the patient
    created_at = Column(Date, server_default=func.now())

    # Relationships
    icu_records = relationship("ICUPatient", back_populates="patient", cascade="all, delete-orphan")
    inpatient_records = relationship("Inpatient", back_populates="patient", cascade="all, delete-orphan")
    assigned_doctor = relationship("User", back_populates="patients", foreign_keys=[assigned_doctor_id])
    registered_by_user = relationship("User", foreign_keys=[registered_by])
    medical_records = relationship("MedicalRecord", back_populates="patient", cascade="all, delete-orphan")
    admissions = relationship("PatientAdmission", back_populates="patient")


    bills = relationship("Billing", back_populates="patient", cascade="all, delete-orphan")
    lab_tests = relationship("LabTest", back_populates="patient", cascade="all, delete-orphan")
    prescriptions = relationship("Prescription", back_populates="patient", cascade="all, delete-orphan")
    radiology_scan = relationship("RadiologyScan", back_populates="patient", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="patient", cascade="all, delete-orphan")
