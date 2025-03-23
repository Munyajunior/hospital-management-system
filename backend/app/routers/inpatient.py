from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.admission import Inpatient
from models.user import User
from typing import List
from schemas.admission import InpatientCreate, InpatientResponse
from core.database import get_db
from core.dependencies import RoleChecker

router = APIRouter(prefix="/inpatients", tags=["INPATIENT Management"])

nurse_or_doctor = RoleChecker(["nurse", "doctor", "admin"])

@router.post("/patients/", response_model=InpatientResponse)
def create_inpatient_patient(in_patient: InpatientCreate, db: Session = Depends(get_db), user: User = Depends(nurse_or_doctor)):
    """Create a new INPATIENT patient record."""
    new_in_patient = Inpatient(**in_patient.model_dump(), updated_by=user.id)
    db.add(new_in_patient)
    db.commit()
    db.refresh(new_in_patient)
    return new_in_patient

@router.put("/patients/{in_patient_id}", response_model=InpatientResponse)
def update_in_patient(in_patient_id: int, updates: InpatientCreate, db: Session = Depends(get_db), user: User = Depends(nurse_or_doctor)):
    """Update an ICU patient record."""
    in_patient = db.query(Inpatient).filter(Inpatient.admission_id == in_patient_id).first()
    if not in_patient:
        raise HTTPException(status_code=404, detail="IN_PATIENT patient not found")

    for key, value in updates.model_dump(exclude_unset=True).items():
        setattr(in_patient, key, value)

    in_patient.updated_by = user.id
    db.commit()
    db.refresh(in_patient)
    return in_patient

@router.get("/patients/", response_model=List[InpatientResponse])
def list_in_patients(db: Session = Depends(get_db)):
    """Retrieve a list of all IN_PATIENT patients."""
    in_patients = db.query(Inpatient).all()
    return in_patients
