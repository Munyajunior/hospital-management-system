from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from models.admission import Ward
from schemas.admission import WardCreate, WardResponse
from core.database import get_async_db
from core.cache import cache

router = APIRouter(prefix="/wards", tags=["Wards"])

@router.post("/", response_model=WardResponse)
async def create_ward(
    ward_data: WardCreate, 
    db: AsyncSession = Depends(get_async_db)
):
    """Create ward with async operations."""
    async with db.begin():
        result = await db.execute(
            select(Ward)
            .where(Ward.name == ward_data.name)
        )
        existing_ward = result.scalars().first()
        if existing_ward:
            raise HTTPException(
                status_code=400, 
                detail="Ward with this name already exists"
            )

        new_ward = Ward(**ward_data.model_dump())
        db.add(new_ward)
        await db.commit()
        await db.refresh(new_ward)
        return new_ward

@router.get("/", response_model=List[WardResponse])
@cache(expire=3600)  # Cache for 1 hour
async def list_wards(
    department_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_async_db)
):
    """List wards with filtering and caching."""
    query = select(Ward)

    if department_id:
        query = query.where(Ward.department_id == department_id)

    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{ward_id}", response_model=WardResponse)
@cache(expire=3600)  # Cache for 1 hour
async def get_ward(
    ward_id: int, 
    db: AsyncSession = Depends(get_async_db)
):
    """Get ward with caching."""
    result = await db.execute(
        select(Ward)
        .where(Ward.id == ward_id)
    )
    ward = result.scalars().first()
    if not ward:
        raise HTTPException(status_code=404, detail="Ward not found")
    return ward

@router.put("/{ward_id}", response_model=WardResponse)
async def update_ward(
    ward_id: int, 
    ward_data: WardCreate, 
    db: AsyncSession = Depends(get_async_db)
):
    """Update ward with async operations."""
    async with db.begin():
        result = await db.execute(
            select(Ward)
            .where(Ward.id == ward_id)
        )
        ward = result.scalars().first()
        if not ward:
            raise HTTPException(status_code=404, detail="Ward not found")

        for key, value in ward_data.model_dump().items():
            setattr(ward, key, value)

        await db.commit()
        await db.refresh(ward)
        return ward

@router.delete("/{ward_id}")
async def delete_ward(
    ward_id: int, 
    db: AsyncSession = Depends(get_async_db)
):
    """Delete ward with async operations."""
    async with db.begin():
        result = await db.execute(
            select(Ward)
            .where(Ward.id == ward_id)
        )
        ward = result.scalars().first()
        if not ward:
            raise HTTPException(status_code=404, detail="Ward not found")

        await db.delete(ward)
        await db.commit()
        return {"message": "Ward deleted successfully"}