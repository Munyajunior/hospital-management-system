from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.session import get_db
from models.lab import LabTest
from schemas.lab import LabTestCreate, LabTestResponse

router = APIRouter()

@router.post("/", response_model=LabTestResponse)
def request_lab_test(lab_test: LabTestCreate, db: Session = Depends(get_db)):
    new_test = LabTest(**lab_test.dict())
    db.add(new_test)
    db.commit()
    db.refresh(new_test)
    return new_test

@router.get("/", response_model=list[LabTestResponse])
def get_lab_tests(db: Session = Depends(get_db)):
    return db.query(LabTest).all()
