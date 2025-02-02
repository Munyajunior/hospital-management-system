from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.session import get_db
from utils.dependencies import role_required
from models.user import UserRole
from backend.schemas.patient import PatientCreate, PatientResponse
from backend.models.patient import Patient

router = APIRouter()

@router.post("/patients", response_model=PatientResponse, dependencies=[Depends(role_required([UserRole.ADMIN, UserRole.NURSE, UserRole.SECRETARY]))])
def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    """
    Allows authorized users to create a patient record.
    """
    new_patient = Patient(**patient.dict())
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return new_patient

# Get all patients
@router.get("/patients/all")
def get_patients(db: Session = Depends(get_db)):
    return db.query(Patient).all()
