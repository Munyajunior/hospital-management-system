from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.models.radiology import RadiologyTest, RadiologyTestStatus
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.schemas.radiology import RadiologyTestCreate, RadiologyTestResponse
from app.core.database import get_db

router = APIRouter(prefix="/radiology", tags=["Radiology"])

# Create a new radiology test request
@router.post("/", response_model=RadiologyTestResponse)
def create_radiology_test(radiology_test: RadiologyTestCreate, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == radiology_test.patient_id).first()
    doctor = db.query(Doctor).filter(Doctor.id == radiology_test.doctor_id).first()

    if not patient or not doctor:
        raise HTTPException(status_code=400, detail="Invalid patient ID or doctor ID")

    new_radiology_test = RadiologyTest(**radiology_test.dict())
    db.add(new_radiology_test)
    db.commit()
    db.refresh(new_radiology_test)
    return new_radiology_test

# Get all radiology tests
@router.get("/", response_model=List[RadiologyTestResponse])
def get_radiology_tests(db: Session = Depends(get_db)):
    return db.query(RadiologyTest).all()

# Get a single radiology test by ID
@router.get("/{test_id}", response_model=RadiologyTestResponse)
def get_radiology_test(test_id: int, db: Session = Depends(get_db)):
    radiology_test = db.query(RadiologyTest).filter(RadiologyTest.id == test_id).first()
    if not radiology_test:
        raise HTTPException(status_code=404, detail="Radiology test not found")
    return radiology_test

# Update radiology test status and report
@router.put("/{test_id}/update", response_model=RadiologyTestResponse)
def update_radiology_test(test_id: int, status: RadiologyTestStatus, report: str, db: Session = Depends(get_db)):
    radiology_test = db.query(RadiologyTest).filter(RadiologyTest.id == test_id).first()
    if not radiology_test:
        raise HTTPException(status_code=404, detail="Radiology test not found")

    radiology_test.status = status
    if status == RadiologyTestStatus.COMPLETED:
        radiology_test.report = report
        radiology_test.completed_date = datetime.utcnow()

    db.commit()
    db.refresh(radiology_test)
    return radiology_test

# Delete a radiology test
@router.delete("/{test_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_radiology_test(test_id: int, db: Session = Depends(get_db)):
    radiology_test = db.query(RadiologyTest).filter(RadiologyTest.id == test_id).first()
    if not radiology_test:
        raise HTTPException(status_code=404, detail="Radiology test not found")

    db.delete(radiology_test)
    db.commit()
    return
