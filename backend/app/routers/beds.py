from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from models.admission import Bed
from schemas.admission import BedCreate, BedResponse
from core.database import get_db
from typing import List, Optional

router = APIRouter(prefix="/beds", tags=["Beds"])

@router.post("/", response_model=BedResponse)
def create_bed(bed_data: BedCreate, db: Session = Depends(get_db)):
    """Create a new bed."""
    existing_bed = db.query(Bed).filter(Bed.bed_number == bed_data.bed_number).first()
    if existing_bed:
        raise HTTPException(status_code=400, detail="Bed with this number already exists")

    new_bed = Bed(**bed_data.model_dump())
    db.add(new_bed)
    db.commit()
    db.refresh(new_bed)
    return new_bed


@router.get("/", response_model=List[BedResponse])
def list_beds(db: Session = Depends(get_db)):
    """Retrieve a list of all beds."""
    beds = db.query(Bed).all()
    return beds


@router.get("/{bed_id}", response_model=BedResponse)
def get_bed(bed_id: int, db: Session = Depends(get_db)):
    """Retrieve a single bed by ID."""
    bed = db.query(Bed).filter(Bed.id == bed_id).first()
    if not bed:
        raise HTTPException(status_code=404, detail="Bed not found")
    return bed

@router.get("/", response_model=List[BedResponse])
def list_beds(
    ward_id: Optional[int] = Query(None, description="Filter beds by ward ID"),
    is_occupied: Optional[bool] = Query(None, description="Filter beds by occupancy status"),
    db: Session = Depends(get_db)
):
    """Retrieve a list of beds, optionally filtered by ward ID and occupancy status."""
    query = db.query(Bed)

    if ward_id:
        query = query.filter(Bed.ward_id == ward_id)

    if is_occupied is not None:
        query = query.filter(Bed.is_occupied == is_occupied)

    beds = query.all()
    return beds

@router.put("/{bed_id}", response_model=BedResponse)
def update_bed(bed_id: int, bed_data: BedCreate, db: Session = Depends(get_db)):
    """Update a bed's details."""
    bed = db.query(Bed).filter(Bed.id == bed_id).first()
    if not bed:
        raise HTTPException(status_code=404, detail="Bed not found")

    for key, value in bed_data.model_dump().items():
        setattr(bed, key, value)

    db.commit()
    db.refresh(bed)
    return bed


@router.delete("/{bed_id}")
def delete_bed(bed_id: int, db: Session = Depends(get_db)):
    """Delete a bed."""
    bed = db.query(Bed).filter(Bed.id == bed_id).first()
    if not bed:
        raise HTTPException(status_code=404, detail="Bed not found")

    db.delete(bed)
    db.commit()
    return {"message": "Bed deleted successfully"}