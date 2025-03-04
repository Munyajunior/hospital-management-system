from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, Enum, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from core.database import Base

class AppointmentStatus(str, PyEnum):
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    COMPLETED = "Completed"
    CANCELED = "Canceled"
    RESCHEDULED = "Rescheduled Pending"

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    patient_name = Column(String, nullable=False)
    datetime = Column(DateTime, nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(Enum(AppointmentStatus, name="appointment_status"), default=AppointmentStatus.PENDING, nullable=False)

    created_at = Column(DateTime, server_default=func.now())

    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    doctor = relationship("User", back_populates="appointments", foreign_keys=[doctor_id])
    patient = relationship("Patient", back_populates="appointments", foreign_keys=[patient_id])



