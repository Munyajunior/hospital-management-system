from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List
from models.pharmacy import (
    Prescription, PrescriptionStatus, 
    Inventory, DrugCategory
)
from models.patient import Patient
from models.user import User
from models.doctor import Doctor
from schemas.pharmacy import (
    PrescriptionCreate, PrescriptionResponse
)
from schemas.inventory import (
    DrugCategoryCreate, DrugCategoryResponse, 
    InventoryCreate, InventoryResponse, 
    InventoryUpdate, InventoryQuantityUpdate
)
from core.database import get_async_db
from core.dependencies import RoleChecker
from core.cache import cache

router = APIRouter(prefix="/pharmacy", tags=["Pharmacy"])

pharmacist_only = RoleChecker(["pharmacist"])
doctor_only = RoleChecker(["doctor"])

@router.post("/prescriptions/", response_model=PrescriptionResponse)
async def create_prescription(
    prescription: PrescriptionCreate, 
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(doctor_only)
):
    """Create prescription with async operations."""
    async with db.begin():
        result = await db.execute(
            select(Patient)
            .where(Patient.id == prescription.patient_id)
        )
        patient = result.scalars().first()
        
        result = await db.execute(
            select(Doctor)
            .where(Doctor.id == prescription.prescribed_by)
        )
        doctor = result.scalars().first()
        
        result = await db.execute(
            select(Inventory)
            .where(Inventory.drug_name == prescription.drug_name)
        )
        drug = result.scalars().first()

        if not patient or not doctor:
            raise HTTPException(
                status_code=400, 
                detail="Invalid patient or doctor ID"
            )
        
        if not drug:
            raise HTTPException(
                status_code=400, 
                detail="Drug not available in inventory"
            )

        new_prescription = Prescription(**prescription.model_dump())
        db.add(new_prescription)
        await db.commit()
        await db.refresh(new_prescription)
        return new_prescription

@router.get("/prescriptions/", response_model=List[PrescriptionResponse])
@cache(expire=120)  # Cache for 2 minutes
async def get_prescriptions(db: AsyncSession = Depends(get_async_db)):
    """List prescriptions with caching."""
    result = await db.execute(select(Prescription))
    return result.scalars().all()

@router.put("/prescriptions/{prescription_id}/dispense", response_model=PrescriptionResponse)
async def dispense_prescription(
    prescription_id: int, 
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(pharmacist_only)
):
    """Dispense prescription with inventory update and async operations."""
    async with db.begin():
        result = await db.execute(
            select(Prescription)
            .where(Prescription.id == prescription_id)
        )
        prescription = result.scalars().first()
        if not prescription:
            raise HTTPException(status_code=404, detail="Prescription not found")
        
        if prescription.status == PrescriptionStatus.DISPENSED:
            raise HTTPException(
                status_code=400, 
                detail="Prescription already dispensed"
            )

        result = await db.execute(
            select(Inventory)
            .where(Inventory.drug_name == prescription.drug_name)
        )
        drug_item = result.scalars().first()
        if not drug_item:
            raise HTTPException(
                status_code=404, 
                detail=f"'{prescription.drug_name}' is not available in inventory"
            )
        
        if drug_item.quantity <= 0:
            raise HTTPException(
                status_code=400, 
                detail=f"'{prescription.drug_name}' is out of stock. Cannot dispense."
            )

        # Update inventory
        new_quantity = drug_item.quantity - 1
        drug_item.quantity = new_quantity

        # Update prescription status
        prescription.status = PrescriptionStatus.DISPENSED
        await db.commit()
        await db.refresh(prescription)
        return prescription

@router.delete("/prescriptions/{prescription_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prescription(
    prescription_id: int, 
    db: AsyncSession = Depends(get_async_db)
):
    """Delete prescription with async operations."""
    async with db.begin():
        result = await db.execute(
            select(Prescription)
            .where(Prescription.id == prescription_id)
        )
        prescription = result.scalars().first()
        if not prescription:
            raise HTTPException(status_code=404, detail="Prescription not found")

        await db.delete(prescription)
        await db.commit()

