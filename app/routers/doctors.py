from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.patients import PatientResponse 
from app.schemas.doctor import DoctorCreate, DoctorResponse
from app.models.doctor import Doctor
from app.models.user import User
from app.core.database import get_db
from typing import List

router = APIRouter(prefix="/doctors", tags=["Doctors"])

# Create a new doctor
@router.post("/", response_model=DoctorResponse)
def create_doctor(doctor: DoctorCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == doctor.user_id, User.role == "doctor").first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid user ID or user is not a doctor")

    new_doctor = Doctor(**doctor.model_dump())
    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)
    return new_doctor

# Get all doctors
@router.get("/", response_model=List[DoctorResponse])
def get_doctors(db: Session = Depends(get_db)):
    return db.query(Doctor).all()

# Get a single doctor by ID
@router.get("/{doctor_id}", response_model=DoctorResponse)
def get_doctor(doctor_id: int, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor

# Update doctor details
@router.put("/{doctor_id}", response_model=DoctorResponse)
def update_doctor(doctor_id: int, doctor_data: DoctorCreate, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    for key, value in doctor_data.dict().items():
        setattr(doctor, key, value)
    
    db.commit()
    db.refresh(doctor)
    return doctor

# Delete a doctor
@router.delete("/{doctor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_doctor(doctor_id: int, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    db.delete(doctor)
    db.commit()
    return

# Get all patients assigned to a doctor
@router.get("/{doctor_id}/patients", response_model=List[PatientResponse])
def get_doctor_patients(doctor_id: int, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    return doctor.patients
