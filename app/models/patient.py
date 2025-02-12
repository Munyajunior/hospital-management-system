from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    date_of_birth = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    contact_number = Column(String, nullable=False)
    address = Column(Text, nullable=False)
    medical_history = Column(Text, nullable=True)
    assigned_doctor_id = Column(Integer, ForeignKey("doctors.id"))
    registered_by = Column(Integer, ForeignKey("users.id"), nullable=False)  # Nurse who registered the patient
    created_at = Column(DateTime, default=datetime.now())
    
    assigned_doctor = relationship("Doctor", back_populates="patients")
    registered_by_user = relationship("User", foreign_keys=[registered_by])

    # Relationship with ICU Admissions
    icu_records = relationship("ICUPatient", back_populates="patient", cascade="all, delete-orphan")

