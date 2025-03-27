from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.admission import ICUPatient, PatientAdmission
from models.user import User
from typing import List
from schemas.admission import ICUPatientCreate, ICUPatientResponse
from core.database import get_async_db
from core.dependencies import RoleChecker
from core.cache import cache

router = APIRouter(prefix="/icu", tags=["ICU Management"])

nurse_or_doctor = RoleChecker(["nurse", "doctor", "admin"])

@router.post("/patients/", response_model=ICUPatientResponse)
async def update_icu_patient(
    icu_patient: ICUPatientCreate,
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(nurse_or_doctor)
):
    """Create ICU patient record with async operations."""
    async with db.begin():
        result = await db.execute(
            select(PatientAdmission)
            .where(PatientAdmission.id == icu_patient.patient_id)
        )
        patient = result.scalars().first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        icu_data = icu_patient.model_dump()
        icu_data["updated_by"] = user.id
        new_icu_record = ICUPatient(**icu_data)
        db.add(new_icu_record)
        await db.commit()
        await db.refresh(new_icu_record)
        return new_icu_record

@router.put("/patients/{icu_patient_id}", response_model=ICUPatientResponse)
async def update_icu_patient(
    icu_patient_id: int, 
    updates: ICUPatientCreate, 
    db: AsyncSession = Depends(get_async_db), 
    user: User = Depends(nurse_or_doctor)
):
    """Update ICU patient with async operations."""
    async with db.begin():
        result = await db.execute(
            select(ICUPatient)
            .where(ICUPatient.id == icu_patient_id)
        )
        icu_patient = result.scalars().first()
        if not icu_patient:
            raise HTTPException(status_code=404, detail="ICU patient not found")

        for key, value in updates.model_dump(exclude_unset=True).items():
            setattr(icu_patient, key, value)

        icu_patient.updated_by = user.id
        await db.commit()
        await db.refresh(icu_patient)
        return icu_patient

@router.get("/patients/", response_model=List[ICUPatientResponse])
@cache(expire=60)  # Cache for 1 minute
async def list_icu_patients(db: AsyncSession = Depends(get_async_db)):
    """List ICU patients with caching."""
    result = await db.execute(select(ICUPatient))
    return result.scalars().all()