from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.models.nurse import Nurse
from app.models.user import User
from app.schemas.nurse import NurseCreate, NurseResponse
from app.core.database import get_db
from app.core.dependencies import RoleChecker

router = APIRouter(prefix="/nurses", tags=["Nurse Management"])

admin_only = RoleChecker("admin")
@router.post("/", response_model=NurseResponse, status_code=status.HTTP_201_CREATED)
def create_nurse(nurse_data: NurseCreate, db: Session = Depends(get_db)
                 , user: User = Depends(admin_only)):
    existing_nurse = db.query(Nurse).filter(Nurse.email == nurse_data.email).first()
    if existing_nurse:
        raise HTTPException(status_code=400, detail="Nurse with this email already exists")

    new_nurse = Nurse(**nurse_data.model_dump())
    db.add(new_nurse)
    db.commit()
    db.refresh(new_nurse)
    return new_nurse

@router.get("/", response_model=List[NurseResponse])
def get_nurses(db: Session = Depends(get_db), user: User = Depends(admin_only)):
    return db.query(Nurse).all()

@router.get("/{nurse_id}", response_model=NurseResponse)
def get_nurse(nurse_id: int, db: Session = Depends(get_db), user: User = Depends(admin_only)):
    nurse = db.query(Nurse).filter(Nurse.id == nurse_id).first()
    if not nurse:
        raise HTTPException(status_code=404, detail="Nurse not found")
    return nurse

@router.put("/{nurse_id}", response_model=NurseResponse)
def update_nurse(nurse_id: int, updated_nurse: NurseCreate, db: Session = Depends(get_db)
                 , user: User = Depends(admin_only)):
    nurse = db.query(Nurse).filter(Nurse.id == nurse_id).first()
    if not nurse:
        raise HTTPException(status_code=404, detail="Nurse not found")

    for key, value in updated_nurse.model_dump().items():
        setattr(nurse, key, value)

    db.commit()
    db.refresh(nurse)
    return nurse

@router.delete("/{nurse_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_nurse(nurse_id: int, db: Session = Depends(get_db)
                 , user: User = Depends(admin_only)):
    nurse = db.query(Nurse).filter(Nurse.id == nurse_id).first()
    if not nurse:
        raise HTTPException(status_code=404, detail="Nurse not found")

    db.delete(nurse)
    db.commit()
    return