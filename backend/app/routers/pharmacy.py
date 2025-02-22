from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from models.pharmacy import Prescription
from models.patient import Patient
from models.user import User
from models.doctor import Doctor
from schemas.pharmacy import PrescriptionCreate, PrescriptionResponse
from core.database import get_db
from core.dependencies import RoleChecker

router = APIRouter(prefix="/pharmacy", tags=["Pharmacy"])

admin_only = RoleChecker(["pharmacy"])
staff_only = RoleChecker(["doctor"])

@router.post("/", response_model=PrescriptionResponse)
def create_prescription(prescription: PrescriptionCreate, db: Session = Depends(get_db)
                        , user: User = Depends(staff_only)):
    patient = db.query(Patient).filter(Patient.id == prescription.patient_id).first()
    doctor = db.query(Doctor).filter(Doctor.id == prescription.doctor_id).first()

    if not patient or not doctor:
        raise HTTPException(status_code=400, detail="Invalid patient ID or doctor ID")

    new_prescription = Prescription(**prescription.model_dump())
    db.add(new_prescription)
    db.commit()
    db.refresh(new_prescription)
    return new_prescription

@router.get("/", response_model=List[PrescriptionResponse])
def get_prescriptions(db: Session = Depends(get_db)):
    return db.query(Prescription).all()

@router.get("/{prescription_id}", response_model=PrescriptionResponse)
def get_prescription(prescription_id: int, db: Session = Depends(get_db)):
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return prescription

@router.put("/{prescription_id}/dispense", response_model=PrescriptionResponse)
def dispense_prescription(prescription_id: int, db: Session = Depends(get_db),
                          user: User = Depends(admin_only)):
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    
    prescription.is_dispensed = True
    db.commit()
    db.refresh(prescription)
    return prescription

@router.delete("/{prescription_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prescription(prescription_id: int, db: Session = Depends(get_db)):
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")

    db.delete(prescription)
    db.commit()
    return