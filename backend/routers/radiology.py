from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.session import get_db
from models.radiology import RadiologyScan
from schemas.radiology import RadiologyScanCreate, RadiologyScanResponse

router = APIRouter()

@router.post("/", response_model=RadiologyScanResponse)
def request_radiology_scan(scan: RadiologyScanCreate, db: Session = Depends(get_db)):
    new_scan = RadiologyScan(**scan.dict())
    db.add(new_scan)
    db.commit()
    db.refresh(new_scan)
    return new_scan

@router.get("/", response_model=list[RadiologyScanResponse])
def get_radiology_scans(db: Session = Depends(get_db)):
    return db.query(RadiologyScan).all()
