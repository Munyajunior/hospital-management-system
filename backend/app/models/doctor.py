from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base

class Doctor(Base):
    __tablename__ = "doctors"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    specialization = Column(String, nullable=False)
    contact_number = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False) # Foreign Key to User

    # Relationships
    patients = relationship("Patient", back_populates="assigned_doctor")
    user = relationship("User", back_populates="doctor")