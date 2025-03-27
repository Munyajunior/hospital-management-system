from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from models.admission import Department
from schemas.admission import DepartmentCreate, DepartmentResponse
from models.user import User
from core.dependencies import RoleChecker 
from core.database import get_async_db
from core.cache import cache

router = APIRouter(prefix="/departments", tags=["Departments"])

doctor_or_nurse = RoleChecker(["doctor", "nurse", "admin"])

@router.post("/", response_model=DepartmentResponse)
async def create_department(
    department_data: DepartmentCreate, 
    db: AsyncSession = Depends(get_async_db), 
    user: User = Depends(doctor_or_nurse)
):
    """Create department with async operations."""
    async with db.begin():
        result = await db.execute(
            select(Department)
            .where(Department.name == department_data.name)
        )
        existing_department = result.scalars().first()
        if existing_department:
            raise HTTPException(
                status_code=400, 
                detail="Department with this name already exists"
            )

        new_department = Department(**department_data.model_dump())
        db.add(new_department)
        await db.commit()
        await db.refresh(new_department)
        return new_department

@router.get("/", response_model=List[DepartmentResponse])
@cache(expire=3600)  # Cache for 1 hour
async def list_departments(
    db: AsyncSession = Depends(get_async_db), 
    user: User = Depends(doctor_or_nurse)
):
    """List departments with caching."""
    result = await db.execute(select(Department))
    return result.scalars().all()

@router.get("/{department_id}", response_model=DepartmentResponse)
@cache(expire=3600)  # Cache for 1 hour
async def get_department(
    department_id: int, 
    db: AsyncSession = Depends(get_async_db), 
    user: User = Depends(doctor_or_nurse)
):
    """Get department with caching."""
    result = await db.execute(
        select(Department)
        .where(Department.id == department_id)
    )
    department = result.scalars().first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    return department

@router.put("/{department_id}", response_model=DepartmentResponse)
async def update_department(
    department_id: int, 
    department_data: DepartmentCreate, 
    db: AsyncSession = Depends(get_async_db), 
    user: User = Depends(doctor_or_nurse)
):
    """Update department with async operations."""
    async with db.begin():
        result = await db.execute(
            select(Department)
            .where(Department.id == department_id)
        )
        department = result.scalars().first()
        if not department:
            raise HTTPException(status_code=404, detail="Department not found")

        for key, value in department_data.model_dump().items():
            setattr(department, key, value)

        await db.commit()
        await db.refresh(department)
        return department

@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(
    department_id: int, 
    db: AsyncSession = Depends(get_async_db), 
    user: User = Depends(doctor_or_nurse)
):
    """Delete department with async operations."""
    async with db.begin():
        result = await db.execute(
            select(Department)
            .where(Department.id == department_id)
        )
        department = result.scalars().first()
        if not department:
            raise HTTPException(status_code=404, detail="Department not found")

        await db.delete(department)
        await db.commit()