from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from models.medical_records import MedicalRecord
from models.patient import Patient
from models.user import User
from schemas.medical_record import MedicalRecordCreate, MedicalRecordUpdate, MedicalRecordResponse
from core.database import get_db
from core.dependencies import RoleChecker

router = APIRouter(prefix="/medical_records", tags=["Medical Records"])

authorized_users = RoleChecker(["admin", "doctor", "nurse"])
doctor_only = RoleChecker(["doctor"])
staff_access = RoleChecker(["admin", "nurse", "doctor"])

@router.post("/{patient_id}", response_model=MedicalRecordResponse)
def create_medical_record(patient_id: int, record_data: MedicalRecordCreate, db: Session = Depends(get_db), user: User = Depends(doctor_only)):
    """Create a medical record for a patient. Only doctors can do this."""
    
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    if db.query(MedicalRecord).filter(MedicalRecord.patient_id == patient_id).first():
        raise HTTPException(status_code=400, detail="Medical record already exists")
    
    new_record = MedicalRecord(**record_data.model_dump(), patient_id=patient_id, created_by=user.id)
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record

@router.get("/", response_model=List[MedicalRecordResponse])
def get_medical_record(patient_id: Optional[int] = Query(None), db: Session = Depends(get_db), user: User = Depends(staff_access)):
    """Get a patient's medical record. Accessible by doctors, nurses, and admins."""
    query = (db.query(MedicalRecord.id,MedicalRecord.patient_id,
                      Patient.full_name.label("patient_name"),
                      MedicalRecord.created_by,
                      User.full_name.label("created_by_name"),
                      MedicalRecord.visit_date,
                      MedicalRecord.diagnosis,
                      MedicalRecord.treatment_plan,
                      MedicalRecord.medical_history,
                      MedicalRecord.prescription,
                      MedicalRecord.lab_tests_requested,
                      MedicalRecord.scans_requested,
                      MedicalRecord.lab_tests_results,
                      MedicalRecord.scan_results,
                      MedicalRecord.notes,
                      MedicalRecord.created_at,
                      MedicalRecord.updated_at
                      ).join(Patient, MedicalRecord.patient_id == Patient.id)
                       .join(User, MedicalRecord.created_by == User.id)
             )
    if patient_id:
        query = query.filter(MedicalRecord.patient_id == patient_id)
    
    record = query.all()
    return record

@router.put("/{patient_id}", response_model=MedicalRecordResponse)
def update_medical_record(patient_id: int, updates: MedicalRecordUpdate, db: Session = Depends(get_db), user: User = Depends(doctor_only)):
    """Update a patient's medical record. Only doctors can update records."""
    
    record = db.query(MedicalRecord).filter(MedicalRecord.patient_id == patient_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Medical record not found")

    update_data = updates.model_dump(exclude_unset=True)
    append_flags = update_data.pop('append', {})  # Extract append flags

    for key, value in update_data.items():
        if value is not None:
            if append_flags.get(key, False) and getattr(record, key):
                # Append new data to existing data
                setattr(record, key, getattr(record, key) + "\n" + value)
            else:
                # Overwrite existing data
                setattr(record, key, value)

    db.commit()
    db.refresh(record)
    return record







