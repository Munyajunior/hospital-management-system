from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from schemas.doctor import DoctorCreate, DoctorResponse
from models.doctor import Doctor
from schemas.patients import PatientResponse
from models.patient import Patient
from models.user import User
from core.database import get_async_db
from core.dependencies import RoleChecker, get_current_active_user
from utils.security import hash_password
from core.cache import cache

router = APIRouter(prefix="/doctors", tags=["Doctors"])

admin_only = RoleChecker(["admin"])
staff_only = RoleChecker(["doctor","admin","nurse", "receptionists"])

@router.post("/", response_model=DoctorResponse)
async def create_doctor(
    doctor: DoctorCreate, 
    db: AsyncSession = Depends(get_async_db), 
    user: User = Depends(admin_only)
):
    """Create doctor with async operations."""
    async with db.begin():
        # Check if doctor email exists
        result = await db.execute(
            select(Doctor)
            .where(Doctor.email == doctor.email)
        )
        existing_doctor = result.scalars().first()
        if existing_doctor:
            raise HTTPException(
                status_code=400, 
                detail="A doctor with this email already exists"
            )

        # Check if user email exists
        result = await db.execute(
            select(User)
            .where(User.email == doctor.email)
        )
        existing_user = result.scalars().first()
        if existing_user:
            raise HTTPException(
                status_code=400, 
                detail="A user with this email already exists"
            )
        
        # Create User
        new_user = User(
            full_name=doctor.full_name,
            email=doctor.email,
            contact_number=doctor.contact_number,
            address=doctor.address,
            hashed_password=hash_password(doctor.password),
            role="doctor"
        )
        db.add(new_user)
        await db.flush()  # Get the user ID before creating Doctor

        # Create Doctor
        new_doctor = Doctor(
            id=new_user.id,
            full_name=doctor.full_name,
            specialization=doctor.specialization,
            contact_number=doctor.contact_number,
            address=doctor.address,
            email=doctor.email
        )
        db.add(new_doctor)
        await db.commit()
        await db.refresh(new_doctor)
        return new_doctor

@router.get("/", response_model=List[DoctorResponse])
@cache(expire=120)  # Cache for 2 minutes
async def get_doctors(
    db: AsyncSession = Depends(get_async_db), 
    user: User = Depends(staff_only)
):
    """List doctors with caching."""
    result = await db.execute(select(Doctor))
    return result.scalars().all()

@router.get("/{doctor_id}", response_model=DoctorResponse)
@cache(expire=120)  # Cache for 2 minutes
async def get_doctor(
    doctor_id: int, 
    db: AsyncSession = Depends(get_async_db), 
    user: User = Depends(staff_only)
):
    """Get doctor with caching."""
    result = await db.execute(
        select(Doctor)
        .where(Doctor.id == doctor_id)
    )
    doctor = result.scalars().first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor

@router.put("/{doctor_id}", response_model=DoctorResponse)
async def update_doctor(
    doctor_id: int, 
    doctor_data: DoctorCreate, 
    db: AsyncSession = Depends(get_async_db), 
    user: User = Depends(admin_only)
):
    """Update doctor with async operations."""
    async with db.begin():
        result = await db.execute(
            select(Doctor)
            .where(Doctor.id == doctor_id)
        )
        doctor = result.scalars().first()
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")
        
        for key, value in doctor_data.model_dump().items():
            setattr(doctor, key, value)
        
        await db.commit()
        await db.refresh(doctor)
        return doctor

@router.get("/{doctor_id}/patients", response_model=List[PatientResponse])
@cache(expire=60)  # Cache for 1 minute
async def get_assigned_patients(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    _: User = Depends(RoleChecker(["doctor"]))
):
    """Get doctor's patients with caching."""
    result = await db.execute(
        select(Patient)
        .where(Patient.assigned_doctor_id == current_user.id)
    )
    patients = result.scalars().all()
    if not patients:
        raise HTTPException(status_code=404, detail="No patients assigned")
    return patients

@router.delete("/{doctor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_doctor(
    doctor_id: int, 
    db: AsyncSession = Depends(get_async_db), 
    user: User = Depends(admin_only)
):
    """Delete doctor with async operations."""
    async with db.begin():
        result = await db.execute(
            select(Doctor)
            .where(Doctor.id == doctor_id)
        )
        doctor = result.scalars().first()
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")

        await db.delete(doctor)
        await db.commit()