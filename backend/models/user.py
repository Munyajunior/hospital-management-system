from sqlalchemy import Column, String, Integer, Boolean, Enum
from sqlalchemy.orm import relationship
from backend.database.base import Base
import enum

class UserRole(enum.Enum):
    ADMIN = "admin"
    NURSE = "nurse"
    SECRETARY = "secretary"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)

    # Relationships (for future extensions)
    patients = relationship("Patient", back_populates="assigned_nurse")  # Nurse/Secretary managing patients

    def __repr__(self):
        return f"<User {self.username} ({self.role.value})>"
