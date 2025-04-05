from sqlalchemy import Column, Integer, String, DateTime, Boolean, LargeBinary, Text
import json
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base
import base64



class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    contact_number = Column(String, nullable=True)
    address = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # admin, nurse, doctor, pharmacist, lab, radiology, icu
    is_active = Column(Boolean, default=True)
    profile_picture = Column(LargeBinary, nullable=True)  # Store binary image data
    profile_picture_type = Column(String, nullable=True)  # Store image MIME type
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    settings = Column(Text, nullable=True)  # Store JSON settings
    security_questions = Column(Text, nullable=True)  # Store JSON security questions
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), default=func.now())

   
    # Relationships
    appointments = relationship("Appointment", back_populates="doctor", foreign_keys="[Appointment.doctor_id]")  
    patients = relationship("Patient", back_populates="assigned_doctor", foreign_keys="[Patient.assigned_doctor_id]")

    def set_profile_picture(self, image_data: bytes, content_type: str):
        """Store profile picture in the database."""
        self.profile_picture = image_data
        self.profile_picture_type = content_type

    def get_profile_picture_base64(self):
        """Get profile picture as base64 encoded string."""
        if self.profile_picture and self.profile_picture_type:
            return f"data:{self.profile_picture_type};base64,{base64.b64encode(self.profile_picture).decode('utf-8')}"
        return None

    def get_settings(self):
        """Get parsed settings dictionary"""
        if not self.settings:
            return {}
        try:
            return json.loads(self.settings)
        except:
            return {}

    def get_security_questions(self):
        """Get parsed security questions"""
        if not self.security_questions:
            return []
        try:
            return json.loads(self.security_questions)
        except:
            return []