from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from models.admission import Ward
from schemas.admission import WardCreate, WardResponse
from core.database import get_db
from typing import List, Optional

router = APIRouter(prefix="/wards", tags=["Wards"])

@router.post("/", response_model=WardResponse)
def create_ward(ward_data: WardCreate, db: Session = Depends(get_db)):
    """Create a new ward."""
    existing_ward = db.query(Ward).filter(Ward.name == ward_data.name).first()
    if existing_ward:
        raise HTTPException(status_code=400, detail="Ward with this name already exists")

    new_ward = Ward(**ward_data.model_dump())
    db.add(new_ward)
    db.commit()
    db.refresh(new_ward)
    return new_ward


@router.get("/", response_model=List[WardResponse])
def list_wards(
    department_id: Optional[int] = Query(None, description="Filter wards by department ID"),
    db: Session = Depends(get_db)
):
    """Retrieve a list of wards, optionally filtered by department ID."""
    query = db.query(Ward)

    if department_id:
        query = query.filter(Ward.department_id == department_id)

    wards = query.all()
    return wards

@router.get("/", response_model=List[WardResponse])
def list_wards(db: Session = Depends(get_db)):
    """Retrieve a list of all wards."""
    wards = db.query(Ward).all()
    return wards


@router.get("/{ward_id}", response_model=WardResponse)
def get_ward(ward_id: int, db: Session = Depends(get_db)):
    """Retrieve a single ward by ID."""
    ward = db.query(Ward).filter(Ward.id == ward_id).first()
    if not ward:
        raise HTTPException(status_code=404, detail="Ward not found")
    return ward


@router.put("/{ward_id}", response_model=WardResponse)
def update_ward(ward_id: int, ward_data: WardCreate, db: Session = Depends(get_db)):
    """Update a ward's details."""
    ward = db.query(Ward).filter(Ward.id == ward_id).first()
    if not ward:
        raise HTTPException(status_code=404, detail="Ward not found")

    for key, value in ward_data.model_dump().items():
        setattr(ward, key, value)

    db.commit()
    db.refresh(ward)
    return ward


@router.delete("/{ward_id}")
def delete_ward(ward_id: int, db: Session = Depends(get_db)):
    """Delete a ward."""
    ward = db.query(Ward).filter(Ward.id == ward_id).first()
    if not ward:
        raise HTTPException(status_code=404, detail="Ward not found")

    db.delete(ward)
    db.commit()
    return {"message": "Ward deleted successfully"}