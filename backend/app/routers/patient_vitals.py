from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.admission import PatientVitals
from models.patient import Patient
from models.user import User
from typing import List
from schemas.admission import PatientVitalsCreate, PatientVitalsResponse
from core.database import get_db
from core.dependencies import RoleChecker

router = APIRouter(prefix="/vitals", tags=["Patient Vitals"])

nurse_or_doctor = RoleChecker(["nurse", "doctor", "admin"])

@router.post("/", response_model=PatientVitalsResponse)
def update_vitals(vitals: PatientVitalsCreate, db: Session = Depends(get_db), user: User = Depends(nurse_or_doctor)):
    # Check if the patient exists
    patient = db.query(Patient).filter(Patient.id == vitals.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Create a new vitals record
    vitals_data = vitals.model_dump()
    vitals_data["recorded_by"] = user.id
    new_vitals = PatientVitals(**vitals_data)
    db.add(new_vitals)
    db.commit()
    db.refresh(new_vitals)

    return new_vitals

@router.get("/{patient_id}", response_model=List[PatientVitalsResponse])
def get_vitals(patient_id: int, db: Session = Depends(get_db), user: User = Depends(nurse_or_doctor)):
    # Fetch all vitals records for the patient
    vitals = db.query(PatientVitals).filter(PatientVitals.patient_id == patient_id).all()
    return vitals