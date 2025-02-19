from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.models.lab import LabTest, LabTestStatus
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.schemas.lab import LabTestCreate, LabTestResponse
from app.core.database import get_db
from app.models.user import User
from app.core.dependencies import RoleChecker

router = APIRouter(prefix="/lab", tags=["Lab"])

staff_only = RoleChecker(["lab"])

@router.post("/", response_model=LabTestResponse)
def create_lab_test(lab_test: LabTestCreate, db: Session = Depends(get_db), user: User = Depends(staff_only)):
    patient = db.query(Patient).filter(Patient.id == lab_test.patient_id).first()
    doctor = db.query(Doctor).filter(Doctor.id == lab_test.doctor_id).first()

    if not patient or not doctor:
        raise HTTPException(status_code=400, detail="Invalid patient ID or doctor ID")

    new_lab_test = LabTest(**lab_test.model_dump())
    db.add(new_lab_test)
    db.commit()
    db.refresh(new_lab_test)
    return new_lab_test

@router.get("/", response_model=List[LabTestResponse])
def get_lab_tests(db: Session = Depends(get_db), user: User = Depends(staff_only)):
    return db.query(LabTest).all()

@router.get("/{test_id}", response_model=LabTestResponse)
def get_lab_test(test_id: int, db: Session = Depends(get_db), user: User = Depends(staff_only)):
    lab_test = db.query(LabTest).filter(LabTest.id == test_id).first()
    if not lab_test:
        raise HTTPException(status_code=404, detail="Lab test not found")
    return lab_test

@router.put("/{test_id}/update", response_model=LabTestResponse)
def update_lab_test(test_id: int, status: LabTestStatus, result: str, db: Session = Depends(get_db), 
                    user: User = Depends(staff_only)):
    lab_test = db.query(LabTest).filter(LabTest.id == test_id).first()
    if not lab_test:
        raise HTTPException(status_code=404, detail="Lab test not found")

    lab_test.status = status
    if status == LabTestStatus.COMPLETED:
        lab_test.result = result
        lab_test.completed_date = datetime.now()

    db.commit()
    db.refresh(lab_test)
    return lab_test

@router.delete("/{test_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lab_test(test_id: int, db: Session = Depends(get_db), user: User = Depends(staff_only)):
    lab_test = db.query(LabTest).filter(LabTest.id == test_id).first()
    if not lab_test:
        raise HTTPException(status_code=404, detail="Lab test not found")

    db.delete(lab_test)
    db.commit()
    return