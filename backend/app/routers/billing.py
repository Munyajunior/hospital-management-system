from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.billing import Billing, BillingStatus
from models.patient import Patient
from models.user import User
from schemas.billing import BillingCreate, BillingResponse
from core.database import get_async_db
from core.dependencies import RoleChecker
from core.cache import cache
from typing import List


router = APIRouter(prefix="/billing", tags=["Billing"])

billing_staff_only = RoleChecker(["admin", "billing"])

@router.post("/", response_model=BillingResponse)
async def create_billing(
    billing: BillingCreate, 
    db: AsyncSession = Depends(get_async_db), 
    user: User = Depends(billing_staff_only)
):
    """Create billing record with async operations."""
    async with db.begin():
        result = await db.execute(
            select(Patient)
            .where(Patient.id == billing.patient_id)
        )
        patient = result.scalars().first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        new_billing = Billing(**billing.model_dump())
        db.add(new_billing)
        await db.commit()
        await db.refresh(new_billing)
        return new_billing

@router.get("/", response_model=List[BillingResponse])
@cache(expire=120)  # Cache for 2 minutes
async def list_billing(
    db: AsyncSession = Depends(get_async_db), 
    user: User = Depends(billing_staff_only)
):
    """List billing records with caching."""
    result = await db.execute(select(Billing))
    return result.scalars().all()

@router.put("/{billing_id}/status", response_model=BillingResponse)
async def update_billing_status(
    billing_id: int, 
    status: BillingStatus, 
    db: AsyncSession = Depends(get_async_db), 
    user: User = Depends(billing_staff_only)
):
    """Update billing status with async operations."""
    async with db.begin():
        result = await db.execute(
            select(Billing)
            .where(Billing.id == billing_id)
        )
        billing = result.scalars().first()
        if not billing:
            raise HTTPException(status_code=404, detail="Billing record not found")

        billing.status = status
        await db.commit()
        await db.refresh(billing)
        return billing

@router.delete("/{billing_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_billing(
    billing_id: int, 
    db: AsyncSession = Depends(get_async_db), 
    user: User = Depends(billing_staff_only)
):
    """Delete billing record with async operations."""
    async with db.begin():
        result = await db.execute(
            select(Billing)
            .where(Billing.id == billing_id)
        )
        billing = result.scalars().first()
        if not billing:
            raise HTTPException(status_code=404, detail="Billing record not found")

        await db.delete(billing)
        await db.commit()