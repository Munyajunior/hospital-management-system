from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.session import get_db
from models.icu import ICUAdmission
from schemas.icu import ICUAdmissionCreate, ICUAdmissionResponse

router = APIRouter()

@router.post("/", response_model=ICUAdmissionResponse)
def admit_patient_to_icu(admission: ICUAdmissionCreate, db: Session = Depends(get_db)):
    new_admission = ICUAdmission(**admission.dict())
    db.add(new_admission)
    db.commit()
    db.refresh(new_admission)
    return new_admission

@router.get("/", response_model=list[ICUAdmissionResponse])
def get_icu_admissions(db: Session = Depends(get_db)):
    return db.query(ICUAdmission).all()
