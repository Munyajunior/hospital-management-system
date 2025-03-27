from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy.sql import func
from models.lab import LabTest, LabTestStatus
from models.patient import Patient
from schemas.lab import LabTestCreate, LabTestResponse, LabTestUpdate
from core.database import get_db
from models.user import User
from core.dependencies import RoleChecker

router = APIRouter(prefix="/lab", tags=["Lab"])

doctor_only = RoleChecker(["doctor"])
lab_staff_only = RoleChecker(["lab_technician"])


# create lab Test
@router.post("/", response_model=LabTestResponse)
def request_lab_test(
    lab_test: LabTestCreate, 
    db: Session = Depends(get_db), 
    user: User = Depends(doctor_only)
):
    patient = db.query(Patient).filter(Patient.id == lab_test.patient_id).first()
    if not patient:
        raise HTTPException(status_code=400, detail="Invalid patient ID")

    new_lab_test = LabTest(
        requested_by=user.id,  # Doctor making the request
        patient_id=lab_test.patient_id,
        test_type=lab_test.test_type,
        additional_notes=lab_test.additional_notes
    )
    db.add(new_lab_test)
    db.commit()
    db.refresh(new_lab_test)
    return new_lab_test

# Get all lab test
@router.get("/", response_model=List[LabTestResponse])
def get_lab_tests(db: Session = Depends(get_db), user: User = Depends(lab_staff_only)):
    return db.query(LabTest).all()


# Get all lab test requested by a doctor
@router.get("/test/{doctor_id}", response_model=List[LabTestResponse])
async def get_lab_test_requested(doctor_id:int, db: Session = Depends(get_db), user: User = Depends(doctor_only)):
    lab_test = db.query(LabTest).filter(LabTest.requested_by == doctor_id).all()
    if not lab_test:
        return []
    return lab_test

# Get a specific lab test by id
@router.get("/{test_id}", response_model=LabTestResponse)
def get_lab_test(test_id: int, db: Session = Depends(get_db), user: User = Depends(lab_staff_only)):
    lab_test = db.query(LabTest).filter(LabTest.id == test_id).first()
    if not lab_test:
        raise HTTPException(status_code=404, detail="Lab test not found")
    return lab_test


# update a specific lab test
@router.put("/{test_id}/in-progress", response_model=LabTestResponse)
def update_lab_test(
    test_id: int, 
    update_data: LabTestUpdate, 
    db: Session = Depends(get_db), 
    user: User = Depends(lab_staff_only)
):
    lab_test = db.query(LabTest).filter(LabTest.id == test_id).first()
    if not lab_test:
        raise HTTPException(status_code=404, detail="Lab test not found")

    
    if update_data.status == LabTestStatus.IN_PROGRESS:
        lab_test.status = LabTestStatus.IN_PROGRESS
        if update_data.results:
            lab_test.results = update_data.results
        else:
            raise HTTPException(status_code=400, detail="Results is expected")
    else:
        raise HTTPException(status_code=400, detail="Invalid status value. Expected 'In Progress'")
            
    db.commit()
    
    db.refresh(lab_test)
    return lab_test

# update a specific lab test
@router.put("/{test_id}/update", response_model=LabTestResponse)
def update_lab_test(
    test_id: int, 
    update_data: LabTestUpdate, 
    db: Session = Depends(get_db), 
    user: User = Depends(lab_staff_only)
):
    lab_test = db.query(LabTest).filter(LabTest.id == test_id).first()
    if not lab_test:
        raise HTTPException(status_code=404, detail="Lab test not found")

    lab_test.status = update_data.status
    if update_data.status == LabTestStatus.COMPLETED and update_data.results:
        lab_test.results = update_data.results
        lab_test.additional_notes = update_data.additional_notes
        lab_test.completed_date = func.now()

    db.commit()
    db.refresh(lab_test)
    return lab_test

@router.delete("/{test_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lab_test(test_id: int, db: Session = Depends(get_db), user: User = Depends(lab_staff_only)):
    lab_test = db.query(LabTest).filter(LabTest.id == test_id).first()
    if not lab_test:
        raise HTTPException(status_code=404, detail="Lab test not found")

    db.delete(lab_test)
    db.commit()
