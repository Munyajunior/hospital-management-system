from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base

class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    date_of_birth = Column(Date, nullable=False)  # Changed to Date
    gender = Column(String, nullable=False)
    contact_number = Column(String, nullable=False)
    address = Column(Text, nullable=False)
    medical_history = Column(Text, nullable=True)
    diagnosis = Column(Text, nullable=True)
    treatment_plan = Column(Text, nullable=True)
    prescription = Column(Text, nullable=True)
    lab_tests_requested = Column(Text, nullable=True)
    scans_requested = Column(Text, nullable=True)
    lab_tests_results= Column(Text, nullable=True)
    scan_results = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    assigned_doctor_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    registered_by = Column(Integer, ForeignKey("users.id"), nullable=False)  # Nurse who registered the patient
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    assigned_doctor = relationship("User", back_populates="patients", foreign_keys=[assigned_doctor_id])
    registered_by_user = relationship("User", foreign_keys=[registered_by])
    icu_records = relationship("ICUPatient", back_populates="patient", cascade="all, delete-orphan")
    lab_tests = relationship("LabTest", back_populates="patient", cascade="all, delete-orphan")
    prescriptions = relationship("Prescription", back_populates="patient", cascade="all, delete-orphan")
    radiology_scan = relationship("RadiologyScan", back_populates="patient", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="patient", cascade="all, delete-orphan")
   