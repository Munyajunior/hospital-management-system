from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.admission import PatientVitals, PatientAdmission
from models.patient import Patient
from models.user import User
from typing import List
from schemas.admission import (
    PatientVitalsCreate, PatientVitalsResponse, 
    PatientVitalsResponseTable
)
from core.database import get_async_db
from core.dependencies import RoleChecker
from core.cache import cache

router = APIRouter(prefix="/vitals", tags=["Patient Vitals"])

nurse_or_doctor = RoleChecker(["nurse", "doctor", "admin"])

@router.post("/", response_model=PatientVitalsResponse)
async def update_vitals(
    vitals: PatientVitalsCreate, 
    db: AsyncSession = Depends(get_async_db), 
    user: User = Depends(nurse_or_doctor)
):
    """Create vitals record with async operations."""
    async with db.begin():
        result = await db.execute(
            select(PatientAdmission)
            .where(PatientAdmission.id == vitals.patient_id)
        )
        patient = result.scalars().first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        vitals_data = vitals.model_dump()
        vitals_data["recorded_by"] = user.id
        new_vitals = PatientVitals(**vitals_data)
        db.add(new_vitals)
        await db.commit()
        await db.refresh(new_vitals)
        return new_vitals

@router.get("/{patient_id}", response_model=List[PatientVitalsResponse])
@cache(expire=60)  # Cache for 1 minute
async def get_vitals(
    patient_id: int, 
    db: AsyncSession = Depends(get_async_db), 
    user: User = Depends(nurse_or_doctor)
):
    """Get patient's vitals with caching."""
    result = await db.execute(
        select(PatientVitals)
        .where(PatientVitals.patient_id == patient_id)
    )
    vitals = result.scalars().all()
    return vitals

@router.get("/", response_model=List[PatientVitalsResponseTable])
@cache(expire=60)  # Cache for 1 minute
async def get_all_vitals(
    db: AsyncSession = Depends(get_async_db), 
    user: User = Depends(nurse_or_doctor)
):
    """Get all vitals with patient details and caching."""
    result = await db.execute(
        select(
            PatientVitals.id,
            PatientVitals.patient_id,
            Patient.full_name.label("patient_name"),
            PatientVitals.blood_pressure,
            PatientVitals.heart_rate,
            PatientVitals.temperature,
            PatientVitals.recorded_by,
            User.full_name.label("recorded_by_name"),
            PatientVitals.recorded_at
        )
        .join(Patient, PatientVitals.patient_id == Patient.id)
        .join(User, PatientVitals.recorded_by == User.id)
    )
    return result.all()