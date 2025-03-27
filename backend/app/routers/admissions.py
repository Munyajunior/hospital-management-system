from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased
from typing import List, Optional
from models.user import User
from models.admission import (
    PatientAdmission, AdmissionCategory, AdmissionStatus, 
    Bed, ICUPatient, Inpatient, Ward, Department
)
from models.patient import Patient
from schemas.admission import (
    AdmissionCreate, AdmissionResponse, 
    AdmissionTableResponse
)
from core.database import get_async_db
from core.dependencies import RoleChecker
from sqlalchemy.sql import func
from core.cache import cache
from core.batching import batch_query

router = APIRouter(prefix="/admissions", tags=["Admissions"]) 

nurse_or_doctor = RoleChecker(["nurse", "doctor", "admin"])

@router.post("/", response_model=AdmissionResponse)
async def admit_patient(
    admission_data: AdmissionCreate, 
    db: AsyncSession = Depends(get_async_db), 
    user: User = Depends(nurse_or_doctor)
):
    """Admit a patient with async operations and transaction management."""
    async with db.begin():
        # Auto-assign a bed if not provided
        bed = None
        if not admission_data.bed_id:
            result = await db.execute(
                select(Bed)
                .where(
                    Bed.ward_id == admission_data.ward_id, 
                    Bed.is_occupied == False
                )
                .limit(1)
            )
            bed = result.scalars().first()
            if not bed:
                raise HTTPException(
                    status_code=400, 
                    detail="No available beds in the selected ward"
                )
            admission_data.bed_id = bed.id
        else:
            result = await db.execute(
                select(Bed)
                .where(
                    Bed.id == admission_data.bed_id, 
                    Bed.is_occupied == False
                )
            )
            bed = result.scalars().first()
            if not bed:
                raise HTTPException(
                    status_code=400, 
                    detail="Selected bed is occupied or does not exist"
                )
        
        bed.is_occupied = True

        # Check if patient has an assigned doctor
        result = await db.execute(
            select(Patient)
            .where(Patient.id == admission_data.patient_id)
        )
        patient = result.scalars().first()
        if patient.assigned_doctor_id:
            admission_data.assigned_doctor_id = patient.assigned_doctor_id
        elif admission_data.category in [AdmissionCategory.INPATIENT, AdmissionCategory.ICU]:
            result = await db.execute(
                select(User)
                .where(User.role == "doctor")
                .limit(1)
            )
            doctor = result.scalars().first()
            if not doctor:
                raise HTTPException(
                    status_code=400, 
                    detail="No available doctors for assignment"
                )
            admission_data.assigned_doctor_id = doctor.id

        # Create admission record
        new_admission = PatientAdmission(
            **admission_data.model_dump(), 
            admitted_by=user.id
        )
        db.add(new_admission)
        await db.commit()
        await db.refresh(new_admission)

        # Create specific admission type record
        if admission_data.category == AdmissionCategory.ICU:
            icu_patient = ICUPatient(
                patient_id=admission_data.patient_id,
                admission_id=new_admission.id,
                status="Stable",
                updated_by=user.id
            )
            db.add(icu_patient)
        elif admission_data.category == AdmissionCategory.INPATIENT:
            inpatient = Inpatient(
                patient_id=admission_data.patient_id,
                admission_id=new_admission.id,
                status="Stable",
                updated_by=user.id
            )
            db.add(inpatient)
        
        await db.commit()
        return new_admission

@router.put("/{admission_id}/discharge", response_model=AdmissionResponse)
@cache(expire=60)  # Cache discharge operations for 1 minute
async def discharge_patient(
    admission_id: int, 
    db: AsyncSession = Depends(get_async_db), 
    user: User = Depends(nurse_or_doctor)
):
    """Discharge a patient with async operations."""
    async with db.begin():
        result = await db.execute(
            select(PatientAdmission)
            .where(PatientAdmission.id == admission_id)
        )
        admission = result.scalars().first()
        
        if not admission:
            raise HTTPException(
                status_code=404, 
                detail="Admission record not found"
            )

        if admission.status == AdmissionStatus.DISCHARGED:
            raise HTTPException(
                status_code=400, 
                detail="Patient is already discharged"
            )

        # Free the assigned bed
        if admission.bed_id:
            result = await db.execute(
                select(Bed)
                .where(Bed.id == admission.bed_id)
            )
            bed = result.scalars().first()
            if bed:
                bed.is_occupied = False  

        admission.discharge_date = func.now()
        admission.status = AdmissionStatus.DISCHARGED

        await db.commit()
        await db.refresh(admission)
        return admission

@router.get("/", response_model=List[AdmissionTableResponse])
@cache(expire=120)  # Cache for 2 minutes
@batch_query(batch_size=50)  # Process in batches of 50
async def list_admissions(
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(nurse_or_doctor),
    status: Optional[AdmissionStatus] = Query(None),
    category: Optional[str] = Query(None),
    department_id: Optional[int] = Query(None),
    patient_id: Optional[int] = Query(None)
):
    """Optimized admission listing with joins and caching."""
    Doctor = aliased(User)
    
    query = (
        select(
            PatientAdmission.id,
            PatientAdmission.patient_id,
            Patient.full_name.label("patient_name"),
            PatientAdmission.admitted_by,
            User.full_name.label("admitted_by_name"),
            PatientAdmission.assigned_doctor_id,
            Doctor.full_name.label("assigned_doctor_name"),
            PatientAdmission.category,
            PatientAdmission.department_id,
            Department.name.label("department_name"),
            PatientAdmission.ward_id,
            Ward.name.label("ward_name"),
            PatientAdmission.bed_id,
            Bed.bed_number.label("bed_number"),
            PatientAdmission.status,
            PatientAdmission.admission_date,
            PatientAdmission.discharge_date
        )
        .join(Patient, PatientAdmission.patient_id == Patient.id)
        .join(User, PatientAdmission.admitted_by == User.id)
        .outerjoin(Doctor, PatientAdmission.assigned_doctor_id == Doctor.id)
        .join(Department, PatientAdmission.department_id == Department.id)
        .join(Ward, PatientAdmission.ward_id == Ward.id)
        .join(Bed, PatientAdmission.bed_id == Bed.id)
    )
    
    if status:
        query = query.where(PatientAdmission.status == status)
    if category:
        query = query.where(PatientAdmission.category == category)
    if department_id:
        query = query.where(PatientAdmission.department_id == department_id)
    if patient_id:
        query = query.where(PatientAdmission.patient_id == patient_id)

    result = await db.execute(query)
    return result.all()