from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from datetime import datetime
from models.radiology import RadiologyScan
from models.patient import Patient
from models.doctor import Doctor
from models.user import User
from schemas.radiology import (
    RadiologyScanCreate, RadiologyScanResponse, 
    RadiologyScanUpdate, RadiologyScanStatus
)
from core.database import get_async_db
from core.dependencies import RoleChecker
from core.cache import cache

router = APIRouter(prefix="/radiology", tags=["Radiology"])

doctor_only = RoleChecker(["doctor"])
staff_only = RoleChecker(["radiologist"])

@router.post("/", response_model=RadiologyScanResponse)
async def create_radiology_scan(
    radiology_scan: RadiologyScanCreate, 
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(doctor_only)
):
    """Create radiology scan with async operations."""
    async with db.begin():
        result = await db.execute(
            select(Patient)
            .where(Patient.id == radiology_scan.patient_id)
        )
        patient = result.scalars().first()
        
        result = await db.execute(
            select(Doctor)
            .where(Doctor.id == radiology_scan.requested_by)
        )
        doctor = result.scalars().first()

        if not patient or not doctor:
            raise HTTPException(
                status_code=400, 
                detail="Invalid patient ID or doctor ID"
            )

        new_radiology_scan = RadiologyScan(
            patient_id=radiology_scan.patient_id,
            requested_by=user.id,
            scan_type=radiology_scan.scan_type,
            additional_notes=radiology_scan.additional_notes
        )
        db.add(new_radiology_scan)
        await db.commit()
        await db.refresh(new_radiology_scan)
        return new_radiology_scan

@router.get("/", response_model=List[RadiologyScanResponse])
@cache(expire=120)  # Cache for 2 minutes
async def get_radiology_scans(db: AsyncSession = Depends(get_async_db)):
    """List radiology scans with caching."""
    result = await db.execute(select(RadiologyScan))
    return result.scalars().all()

@router.get("/scan/{doctor_id}", response_model=List[RadiologyScanResponse])
@cache(expire=120)  # Cache for 2 minutes
async def get_doctor_radiology_scans(
    doctor_id: int, 
    db: AsyncSession = Depends(get_async_db), 
    user: User = Depends(doctor_only)
):
    """Get doctor's radiology scans with caching."""
    result = await db.execute(
        select(RadiologyScan)
        .where(RadiologyScan.requested_by == doctor_id)
    )
    radiology_scan = result.scalars().all()
    return radiology_scan if radiology_scan else []

@router.get("/{scan_id}", response_model=RadiologyScanResponse)
@cache(expire=120)  # Cache for 2 minutes
async def get_radiology_scan(
    scan_id: int, 
    db: AsyncSession = Depends(get_async_db), 
    user: User = Depends(staff_only)
):
    """Get radiology scan with caching."""
    result = await db.execute(
        select(RadiologyScan)
        .where(RadiologyScan.id == scan_id)
    )
    radiology_scan = result.scalars().first()
    if not radiology_scan:
        raise HTTPException(status_code=404, detail="Radiology scan not found")
    return radiology_scan

@router.put("/{scan_id}/in-progress", response_model=RadiologyScanResponse)
async def update_radiology_scan_status(
    scan_id: int, 
    update: RadiologyScanUpdate, 
    db: AsyncSession = Depends(get_async_db), 
    user: User = Depends(staff_only)
):
    """Update radiology scan status with async operations."""
    async with db.begin():
        result = await db.execute(
            select(RadiologyScan)
            .where(RadiologyScan.id == scan_id)
        )
        radiology_scan = result.scalars().first()
        if not radiology_scan:
            raise HTTPException(status_code=404, detail="Radiology scan not found")

        if update.status not in RadiologyScanStatus.IN_PROGRESS:
            raise HTTPException(
                status_code=400, 
                detail="Invalid status value. Expected 'In Progress'"
            )

        radiology_scan.status = RadiologyScanStatus.IN_PROGRESS
        if update.results:
            radiology_scan.results = update.results
            
        await db.commit()
        await db.refresh(radiology_scan)
        return radiology_scan

@router.put("/{scan_id}/update", response_model=RadiologyScanResponse)
async def update_radiology_scan(
    scan_id: int, 
    update: RadiologyScanUpdate, 
    db: AsyncSession = Depends(get_async_db), 
    user: User = Depends(staff_only)
):
    """Update radiology scan with async operations."""
    async with db.begin():
        result = await db.execute(
            select(RadiologyScan)
            .where(RadiologyScan.id == scan_id)
        )
        radiology_scan = result.scalars().first()
        if not radiology_scan:
            raise HTTPException(status_code=404, detail="Radiology scan not found")

        if update.status not in RadiologyScanStatus:
            raise HTTPException(
                status_code=400, 
                detail="Invalid status value"
            )

        radiology_scan.status = update.status
        if update.status == RadiologyScanStatus.COMPLETED and update.results:
            radiology_scan.results = update.results
            radiology_scan.completed_date = func.now()
        else:
            raise HTTPException(
                status_code=400, 
                detail="Results Missing!!! please Enter Results"
            )
        
        await db.commit()
        await db.refresh(radiology_scan)
        return radiology_scan

@router.delete("/{scan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_radiology_scan(
    scan_id: int, 
    db: AsyncSession = Depends(get_async_db)
):
    """Delete radiology scan with async operations."""
    async with db.begin():
        result = await db.execute(
            select(RadiologyScan)
            .where(RadiologyScan.id == scan_id)
        )
        radiology_scan = result.scalars().first()
        if not radiology_scan:
            raise HTTPException(status_code=404, detail="Radiology scan not found")

        await db.delete(radiology_scan)
        await db.commit()