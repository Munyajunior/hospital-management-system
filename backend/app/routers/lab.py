from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from models.lab import LabTest, LabTestStatus
from models.patient import Patient
from models.user import User
from schemas.lab import LabTestCreate, LabTestResponse, LabTestUpdate
from core.database import get_async_db
from core.dependencies import RoleChecker
from core.cache import cache

router = APIRouter(prefix="/lab", tags=["Lab"])

doctor_only = RoleChecker(["doctor"])
lab_staff_only = RoleChecker(["lab_technician"])

@router.post("/", response_model=LabTestResponse)
async def request_lab_test(
    lab_test: LabTestCreate, 
    db: AsyncSession = Depends(get_async_db), 
    user: User = Depends(doctor_only)
):
    """Create lab test with async operations."""
    async with db.begin():
        result = await db.execute(
            select(Patient)
            .where(Patient.id == lab_test.patient_id)
        )
        patient = result.scalars().first()
        if not patient:
            raise HTTPException(status_code=400, detail="Invalid patient ID")

        new_lab_test = LabTest(
            requested_by=user.id,
            patient_id=lab_test.patient_id,
            test_type=lab_test.test_type,
            additional_notes=lab_test.additional_notes
        )
        db.add(new_lab_test)
        await db.commit()
        await db.refresh(new_lab_test)
        return new_lab_test

@router.get("/", response_model=List[LabTestResponse])
@cache(expire=120)  # Cache for 2 minutes
async def get_lab_tests(
    db: AsyncSession = Depends(get_async_db), 
    user: User = Depends(lab_staff_only)
):
    """List lab tests with caching."""
    result = await db.execute(select(LabTest))
    return result.scalars().all()

@router.get("/test/{doctor_id}", response_model=List[LabTestResponse])
@cache(expire=120)  # Cache for 2 minutes
async def get_lab_test_requested(
    doctor_id:int, 
    db: AsyncSession = Depends(get_async_db), 
    user: User = Depends(doctor_only)
):
    """Get doctor's lab tests with caching."""
    result = await db.execute(
        select(LabTest)
        .where(LabTest.requested_by == doctor_id)
    )
    lab_test = result.scalars().all()
    return lab_test if lab_test else []

@router.get("/{test_id}", response_model=LabTestResponse)
@cache(expire=120)  # Cache for 2 minutes
async def get_lab_test(
    test_id: int, 
    db: AsyncSession = Depends(get_async_db), 
    user: User = Depends(lab_staff_only)
):
    """Get lab test with caching."""
    result = await db.execute(
        select(LabTest)
        .where(LabTest.id == test_id)
    )
    lab_test = result.scalars().first()
    if not lab_test:
        raise HTTPException(status_code=404, detail="Lab test not found")
    return lab_test

@router.put("/{test_id}/in-progress", response_model=LabTestResponse)
async def update_lab_test(
    test_id: int, 
    update_data: LabTestUpdate, 
    db: AsyncSession = Depends(get_async_db), 
    user: User = Depends(lab_staff_only)
):
    """Update lab test status with async operations."""
    async with db.begin():
        result = await db.execute(
            select(LabTest)
            .where(LabTest.id == test_id)
        )
        lab_test = result.scalars().first()
        if not lab_test:
            raise HTTPException(status_code=404, detail="Lab test not found")

        if update_data.status == LabTestStatus.IN_PROGRESS:
            lab_test.status = LabTestStatus.IN_PROGRESS
            if update_data.results:
                lab_test.results = update_data.results
            else:
                raise HTTPException(
                    status_code=400, 
                    detail="Results is expected"
                )
        else:
            raise HTTPException(
                status_code=400, 
                detail="Invalid status value. Expected 'In Progress'"
            )
                
        await db.commit()
        await db.refresh(lab_test)
        return lab_test

@router.put("/{test_id}/update", response_model=LabTestResponse)
async def update_lab_test(
    test_id: int, 
    update_data: LabTestUpdate, 
    db: AsyncSession = Depends(get_async_db), 
    user: User = Depends(lab_staff_only)
):
    """Update lab test with async operations."""
    async with db.begin():
        result = await db.execute(
            select(LabTest)
            .where(LabTest.id == test_id)
        )
        lab_test = result.scalars().first()
        if not lab_test:
            raise HTTPException(status_code=404, detail="Lab test not found")

        lab_test.status = update_data.status
        if update_data.status == LabTestStatus.COMPLETED and update_data.results:
            lab_test.results = update_data.results
            lab_test.additional_notes = update_data.additional_notes
            lab_test.completed_date = func.now()
        else:
            raise HTTPException(
                status_code=400, 
                detail="Results Missing!!! please Enter Results"
            )
        
        await db.commit()
        await db.refresh(lab_test)
        return lab_test

@router.delete("/{test_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lab_test(
    test_id: int, 
    db: AsyncSession = Depends(get_async_db), 
    user: User = Depends(lab_staff_only)
):
    """Delete lab test with async operations."""
    async with db.begin():
        result = await db.execute(
            select(LabTest)
            .where(LabTest.id == test_id)
        )
        lab_test = result.scalars().first()
        if not lab_test:
            raise HTTPException(status_code=404, detail="Lab test not found")

        await db.delete(lab_test)
        await db.commit()