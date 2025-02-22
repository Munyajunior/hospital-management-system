from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from schemas.patients import PatientCreate, PatientResponse
from models.patient import Patient
from models.user import User
from core.database import get_db
from core.dependencies import RoleChecker

router = APIRouter(prefix="/patients", tags=["Patients"])



# Allow nurses and receptionists
staff_only = RoleChecker(["admin","nurse", "receptionist", "doctor"])

@router.post("/", response_model=PatientResponse)
def create_patient(patient: PatientCreate, db: Session = Depends(get_db), 
                   user: User = Depends(staff_only)):
    # Validate doctor if provided
    if patient.assigned_doctor_id:
        doctor = db.query(User).filter(User.id == patient.assigned_doctor_id, User.role == "doctor").first()
        if not doctor:
            raise HTTPException(status_code=400, detail="Invalid doctor ID")

    new_patient = Patient(**patient.model_dump())
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return new_patient


@router.get("/", response_model=List[PatientResponse])
def get_patients(db: Session = Depends(get_db),
                 user: User = Depends(staff_only)):
    return db.query(Patient).all()

@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: int, db: Session = Depends(get_db),
                user: User = Depends(staff_only)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@router.put("/{patient_id}", response_model=PatientResponse)
def update_patient(patient_id: int, patient_data: PatientCreate, db: Session = Depends(get_db),
                   user: User = Depends(staff_only)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    for key, value in patient_data.model_dump().items():
        setattr(patient, key, value)
    
    db.commit()
    db.refresh(patient)
    return patient

@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(patient_id: int, db: Session = Depends(get_db),
                   user: User = Depends(staff_only)): #TODO: implement who can delete patient
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    db.delete(patient)
    db.commit()
    return

@router.put("/{patient_id}/assign/{doctor_id}", response_model=PatientResponse)
def assign_patient_to_doctor(patient_id: int, doctor_id: int, db: Session = Depends(get_db),
                             user: User = Depends(staff_only)):
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