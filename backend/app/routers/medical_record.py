from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from models.medical_records import MedicalRecord
from models.patient import Patient
from models.user import User
from schemas.medical_record import (
    MedicalRecordCreate, MedicalRecordUpdate, 
    MedicalRecordResponse
)
from core.database import get_async_db
from core.dependencies import RoleChecker
from core.cache import cache

router = APIRouter(prefix="/medical_records", tags=["Medical Records"])

authorized_users = RoleChecker(["admin", "doctor", "nurse"])
doctor_only = RoleChecker(["doctor"])
staff_access = RoleChecker(["admin", "nurse", "doctor"])

@router.post("/{patient_id}", response_model=MedicalRecordResponse)
async def create_medical_record(
    patient_id: int, 
    record_data: MedicalRecordCreate, 
    db: AsyncSession = Depends(get_async_db), 
    user: User = Depends(doctor_only)
):
    """Create medical record with async operations."""
    async with db.begin():
        result = await db.execute(
            select(Patient)
            .where(Patient.id == patient_id)
        )
        patient = result.scalars().first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        result = await db.execute(
            select(MedicalRecord)
            .where(MedicalRecord.patient_id == patient_id)
        )
        if result.scalars().first():
            raise HTTPException(
                status_code=400, 
                detail="Medical record already exists"
            )
        
        new_record = MedicalRecord(
            **record_data.model_dump(), 
            patient_id=patient_id, 
            created_by=user.id
        )
        db.add(new_record)
        await db.commit()
        await db.refresh(new_record)
        return new_record

@router.get("/", response_model=List[MedicalRecordResponse])
@cache(expire=120)  # Cache for 2 minutes
async def get_medical_record(
    patient_id: Optional[int] = Query(None), 
    db: AsyncSession = Depends(get_async_db), 
    user: User = Depends(staff_access)
):
    """Get medical records with filtering and caching."""
    query = (
        select(
            MedicalRecord.id,
            MedicalRecord.patient_id,
            Patient.full_name.label("patient_name"),
            MedicalRecord.created_by,
            User.full_name.label("created_by_name"),
            MedicalRecord.visit_date,
            MedicalRecord.diagnosis,
            MedicalRecord.treatment_plan,
            MedicalRecord.medical_history,
            MedicalRecord.prescription,
            MedicalRecord.lab_tests_requested,
            MedicalRecord.scans_requested,
            MedicalRecord.lab_tests_results,
            MedicalRecord.scan_results,
            MedicalRecord.notes,
            MedicalRecord.created_at,
            MedicalRecord.updated_at
        )
        .join(Patient, MedicalRecord.patient_id == Patient.id)
        .join(User, MedicalRecord.created_by == User.id)
    )
    
    if patient_id:
        query = query.where(MedicalRecord.patient_id == patient_id)
    
    result = await db.execute(query)
    return result.all()

@router.put("/{patient_id}", response_model=MedicalRecordResponse)
async def update_medical_record(
    patient_id: int, 
    updates: MedicalRecordUpdate, 
    db: AsyncSession = Depends(get_async_db), 
    user: User = Depends(doctor_only)
):
    """Update medical record with async operations."""
    async with db.begin():
        result = await db.execute(
            select(MedicalRecord)
            .where(MedicalRecord.patient_id == patient_id)
        )
        record = result.scalars().first()
        if not record:
            raise HTTPException(status_code=404, detail="Medical record not found")

        update_data = updates.model_dump(exclude_unset=True)
        append_flags = update_data.pop('append', {})

        for key, value in update_data.items():
            if value is not None:
                if append_flags.get(key, False) and getattr(record, key):
                    setattr(record, key, getattr(record, key) + "\n" + value)
                else:
                    setattr(record, key, value)

        await db.commit()
        await db.refresh(record)
        return record