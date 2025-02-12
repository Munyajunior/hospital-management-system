from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.patients import PatientCreate, PatientResponse
from app.models.patient import Patient
from app.models.user import User
from app.core.database import get_db
from typing import List

router = APIRouter(prefix="/patients", tags=["Patients"])

# Create new patient
@router.post("/", response_model=PatientResponse)
def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    new_patient = Patient(**patient.model_dump())
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return new_patient

# Get all patients
@router.get("/", response_model=List[PatientResponse])
def get_patients(db: Session = Depends(get_db)):
    return db.query(Patient).all()

# Get a single patient by ID
@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

# Update patient details
@router.put("/{patient_id}", response_model=PatientResponse)
def update_patient(patient_id: int, patient_data: PatientCreate, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    for key, value in patient_data.dict().items():
        setattr(patient, key, value)
    
    db.commit()
    db.refresh(patient)
    return patient

# Delete a patient
@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    db.delete(patient)
    db.commit()
    return

# Assign a patient to a doctor
@router.put("/{patient_id}/assign/{doctor_id}", response_model=PatientResponse)
def assign_patient_to_doctor(patient_id: int, doctor_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    doctor = db.query(User).filter(User.id == doctor_id, User.role == "doctor").first()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    patient.assigned_doctor_id = doctor_id
    db.commit()
    db.refresh(patient)

    return patient