@router.post("/categories/", response_model=DrugCategoryResponse)
async def create_drug_category(
    category: DrugCategoryCreate, 
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(pharmacist_only)
):
    """Create drug category with async operations."""
    async with db.begin():
        result = await db.execute(
            select(DrugCategory)
            .where(DrugCategory.name == category.name)
        )
        existing_category = result.scalars().first()
        if existing_category:
            raise HTTPException(
                status_code=400, 
                detail="Category already exists"
            )
        
        new_category = DrugCategory(**category.model_dump())
        db.add(new_category)
        await db.commit()
        await db.refresh(new_category)
        return new_category

@router.get("/categories/", response_model=List[DrugCategoryResponse])
@cache(expire=3600)  # Cache for 1 hour
async def get_drug_categories(db: AsyncSession = Depends(get_async_db)):
    """List drug categories with caching."""
    result = await db.execute(select(DrugCategory))
    return result.scalars().all()

@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_drug_category(
    category_id: int, 
    db: AsyncSession = Depends(get_async_db), 
    user: User = Depends(pharmacist_only)
):
    """Delete drug category with async operations."""
    async with db.begin():
        result = await db.execute(
            select(DrugCategory)
            .where(DrugCategory.id == category_id)
        )
        category = result.scalars().first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        await db.delete(category)
        await db.commit()

@router.post("/inventory/", response_model=InventoryResponse)
async def add_inventory(
    item: InventoryCreate, 
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(pharmacist_only)
):
    """Add inventory item with async operations."""
    async with db.begin():
        result = await db.execute(
            select(DrugCategory)
            .where(DrugCategory.id == item.category_id)
        )
        category = result.scalars().first()
        if not category:
            raise HTTPException(
                status_code=404, 
                detail="Drug category not found"
            )

        result = await db.execute(
            select(Inventory)
            .where(Inventory.drug_name == item.drug_name)
        )
        existing_item = result.scalars().first()
        if existing_item:
            existing_item.quantity += item.quantity
        else:
            new_item = Inventory(**item.model_dump())
            db.add(new_item)

        await db.commit()
        
        result = await db.execute(
            select(Inventory)
            .where(Inventory.drug_name == item.drug_name)
        )
        return result.scalars().first()

@router.get("/inventory/", response_model=List[InventoryResponse])
@cache(expire=120)  # Cache for 2 minutes
async def get_inventory(db: AsyncSession = Depends(get_async_db)):
    """List inventory items with caching."""
    result = await db.execute(
        select(Inventory)
        .options(selectinload(Inventory.category))
    )
    return result.scalars().all()

@router.put("/inventory/{inventory_id}/update-quantity", response_model=InventoryResponse)
async def update_inventory_quantity(
    inventory_id: int, 
    update: InventoryQuantityUpdate, 
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(pharmacist_only)
):
    """Update inventory quantity with async operations."""
    async with db.begin():
        result = await db.execute(
            select(Inventory)
            .where(Inventory.id == inventory_id)
        )
        inventory_item = result.scalars().first()
        if not inventory_item:
            raise HTTPException(
                status_code=404, 
                detail="Inventory item not found"
            )

        inventory_item.quantity = update.quantity  
        await db.commit()
        await db.refresh(inventory_item)
        return inventory_item

@router.put("/inventory/{inventory_id}", response_model=InventoryResponse)
async def update_inventory(
    inventory_id: int, 
    update: InventoryUpdate, 
    db: AsyncSession = Depends(get_async_db)
):
    """Update inventory item with async operations."""
    async with db.begin():
        result = await db.execute(
            select(Inventory)
            .where(Inventory.id == inventory_id)
        )
        item = result.scalars().first()
        if not item:
            raise HTTPException(status_code=404, detail="Inventory not found")
        
        result = await db.execute(
            select(DrugCategory)
            .where(DrugCategory.id == update.category_id)
        )
        category = result.scalars().first()
        if not category:
            raise HTTPException(
                status_code=404, 
                detail="Drug category not found"
            )

        item.drug_name = update.drug_name
        item.quantity = update.quantity
        item.category_id = update.category_id

        await db.commit()
        await db.refresh(item)
        return item

@router.delete("/inventory/{inventory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_inventory_item(
    inventory_id: int, 
    db: AsyncSession = Depends(get_async_db)
):
    """Delete inventory item with async operations."""
    async with db.begin():
        result = await db.execute(
            select(Inventory)
            .where(Inventory.id == inventory_id)
        )
        item = result.scalars().first()
        if not item:
            raise HTTPException(status_code=404, detail="Inventory not found")
        
        await db.delete(item)
        await db.commit()