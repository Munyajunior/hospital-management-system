from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from schemas.doctor import DoctorCreate, DoctorResponse
from models.doctor import Doctor
from schemas.patients import PatientResponse
from models.patient import Patient
from models.user import User
from core.database import get_db
from core.dependencies import RoleChecker, get_current_active_user
from core.security import hash_password

router = APIRouter(prefix="/doctors", tags=["Doctors"])

# Allow only admins to create doctors
admin_only = RoleChecker(["admin"])

# Allow staff to view doctors
staff_only = RoleChecker(["doctor","admin","nurse", "receptionists"])

@router.post("/", response_model=DoctorResponse)
def create_doctor(doctor: DoctorCreate, db: Session = Depends(get_db), user: User = Depends(admin_only)):
    """
    Create a new doctor. Automatically creates a corresponding User account.
    """
    # Check if doctor email already exists
    existing_doctor = db.query(Doctor).filter(Doctor.email == doctor.email).first()
    if existing_doctor:
        raise HTTPException(status_code=400, detail="A doctor with this email already exists")

    # Check if user with the same email exists
    existing_user = db.query(User).filter(User.email == doctor.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="A user with this email already exists")
    

    # Create User
    new_user = User(
        full_name=doctor.full_name,
        email=doctor.email,
        hashed_password=hash_password(doctor.password),
        role="doctor"
    )
    
    db.add(new_user)
    db.flush()  # Ensures user.id is available before creating Doctor

    # Create Doctor linked to the User
    new_doctor = Doctor(
        id=new_user.id, # Link doctor to the created user 
        full_name=doctor.full_name,
        specialization=doctor.specialization,
        contact_number=doctor.contact_number,
        email=doctor.email,
        hashed_password=hash_password(doctor.password)
    )
    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)
    
    return new_doctor


@router.get("/", response_model=List[DoctorResponse])
def get_doctors(db: Session = Depends(get_db), user: User = Depends(staff_only)):
    return db.query(Doctor).all()

@router.get("/{doctor_id}", response_model=DoctorResponse)
def get_doctor(doctor_id: int, db: Session = Depends(get_db), user: User = Depends(staff_only)):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor

@router.put("/{doctor_id}", response_model=DoctorResponse)
def update_doctor(doctor_id: int, doctor_data: DoctorCreate, db: Session = Depends(get_db), user: User = Depends(admin_only)):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    for key, value in doctor_data.model_dump().items():
        setattr(doctor, key, value)
    
    db.commit()
    db.refresh(doctor)
    return doctor


@router.get("/{doctor_id}/patients", response_model=List[PatientResponse])
def get_assigned_patients(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),  # Must be logged in
    _: User = Depends(RoleChecker(["doctor"]))               # Must have doctor role
):
    """
    Retrieve all patients assigned to the current doctor.
    """
    patients = db.query(Patient).filter(Patient.assigned_doctor_id == current_user.id).all()
    if not patients:
        raise HTTPException(status_code=404, detail="No patients assigned")
    return patients



@router.delete("/{doctor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_doctor(doctor_id: int, db: Session = Depends(get_db), user: User = Depends(admin_only)):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    db.delete(doctor)
    db.commit()
    return