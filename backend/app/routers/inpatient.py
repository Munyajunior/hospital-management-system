from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.admission import Inpatient, PatientAdmission
from models.user import User
from typing import List
from schemas.admission import InpatientCreate, InpatientResponse
from core.database import get_async_db
from core.dependencies import RoleChecker
from core.cache import cache

router = APIRouter(prefix="/inpatients", tags=["INPATIENT Management"])

nurse_or_doctor = RoleChecker(["nurse", "doctor", "admin"])

@router.post("/patients/", response_model=InpatientResponse)
async def update_inpatient(
    inpatient: InpatientCreate,
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(nurse_or_doctor)
):
    """Create inpatient record with async operations."""
    async with db.begin():
        result = await db.execute(
            select(PatientAdmission)
            .where(PatientAdmission.id == inpatient.patient_id)
        )
        patient = result.scalars().first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        inpatient_data = inpatient.model_dump()
        inpatient_data["updated_by"] = user.id
        new_inpatient_record = Inpatient(**inpatient_data)
        db.add(new_inpatient_record)
        await db.commit()
        await db.refresh(new_inpatient_record)
        return new_inpatient_record

@router.put("/patients/{in_patient_id}", response_model=InpatientResponse)
async def update_in_patient(
    in_patient_id: int, 
    updates: InpatientCreate, 
    db: AsyncSession = Depends(get_async_db), 
    user: User = Depends(nurse_or_doctor)
):
    """Update inpatient with async operations."""
    async with db.begin():
        result = await db.execute(
            select(Inpatient)
            .where(Inpatient.admission_id == in_patient_id)
        )
        in_patient = result.scalars().first()
        if not in_patient:
            raise HTTPException(status_code=404, detail="IN_PATIENT patient not found")

        for key, value in updates.model_dump(exclude_unset=True).items():
            setattr(in_patient, key, value)

        in_patient.updated_by = user.id
        await db.commit()
        await db.refresh(in_patient)
        return in_patient

@router.get("/patients/", response_model=List[InpatientResponse])
@cache(expire=60)  # Cache for 1 minute
async def list_in_patients(db: AsyncSession = Depends(get_async_db)):
    """List inpatients with caching."""
    result = await db.execute(select(Inpatient))
    return result.scalars().all()