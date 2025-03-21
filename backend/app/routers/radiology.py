from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import List
from datetime import datetime
from models.radiology import RadiologyScan
from models.patient import Patient
from models.doctor import Doctor
from models.user import User
from schemas.radiology import RadiologyScanCreate, RadiologyScanResponse, RadiologyScanUpdate, RadiologyScanStatus
from core.database import get_db
from core.dependencies import RoleChecker

router = APIRouter(prefix="/radiology", tags=["Radiology"])

doctor_only = RoleChecker(["doctor"])
staff_only = RoleChecker(["radiologist"])

# Create a new radiology test request
@router.post("/", response_model=RadiologyScanResponse)
def create_radiology_scan(radiology_scan: RadiologyScanCreate, db: Session = Depends(get_db),
                          user: User = Depends(doctor_only)):
    patient = db.query(Patient).filter(Patient.id == radiology_scan.patient_id).first()
    doctor = db.query(Doctor).filter(Doctor.id == radiology_scan.requested_by).first()

    if not patient or not doctor:
        raise HTTPException(status_code=400, detail="Invalid patient ID or doctor ID")

    new_radiology_scan = RadiologyScan(
        patient_id=radiology_scan.patient_id,
        requested_by=user.id,  # Doctor making the request
        scan_type=radiology_scan.scan_type,
        additional_notes=radiology_scan.additional_notes
    )
    db.add(new_radiology_scan)
    db.commit()
    db.refresh(new_radiology_scan)
    return new_radiology_scan

# Get all radiology scans
@router.get("/", response_model=List[RadiologyScanResponse])
def get_radiology_scans(db: Session = Depends(get_db)):
    return db.query(RadiologyScan).all()

# Get all radiology scans requested by a doctor
@router.get("/scan/{doctor_id}", response_model=List[RadiologyScanResponse])
def get_all_radiology_scans(doctor_id: int, db: Session = Depends(get_db), user: User = Depends(doctor_only)):
    radiology_scan = db.query(RadiologyScan).filter(RadiologyScan.requested_by == doctor_id).all()
    if not radiology_scan:
        return []
    
    return radiology_scan

# Get a single radiology scan by ID
@router.get("/{scan_id}", response_model=RadiologyScanResponse)
def get_radiology_scan(scan_id: int, db: Session = Depends(get_db), user: User = Depends(staff_only)):
    radiology_scan = db.query(RadiologyScan).filter(RadiologyScan.id == scan_id).first()
    if not radiology_scan:
        raise HTTPException(status_code=404, detail="Radiology scan not found")
    return radiology_scan

# Update radiology scan status to in progress when received
@router.put("/{scan_id}/in-progress", response_model=RadiologyScanResponse)
def update_radiology_scan_status(scan_id: int, update: RadiologyScanUpdate, db: Session = Depends(get_db), user: User = Depends(staff_only)):
    """
    Update radiology scan status to "In Progress"
    """
    radiology_scan = db.query(RadiologyScan).filter(RadiologyScan.id == scan_id).first()
    if not radiology_scan:
        raise HTTPException(status_code=404, detail="Radiology scan not found")

    # Ensure the status is a valid enum value
    if update.status != RadiologyScanStatus.IN_PROGRESS:
        raise HTTPException(status_code=400, detail="Invalid status value. Expected 'In Progress'")

    radiology_scan.status = update.status
    if update.results:
        radiology_scan.results = update.results
        
    db.commit()
    db.refresh(radiology_scan)

    return radiology_scan

# Update radiology scan status and report
@router.put("/{scan_id}/update", response_model=RadiologyScanResponse)
def update_radiology_scan(scan_id: int, update: RadiologyScanUpdate, db: Session = Depends(get_db), user: User = Depends(staff_only)):
    radiology_scan = db.query(RadiologyScan).filter(RadiologyScan.id == scan_id).first()
    if not radiology_scan:
        raise HTTPException(status_code=404, detail="Radiology scan not found")

    # Ensure the status is a valid enum value
    if update.status not in RadiologyScanStatus:
        raise HTTPException(status_code=400, detail="Invalid status value")

    radiology_scan.status = update.status
    if update.status == RadiologyScanStatus.COMPLETED and update.results:
        radiology_scan.results = update.results
        radiology_scan.completed_date = func.now()
    
    db.commit()
    db.refresh(radiology_scan)
    return radiology_scan

# Delete a radiology scan
@router.delete("/{scan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_radiology_scan(scan_id: int, db: Session = Depends(get_db)):
    radiology_scan = db.query(RadiologyScan).filter(RadiologyScan.id == scan_id).first()
    if not radiology_scan:
        raise HTTPException(status_code=404, detail="Radiology scan not found")

    db.delete(radiology_scan)
    db.commit()
    return