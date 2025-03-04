from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # admin, nurse, doctor, pharmacy, lab, radiology, icu
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    appointments = relationship("Appointment", back_populates="doctor", foreign_keys="[Appointment.doctor_id]")  
    patients = relationship("Patient", back_populates="assigned_doctor", foreign_keys="[Patient.assigned_doctor_id]")