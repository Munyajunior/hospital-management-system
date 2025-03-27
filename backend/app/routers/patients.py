from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from models.patient import Patient
from models.admission import (
    PatientAdmission, Bed, Ward, Department, 
    Inpatient, ICUPatient
)
from models.user import User
from models.doctor import Doctor
from schemas.patients import (
    PatientCreate, PatientCreateResponse, 
    PatientResponse, PatientUpdate
)
from schemas.admission import AdmissionCategory
from core.database import get_async_db
from utils.security import hash_password, generate_password
from utils.email_util import send_password_email
from core.dependencies import RoleChecker
from core.cache import cache

router = APIRouter(prefix="/patients", tags=["Patients"])

staff_only = RoleChecker(["admin", "nurse", "receptionist"])
doctor_or_nurse = RoleChecker(["doctor", "nurse", "admin"])

@router.post("/", response_model=PatientCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    patient: PatientCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(staff_only)
):
    """Create patient with emergency handling and async operations."""
    async with db.begin():
        # Check if email exists
        result = await db.execute(
            select(Patient)
            .where(Patient.email == patient.email)
        )
        existing_patient = result.scalars().first()
        if existing_patient:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered."
            )

        # Generate password and hash
        password = generate_password()
        password_hash = hash_password(password)

        # Prepare patient data
        patient_data = patient.model_dump()
        patient_data["hashed_password"] = password_hash
        patient_data["registered_by"] = current_user.id
        patient_data["category"] = "inpatient" if patient.emergency else "outpatient"

        # Create patient
        new_patient = Patient(**patient_data)
        db.add(new_patient)
        await db.commit()
        await db.refresh(new_patient)

        # Handle emergency admission
        if patient.emergency:
            if not patient.category or not patient.department_id or not patient.ward_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category, department, and ward are required for emergency admission."
                )

            if patient.category not in [AdmissionCategory.INPATIENT, AdmissionCategory.ICU]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid category for emergency admission. Must be 'Inpatient' or 'ICU'."
                )

            # Validate department
            result = await db.execute(
                select(Department)
                .where(Department.id == patient.department_id)
            )
            department = result.scalars().first()
            if not department:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Department not found."
                )

            # Validate ward
            result = await db.execute(
                select(Ward)
                .where(Ward.id == patient.ward_id)
            )
            ward = result.scalars().first()
            if not ward:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Ward not found."
                )

            if ward.department_id != department.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ward does not belong to the selected department."
                )

            # Find available bed
            result = await db.execute(
                select(Bed)
                .where(
                    Bed.ward_id == ward.id,
                    Bed.is_occupied == False
                )
                .limit(1)
            )
            bed = result.scalars().first()
            if not bed:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No available beds in the selected ward."
                )

            # Create admission
            admission_data = {
                "patient_id": new_patient.id,
                "category": patient.category,
                "department_id": department.id,
                "ward_id": ward.id,
                "bed_id": bed.id,
                "assigned_doctor_id": patient.assigned_doctor_id,
                "admitted_by": current_user.id,
                "status": "Admitted"
            }
            new_admission = PatientAdmission(**admission_data)
            db.add(new_admission)
            bed.is_occupied = True

            # Create specific admission type record
            if admission_data["category"] == AdmissionCategory.ICU:
                icu_patient = ICUPatient(
                    patient_id=admission_data["patient_id"],
                    admission_id=new_admission.id,
                    status="Critical",
                    updated_by=current_user.id
                )
                db.add(icu_patient)
            elif admission_data["category"] == AdmissionCategory.INPATIENT:
                inpatient = Inpatient(
                    patient_id=admission_data["patient_id"],
                    admission_id=new_admission.id,
                    status="Stable",
                    updated_by=current_user.id
                )
                db.add(inpatient)

            await db.commit()

        # Send password email (commented out for now)
        email_sent = await send_password_email(new_patient.email, password)
        if not email_sent:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send password to email."
            )

        return {**new_patient.__dict__, "password": password}

@router.get("/", response_model=List[PatientResponse])
@cache(expire=120)  # Cache for 2 minutes
async def get_patients(
    emergency: Optional[bool] = Query(None), 
    patient_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_async_db), 
    user: User = Depends(doctor_or_nurse)
):
    """List patients with filtering and caching."""
    query = (
        select(
            Patient.id,
            Patient.full_name,
            Patient.date_of_birth,
            Patient.gender,
            Patient.role,
            Patient.email,
            Patient.address, 
            Patient.contact_number, 
            Patient.category, 
            Patient.emergency,
            Patient.assigned_doctor_id,
            Doctor.full_name.label("assigned_doctor_name"),
            Patient.registered_by,
            User.id.label("registered_by_name"),
            Patient.created_at
        )
        .join(Doctor, Patient.assigned_doctor_id == Doctor.id)
        .join(User, Patient.registered_by == User.id)
    )
    
    if emergency is not None:
        query = query.where(Patient.emergency == emergency)
    if patient_id:
        query = query.where(Patient.id == patient_id)
    
    result = await db.execute(query)
    return result.all()

@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: int, 
    patient_data: PatientUpdate, 
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(doctor_or_nurse)
):
    """Update patient with async operations."""
    async with db.begin():
        result = await db.execute(
            select(Patient)
            .where(Patient.id == patient_id)
        )
        patient = result.scalars().first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        for key, value in patient_data.model_dump(exclude_unset=True).items():
            setattr(patient, key, value)

        await db.commit()
        await db.refresh(patient)
        return patient

@router.put("/{patient_id}/assign-category/{category}", response_model=PatientResponse)
async def update_patient_category(
    patient_id: int, 
    category: str, 
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(doctor_or_nurse)
):
    """Update patient category with async operations."""
    if category not in ["outpatient", "inpatient", "ICU"]:
        raise HTTPException(status_code=400, detail="Invalid category")

    async with db.begin():
        result = await db.execute(
            select(Patient)
            .where(Patient.id == patient_id)
        )
        patient = result.scalars().first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        patient.category = category
        await db.commit()
        await db.refresh(patient)
        return patient 

@router.put("/{patient_id}/assign/{doctor_id}", response_model=PatientResponse)
async def assign_patient_to_doctor(
    patient_id: int, 
    doctor_id: int, 
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(staff_only)
):
    """Assign patient to doctor with async operations."""
    async with db.begin():
        result = await db.execute(
            select(Patient)
            .where(Patient.id == patient_id)
        )
        patient = result.scalars().first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        result = await db.execute(
            select(User)
            .where(User.id == doctor_id, User.role == "doctor")
        )
        doctor = result.scalars().first()
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")

        patient.assigned_doctor_id = doctor_id
        await db.commit()
        await db.refresh(patient)
        return patient

@router.put("/{patient_id}/update-medical-records", response_model=PatientResponse)
async def update_medical_records(
    patient_id: int, 
    updates: PatientUpdate, 
    db: AsyncSession = Depends(get_async_db)
):
    """Update medical records with async operations."""
    async with db.begin():
        result = await db.execute(
            select(Patient)
            .where(Patient.id == patient_id)
        )
        patient = result.scalars().first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        for key, value in updates.model_dump(exclude_unset=True).items():
            setattr(patient, key, value)
        
        await db.commit()
        await db.refresh(patient)
        return patient