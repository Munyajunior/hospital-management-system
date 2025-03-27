from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from models.appointment import Appointment, AppointmentStatus
from models.patient import Patient
from models.user import User
from schemas.appointment import (
    AppointmentCreate, AppointmentResponse, 
    AppointmentUpdate, DoctorAppointmentResponse,
    AppointmentReschedule
)
from core.database import get_async_db
from core.dependencies import RoleChecker
from core.cache import cache

router = APIRouter(prefix="/appointments", tags=["Appointments"])

staff_only = RoleChecker(["doctor","nurse"])

@router.post("/", response_model=AppointmentResponse)
async def create_appointment(
    appointment: AppointmentCreate, 
    db: AsyncSession = Depends(get_async_db), 
    user: User = Depends(staff_only)
):
    """Create appointment with async operations."""
    async with db.begin():
        result = await db.execute(
            select(Patient)
            .where(Patient.id == appointment.patient_id)
        )
        patient = result.scalars().first()
        if not patient:
            raise HTTPException(status_code=400, detail="Invalid patient ID")

        new_appointment = Appointment(**appointment.model_dump())
        db.add(new_appointment)
        await db.commit()
        await db.refresh(new_appointment)
        return new_appointment

@router.get("/", response_model=List[AppointmentResponse])
@cache(expire=120)  # Cache for 2 minutes
async def get_appointments(
    db: AsyncSession = Depends(get_async_db), 
    user: User = Depends(staff_only)
):
    """Get all appointments with caching."""
    result = await db.execute(select(Appointment))
    appointments = result.scalars().all()
    return appointments if appointments else []

@router.get("/doctor/{doctor_id}/", response_model=List[DoctorAppointmentResponse])
@cache(expire=120)  # Cache for 2 minutes
async def get_doctor_appointments(
    doctor_id: int, 
    db: AsyncSession = Depends(get_async_db), 
    user: User = Depends(staff_only)
):
    """Get doctor's appointments with async operations."""
    result = await db.execute(
        select(Appointment)
        .where(Appointment.doctor_id == doctor_id)
    )
    appointments = result.scalars().all()
    return appointments if appointments else []

@router.get("/{appointment_id}/", response_model=AppointmentResponse)
@cache(expire=120)  # Cache for 2 minutes
async def get_appointment(
    appointment_id: int, 
    db: AsyncSession = Depends(get_async_db), 
    user: User = Depends(staff_only)
):
    """Get single appointment with caching."""
    result = await db.execute(
        select(Appointment)
        .where(Appointment.id == appointment_id)
    )
    appointment = result.scalars().first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment

@router.put("/{appointment_id}/update", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: int, 
    update_data: AppointmentUpdate, 
    db: AsyncSession = Depends(get_async_db), 
    user: User = Depends(staff_only)
):
    """Update appointment with async operations."""
    async with db.begin():
        result = await db.execute(
            select(Appointment)
            .where(Appointment.id == appointment_id)
        )
        appointment = result.scalars().first()
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")

        if update_data.status not in AppointmentStatus.__members__.values():
            raise HTTPException(status_code=400, detail="Invalid status value")
        
        appointment.status = update_data.status
        await db.commit()
        await db.refresh(appointment)
        return appointment

@router.put("/{appointment_id}/reschedule", response_model=AppointmentResponse)
async def reschedule_appointment(
    appointment_id: int, 
    update_data: AppointmentReschedule, 
    db: AsyncSession = Depends(get_async_db), 
    user: User = Depends(staff_only)
):
    """Reschedule appointment with async operations."""
    async with db.begin():
        result = await db.execute(
            select(Appointment)
            .where(Appointment.id == appointment_id)
        )
        appointment = result.scalars().first()
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")

        if update_data.status not in AppointmentStatus.__members__.values():
            raise HTTPException(status_code=400, detail="Invalid status value")
        
        appointment.status = update_data.status
        appointment.datetime = update_data.datetime
        
        await db.commit()
        await db.refresh(appointment)
        return appointment

@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_appointment(
    appointment_id: int, 
    db: AsyncSession = Depends(get_async_db), 
    user: User = Depends(staff_only)
):
    """Delete appointment with async operations."""
    async with db.begin():
        result = await db.execute(
            select(Appointment)
            .where(Appointment.id == appointment_id)
        )
        appointment = result.scalars().first()
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")

        await db.delete(appointment)
        await db.commit()