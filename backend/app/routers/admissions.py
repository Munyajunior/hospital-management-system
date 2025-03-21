from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from models.user import User
from models.admission import PatientAdmission, AdmissionCategory, AdmissionStatus, Bed, ICUPatient, Inpatient
from models.patient import Patient
from schemas.admission import AdmissionCreate, AdmissionResponse
from core.database import get_db
from core.dependencies import RoleChecker
from sqlalchemy.sql import func
from typing import List, Optional

router = APIRouter(prefix="/admissions", tags=["Admissions"]) 

nurse_or_doctor = RoleChecker(["nurse", "doctor"])

@router.post("/", response_model=AdmissionResponse)
def admit_patient(admission_data: AdmissionCreate, db: Session = Depends(get_db), user: User = Depends(nurse_or_doctor)):
    """Admit a patient, automatically assigning a doctor if required."""
    
    # Auto-assign a bed if not provided
    bed = None
    if not admission_data.bed_id:
        bed = db.query(Bed).filter(Bed.ward_id == admission_data.ward_id, Bed.is_occupied == False).first()
        if not bed:
            raise HTTPException(status_code=400, detail="No available beds in the selected ward")
        admission_data.bed_id = bed.id
    
    # Ensure selected bed is available
    else:
        bed = db.query(Bed).filter(Bed.id == admission_data.bed_id, Bed.is_occupied == False).first()
        if not bed:
            raise HTTPException(status_code=400, detail="Selected bed is occupied or does not exist")
    
    bed.is_occupied = True  # Mark bed as occupied
    
    # Check if admitted patient is already assigned a doctor
    doctor_id = db.query(Patient).filter(Patient.id == admission_data.patient_id).first()
    if doctor_id.assigned_doctor_id:
        admission_data.assigned_doctor_id = doctor_id.assigned_doctor_id
        
    # Auto-assign a doctor for inpatients and ICU cases
    elif admission_data.category in [AdmissionCategory.INPATIENT, AdmissionCategory.ICU]:
        doctor = db.query(User).filter(User.role == "doctor").first()
        if not doctor:
            raise HTTPException(status_code=400, detail="No available doctors for assignment")
        admission_data.assigned_doctor_id = doctor.id

    try: 
        # Create the admission record
        new_admission = PatientAdmission(**admission_data.model_dump(), admitted_by=user.id)
        db.add(new_admission)
        db.commit()
        db.refresh(new_admission)

        # If the category is ICU, create an ICU patient record
        if admission_data.category == AdmissionCategory.ICU:
            icu_patient = ICUPatient(
                patient_id=admission_data.patient_id,
                admission_id=new_admission.id,
                status="Stable",  # Default status
                updated_by=user.id
            )
            db.add(icu_patient)
            db.commit()
            db.refresh(icu_patient)

        # If the category is Inpatient, create an Inpatient record
        elif admission_data.category == AdmissionCategory.INPATIENT:
            inpatient = Inpatient(
                patient_id=admission_data.patient_id,
                admission_id=new_admission.id,
                status="Stable",  # Default status
                updated_by=user.id
            )
            db.add(inpatient)
            db.commit()
            db.refresh(inpatient)

        return new_admission
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{admission_id}/discharge", response_model=AdmissionResponse)
def discharge_patient(admission_id: int, db: Session = Depends(get_db), user: User = Depends(nurse_or_doctor)):
    """Discharge a patient and free their assigned bed."""
    admission = db.query(PatientAdmission).filter(PatientAdmission.id == admission_id).first()
    
    if not admission:
        raise HTTPException(status_code=404, detail="Admission record not found")

    if admission.status == AdmissionStatus.DISCHARGED:
        raise HTTPException(status_code=400, detail="Patient is already discharged")

    # Free the assigned bed
    if admission.bed_id:
        bed = db.query(Bed).filter(Bed.id == admission.bed_id).first()
        if bed:
            bed.is_occupied = False  

    admission.discharge_date = func.now()
    admission.status = AdmissionStatus.DISCHARGED

    db.commit()
    db.refresh(admission)

    return admission


@router.get("/", response_model=List[AdmissionResponse])
def list_admissions(
    db: Session = Depends(get_db),
    user: User = Depends(nurse_or_doctor),
    status: Optional[AdmissionStatus] = Query(None),
    category: Optional[str] = Query(None),
    department_id: Optional[int] = Query(None),
    patient_id: Optional[int] = Query(None)
):
    """Retrieve a list of admissions with optional filters."""
    query = db.query(PatientAdmission)

    if status:
        query = query.filter(PatientAdmission.status == status)
    if category:
        query = query.filter(PatientAdmission.category == category)
    if department_id:
        query = query.filter(PatientAdmission.department_id == department_id)
    if patient_id:
        query = query.filter(PatientAdmission.patient_id == patient_id)

    admissions = query.all()
    return admissions


@router.get("/{admission_id}", response_model=AdmissionResponse)
def get_admission(admission_id: int, db: Session = Depends(get_db), user: User = Depends(nurse_or_doctor)):
    """Retrieve a single admission record by ID."""
    admission = db.query(PatientAdmission).filter(PatientAdmission.id == admission_id).first()

    if not admission:
        raise HTTPException(status_code=404, detail="Admission not found")

    return admission