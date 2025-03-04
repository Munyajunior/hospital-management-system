from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from models.medical_record import MedicalRecord
from models.patient import Patient
from schemas.medical_record import MedicalRecordCreate, MedicalRecordResponse
from core.database import get_db
from core.dependencies import RoleChecker

router = APIRouter(prefix="/medical_records", tags=["Medical Records"])

authorized_users = RoleChecker(["admin", "doctor", "nurse"])

@router.post("/", response_model=MedicalRecordResponse)
def create_medical_record(patient_id: int, db: Session = Depends(get_db)):
    if db.query(MedicalRecord).filter(MedicalRecord.patient_id == patient_id).first():
        raise HTTPException(status_code=400, detail="Medical record already exists.")

    new_record = MedicalRecord(patient_id=patient_id)
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record

@router.get("/{patient_id}", response_model=MedicalRecordResponse)
def get_medical_record(patient_id: int, db: Session = Depends(get_db), user=Depends(authorized_users)):
    record = db.query(MedicalRecord).filter(MedicalRecord.patient_id == patient_id).first()
    return record

@router.put("/{patient_id}", response_model=MedicalRecordResponse)
def update_medical_record(patient_id: int, record_data: MedicalRecordCreate, db: Session = Depends(get_db), user=Depends(authorized_users)):
    record = db.query(MedicalRecord).filter(MedicalRecord.patient_id == patient_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Medical record not found.")

    for key, value in record_data.model_dump().items():
        setattr(record, key, value)

    db.commit()
    db.refresh(record)
    return record
