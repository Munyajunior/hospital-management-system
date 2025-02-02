from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from database.base import Base

class Patient(Base):
    """
    Represents a patient in the system.
    """
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String, nullable=False)
    phone = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=True)
    address = Column(String, nullable=False)
    assigned_doctor_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    doctor = relationship("User", back_populates="patients")
