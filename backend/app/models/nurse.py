from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Nurse(Base):
    __tablename__ = "nurses"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone_number = Column(String, unique=True, nullable=False)
    department = Column(String, nullable=False)

    # Relationships
    icu_patients = relationship("ICUPatient", back_populates="assigned_nurse")