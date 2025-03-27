from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from models.admission import Bed
from schemas.admission import BedCreate, BedResponse
from core.database import get_async_db
from core.cache import cache

router = APIRouter(prefix="/beds", tags=["Beds"])

@router.post("/", response_model=BedResponse)
async def create_bed(
    bed_data: BedCreate, 
    db: AsyncSession = Depends(get_async_db)
):
    """Create bed with async operations."""
    async with db.begin():
        result = await db.execute(
            select(Bed)
            .where(Bed.bed_number == bed_data.bed_number)
        )
        existing_bed = result.scalars().first()
        if existing_bed:
            raise HTTPException(
                status_code=400, 
                detail="Bed with this number already exists"
            )

        new_bed = Bed(**bed_data.model_dump())
        db.add(new_bed)
        await db.commit()
        await db.refresh(new_bed)
        return new_bed

@router.get("/", response_model=List[BedResponse])
@cache(expire=120)  # Cache for 2 minutes
async def list_beds(
    ward_id: Optional[int] = Query(None), 
    is_occupied: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_async_db)
):
    """List beds with filtering and caching."""
    query = select(Bed)

    if ward_id:
        query = query.where(Bed.ward_id == ward_id)
    if is_occupied is not None:
        query = query.where(Bed.is_occupied == is_occupied)

    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{bed_id}", response_model=BedResponse)
@cache(expire=120)  # Cache for 2 minutes
async def get_bed(
    bed_id: int, 
    db: AsyncSession = Depends(get_async_db)
):
    """Get single bed with caching."""
    result = await db.execute(
        select(Bed)
        .where(Bed.id == bed_id)
    )
    bed = result.scalars().first()
    if not bed:
        raise HTTPException(status_code=404, detail="Bed not found")
    return bed

@router.put("/{bed_id}", response_model=BedResponse)
async def update_bed(
    bed_id: int, 
    bed_data: BedCreate, 
    db: AsyncSession = Depends(get_async_db)
):
    """Update bed with async operations."""
    async with db.begin():
        result = await db.execute(
            select(Bed)
            .where(Bed.id == bed_id)
        )
        bed = result.scalars().first()
        if not bed:
            raise HTTPException(status_code=404, detail="Bed not found")

        for key, value in bed_data.model_dump().items():
            setattr(bed, key, value)

        await db.commit()
        await db.refresh(bed)
        return bed

@router.delete("/{bed_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bed(
    bed_id: int, 
    db: AsyncSession = Depends(get_async_db)
):
    """Delete bed with async operations."""
    async with db.begin():
        result = await db.execute(
            select(Bed)
            .where(Bed.id == bed_id)
        )
        bed = result.scalars().first()
        if not bed:
            raise HTTPException(status_code=404, detail="Bed not found")

        await db.delete(bed)
        await db.commit()
        return {"message": "Bed deleted successfully"}