from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, Enum, Boolean, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base
import base64

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    date_of_birth = Column(DateTime(timezone=True), nullable=False)
    gender = Column(Enum("Male", "Female", "Other", name="gender_enum"), nullable=False)
    role = Column(String, default="patient", nullable=False)
    contact_number = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    address = Column(Text, nullable=False)
    profile_picture = Column(LargeBinary, nullable=True)  # Store binary image data
    profile_picture_type = Column(String, nullable=True)  # Store image MIME type
    # Patient categorization
    category = Column(Enum("outpatient", "inpatient", "ICU", name="patient_category"), default="outpatient", nullable=False)
    emergency = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True) 

    assigned_doctor_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    registered_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

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

    def set_profile_picture(self, image_data: bytes, content_type: str):
        """Store profile picture in the database."""
        self.profile_picture = image_data
        self.profile_picture_type = content_type

    def get_profile_picture_base64(self):
        """Get profile picture as base64 encoded string."""
        if self.profile_picture and self.profile_picture_type:
            return f"data:{self.profile_picture_type};base64,{base64.b64encode(self.profile_picture).decode('utf-8')}"
        return None
