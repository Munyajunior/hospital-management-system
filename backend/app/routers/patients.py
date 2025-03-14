from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from schemas.patients import PatientCreate, PatientResponse, PatientUpdate
from models.patient import Patient
from models.user import User
from models.doctor import Doctor
from core.database import get_db
from utils.security import hash_password, generate_password
from core.dependencies import RoleChecker


router = APIRouter(prefix="/patients", tags=["Patients"])



# Allow nurses and receptionists
staff_only = RoleChecker(["admin", "nurse", "receptionist"])
doctor_only = RoleChecker(["doctor","nurse"])


@router.post("/", response_model=PatientResponse)
def create_patient(patient: PatientCreate, db: Session = Depends(get_db), 
                   current_user: User = Depends(staff_only)):

    existing_user = db.query(Patient).filter(Patient.email == patient.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    password_hash = hash_password(generate_password())
    patient_data = patient.model_dump()
    patient_data["hashed_password"] =  password_hash
    patient_data["registered_by"] = current_user.id
    patient_data["category"] = "outpatient" if not patient.emergency else "inpatient"
  

    new_patient = Patient(**patient_data)
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    
    return new_patient

@router.get("/", response_model=List[PatientResponse])
def get_patients(db: Session = Depends(get_db), user: User = Depends(staff_only)):
    return db.query(Patient).all()


@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: int, db: Session = Depends(get_db), user: User = Depends(doctor_only)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.put("/{patient_id}", response_model=PatientResponse)
def update_patient(patient_id: int, patient_data: PatientUpdate, db: Session = Depends(get_db),
                   user: User = Depends(doctor_only)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    for key, value in patient_data.model_dump(exclude_unset=True).items():
        setattr(patient, key, value)

    db.commit()
    db.refresh(patient)
    return patient


@router.put("/{patient_id}/assign-category/{category}", response_model=PatientResponse)
def update_patient_category(patient_id: int, category: str, db: Session = Depends(get_db),
                            user: User = Depends(doctor_only)):
    if category not in ["outpatient", "inpatient", "ICU"]:
        raise HTTPException(status_code=400, detail="Invalid category")

    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    patient.category = category
    db.commit()
    db.refresh(patient)
    return patient 

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


@router.put("/{patient_id}/update-medical-records", response_model=PatientResponse)
def update_medical_records(patient_id: int, updates: PatientUpdate, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    for key, value in updates.model_dump(exclude_unset=True).items():
        setattr(patient, key, value)
    
    db.commit()
    db.refresh(patient)
    return patient






