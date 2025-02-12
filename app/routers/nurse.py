from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.models.nurse import Nurse
from app.schemas.nurse import NurseCreate, NurseResponse
from app.core.database import get_db

router = APIRouter(prefix="/nurses", tags=["Nurse Management"])

# Create a new nurse
@router.post("/", response_model=NurseResponse, status_code=status.HTTP_201_CREATED)
def create_nurse(nurse_data: NurseCreate, db: Session = Depends(get_db)):
    existing_nurse = db.query(Nurse).filter(Nurse.email == nurse_data.email).first()
    if existing_nurse:
        raise HTTPException(status_code=400, detail="Nurse with this email already exists")

    new_nurse = Nurse(**nurse_data.dict())
    db.add(new_nurse)
    db.commit()
    db.refresh(new_nurse)
    return new_nurse

# Get all nurses
@router.get("/", response_model=List[NurseResponse])
def get_nurses(db: Session = Depends(get_db)):
    return db.query(Nurse).all()

# Get a single nurse by ID
@router.get("/{nurse_id}", response_model=NurseResponse)
def get_nurse(nurse_id: int, db: Session = Depends(get_db)):
    nurse = db.query(Nurse).filter(Nurse.id == nurse_id).first()
    if not nurse:
        raise HTTPException(status_code=404, detail="Nurse not found")
    return nurse

# Update nurse details
@router.put("/{nurse_id}", response_model=NurseResponse)
def update_nurse(nurse_id: int, updated_nurse: NurseCreate, db: Session = Depends(get_db)):
    nurse = db.query(Nurse).filter(Nurse.id == nurse_id).first()
    if not nurse:
        raise HTTPException(status_code=404, detail="Nurse not found")

    for key, value in updated_nurse.dict().items():
        setattr(nurse, key, value)

    db.commit()
    db.refresh(nurse)
    return nurse

# Delete a nurse
@router.delete("/{nurse_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_nurse(nurse_id: int, db: Session = Depends(get_db)):
    nurse = db.query(Nurse).filter(Nurse.id == nurse_id).first()
    if not nurse:
        raise HTTPException(status_code=404, detail="Nurse not found")

    db.delete(nurse)
    db.commit()
    return
