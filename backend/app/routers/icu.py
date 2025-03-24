from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.admission import ICUPatient, PatientAdmission
from models.user import User
from typing import List
from schemas.admission import ICUPatientCreate, ICUPatientResponse
from core.database import get_db
from core.dependencies import RoleChecker

router = APIRouter(prefix="/icu", tags=["ICU Management"])

nurse_or_doctor = RoleChecker(["nurse", "doctor", "admin"])

# @router.post("/patients/", response_model=ICUPatientResponse)
# def create_icu_patient(icu_patient: ICUPatientCreate, db: Session = Depends(get_db), user: User = Depends(nurse_or_doctor)):
#     """Create a new ICU patient record."""
#     new_icu_patient = ICUPatient(**icu_patient.model_dump(), updated_by=user.id)
#     db.add(new_icu_patient)
#     db.commit()
#     db.refresh(new_icu_patient)
#     return new_icu_patient

@router.post("/patients/", response_model=ICUPatientResponse)
def update_icu_patient(icu_patient: ICUPatientCreate,db: Session = Depends(get_db),user: User = Depends(nurse_or_doctor)):
    """Create a new ICU patient record."""
    # Check if the patient exists
    patient = db.query(PatientAdmission).filter(PatientAdmission.id == icu_patient.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Create a new ICU record
    icu_data = icu_patient.model_dump()
    icu_data["updated_by"] = user.id
    new_icu_record = ICUPatient(**icu_data)
    db.add(new_icu_record)
    db.commit()
    db.refresh(new_icu_record)

    return new_icu_record

@router.put("/patients/{icu_patient_id}", response_model=ICUPatientResponse)
def update_icu_patient(icu_patient_id: int, updates: ICUPatientCreate, db: Session = Depends(get_db), user: User = Depends(nurse_or_doctor)):
    """Update an ICU patient record."""
    icu_patient = db.query(ICUPatient).filter(ICUPatient.id == icu_patient_id).first()
    if not icu_patient:
        raise HTTPException(status_code=404, detail="ICU patient not found")

    for key, value in updates.model_dump(exclude_unset=True).items():
        setattr(icu_patient, key, value)

    icu_patient.updated_by = user.id
    db.commit()
    db.refresh(icu_patient)
    return icu_patient

@router.get("/patients/", response_model=List[ICUPatientResponse])
def list_icu_patients(db: Session = Depends(get_db)):
    """Retrieve a list of all ICU patients."""
    icu_patients = db.query(ICUPatient).all()
    return icu_patients

