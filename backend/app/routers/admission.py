from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.user import User
from models.admission import PatientAdmission, AdmissionCategory, Bed
from schemas.admission import AdmissionCreate, AdmissionResponse
from core.database import get_db
from core.dependencies import RoleChecker

router = APIRouter(prefix="/admissions", tags=["Admissions"])

nurse_or_doctor = RoleChecker(["nurse", "doctor"])

@router.post("/", response_model=AdmissionResponse)
def admit_patient(admission_data: AdmissionCreate, db: Session = Depends(get_db), user: User = Depends(nurse_or_doctor)):
    """Admit a patient into the system, assigning them to a category, department, ward, and bed."""
    
    # Ensure bed is available
    if admission_data.bed_id:
        bed = db.query(Bed).filter(Bed.id == admission_data.bed_id, Bed.is_occupied == False).first()
        if not bed:
            raise HTTPException(status_code=400, detail="Selected bed is already occupied or does not exist")
        bed.is_occupied = True

    new_admission = PatientAdmission(**admission_data.model_dump(), admitted_by=user.id)
    db.add(new_admission)
    db.commit()
    db.refresh(new_admission)

    return new_admission


@router.put("/{admission_id}/discharge")
def discharge_patient(admission_id: int, db: Session = Depends(get_db), user=Depends(nurse_or_doctor)):
    """Discharge a patient and free their assigned bed."""
    admission = db.query(PatientAdmission).filter(PatientAdmission.id == admission_id).first()
    
    if not admission:
        raise HTTPException(status_code=404, detail="Admission record not found")

    if admission.bed_id:
        bed = db.query(Bed).filter(Bed.id == admission.bed_id).first()
        if bed:
            bed.is_occupied = False  # Free the bed
    
    admission.discharge_date = func.now()
    admission.status = "Discharged"

    db.commit()
    db.refresh(admission)

    return admission

