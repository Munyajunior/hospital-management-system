from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.models.pharmacy import Prescription
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.schemas.pharmacy import PrescriptionCreate, PrescriptionResponse
from app.core.database import get_db

router = APIRouter(prefix="/pharmacy", tags=["Pharmacy"])

# Create a new prescription
@router.post("/", response_model=PrescriptionResponse)
def create_prescription(prescription: PrescriptionCreate, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == prescription.patient_id).first()
    doctor = db.query(Doctor).filter(Doctor.id == prescription.doctor_id).first()

    if not patient or not doctor:
        raise HTTPException(status_code=400, detail="Invalid patient ID or doctor ID")

    new_prescription = Prescription(**prescription.model_dump())
    db.add(new_prescription)
    db.commit()
    db.refresh(new_prescription)
    return new_prescription

# Get all prescriptions
@router.get("/", response_model=List[PrescriptionResponse])
def get_prescriptions(db: Session = Depends(get_db)):
    return db.query(Prescription).all()

# Get a single prescription by ID
@router.get("/{prescription_id}", response_model=PrescriptionResponse)
def get_prescription(prescription_id: int, db: Session = Depends(get_db)):
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return prescription

# Mark prescription as dispensed
@router.put("/{prescription_id}/dispense", response_model=PrescriptionResponse)
def dispense_prescription(prescription_id: int, db: Session = Depends(get_db)):
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    
    prescription.is_dispensed = True
    db.commit()
    db.refresh(prescription)
    return prescription

# Delete a prescription
@router.delete("/{prescription_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prescription(prescription_id: int, db: Session = Depends(get_db)):
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")

    db.delete(prescription)
    db.commit()
    return

# Request a prescription refill
@router.post("/{prescription_id}/refill", response_model=PrescriptionResponse)
def request_prescription_refill(prescription_id: int, db: Session = Depends(get_db)):
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    
    if not prescription.is_dispensed:
        raise HTTPException(status_code=400, detail="Original prescription has not been dispensed yet")

    # Create a duplicate prescription for refill
    new_prescription = Prescription(
        patient_id=prescription.patient_id,
        doctor_id=prescription.doctor_id,
        medication_name=prescription.medication_name,
        dosage=prescription.dosage,
        instructions=prescription.instructions,
    )

    db.add(new_prescription)
    db.commit()
    db.refresh(new_prescription)
    return new_prescription
