from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models.admission import Department
from schemas.admission import DepartmentCreate, DepartmentResponse
from models.user import User
from core.dependencies import RoleChecker 
from core.database import get_db
from typing import List

router = APIRouter(prefix="/departments", tags=["Departments"])

doctor_or_nurse = RoleChecker(["doctor", "nurse", "admin"])
@router.post("/", response_model=DepartmentResponse)
def create_department(department_data: DepartmentCreate, db: Session = Depends(get_db), user: User = Depends(doctor_or_nurse)):
    """Create a new department."""
    existing_department = db.query(Department).filter(Department.name == department_data.name).first()
    if existing_department:
        raise HTTPException(status_code=400, detail="Department with this name already exists")

    new_department = Department(**department_data.model_dump())
    db.add(new_department)
    db.commit()
    db.refresh(new_department)
    return new_department


@router.get("/", response_model=List[DepartmentResponse])
def list_departments(db: Session = Depends(get_db), user: User = Depends(doctor_or_nurse)):
    """Retrieve a list of all departments."""
    departments = db.query(Department).all()
    return departments


@router.get("/{department_id}", response_model=DepartmentResponse)
def get_department(department_id: int, db: Session = Depends(get_db), user: User = Depends(doctor_or_nurse)):
    """Retrieve a single department by ID."""
    department = db.query(Department).filter(Department.id == department_id).first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    return department


@router.put("/{department_id}", response_model=DepartmentResponse)
def update_department(department_id: int, department_data: DepartmentCreate, db: Session = Depends(get_db), user: User = Depends(doctor_or_nurse)):
    """Update a department's details."""
    department = db.query(Department).filter(Department.id == department_id).first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    for key, value in department_data.model_dump().items():
        setattr(department, key, value)

    db.commit()
    db.refresh(department)
    return department


@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_department(department_id: int, db: Session = Depends(get_db), user: User = Depends(doctor_or_nurse)):
    """Delete a department."""
    department = db.query(Department).filter(Department.id == department_id).first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    db.delete(department)
    db.commit()
    