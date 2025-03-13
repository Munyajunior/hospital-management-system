from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy.sql import func
from models.icu import ICUPatient, ICUStatus
from models.patient import Patient
from models.user import User
from schemas.icu import ICUCreate, ICUPatientResponse
from core.database import get_db
from core.dependencies import RoleChecker

router = APIRouter(prefix="/icu", tags=["ICU Management"])

staff_only  = RoleChecker(["nurse", "admin", "icu"])
doctor_only = RoleChecker(["doctor"])
@router.post("/", response_model=ICUPatientResponse)
def admit_patient_to_icu(icu_data: ICUCreate, db: Session = Depends(get_db), user: User = Depends(staff_only)):
    patient = db.query(Patient).filter(Patient.id == icu_data.patient_id).first()
    nurse = db.query(User).filter(User.id == icu_data.admitted_by).first()

    if not patient or not nurse:
        raise HTTPException(status_code=400, detail="Invalid patient ID or nurse ID")

    new_icu_patient = ICUPatient(**icu_data.model_dump())
    db.add(new_icu_patient)
    db.commit()
    db.refresh(new_icu_patient)
    return new_icu_patient

@router.get("/", response_model=List[ICUPatientResponse])
def get_icu_patients(db: Session = Depends(get_db), user: User = Depends(staff_only)):
    return db.query(ICUPatient).all()

@router.get("/{icu_id}", response_model=ICUPatientResponse)
def get_icu_patient(icu_id: int, db: Session = Depends(get_db), user: User = Depends(staff_only)):
    icu_patient = db.query(ICUPatient).filter(ICUPatient.id == icu_id).first()
    if not icu_patient:
        raise HTTPException(status_code=404, detail="ICU patient not found")
    return icu_patient

@router.put("/{icu_id}/update", response_model=ICUPatientResponse)
def update_icu_patient(icu_id: int, status: ICUStatus, db: Session = Depends(get_db), user: User = Depends(doctor_only)):
    icu_patient = db.query(ICUPatient).filter(ICUPatient.id == icu_id).first()
    if not icu_patient:
        raise HTTPException(status_code=404, detail="ICU patient not found")

    icu_patient.status = status
    if status == ICUStatus.DISCHARGED:
        icu_patient.discharge_date = func.now()

    db.commit()
    db.refresh(icu_patient)
    return icu_patient

@router.delete("/{icu_id}", status_code=status.HTTP_204_NO_CONTENT)
def discharge_icu_patient(icu_id: int, db: Session = Depends(get_db), user: User = Depends(doctor_only)):
    icu_patient = db.query(ICUPatient).filter(ICUPatient.id == icu_id).first()
    if not icu_patient:
        raise HTTPException(status_code=404, detail="ICU patient not found")

    db.delete(icu_patient)
    db.commit()
    return