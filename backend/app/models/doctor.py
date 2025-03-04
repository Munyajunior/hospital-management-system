from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base

class Doctor(Base):
    __tablename__ = "doctors"
    
    id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, primary_key=True) # Foreign Key to User. Linking User created to doctor 
    full_name = Column(String, nullable=False)
    specialization = Column(String, nullable=False)
    contact_number = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
