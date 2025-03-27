from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models.billing import Billing, BillingStatus
from models.patient import Patient
from models.user import User
from schemas.billing import BillingCreate, BillingResponse
from core.database import get_db
from core.dependencies import RoleChecker

router = APIRouter(prefix="/billing", tags=["Billing"])

billing_staff_only = RoleChecker(["admin", "billing"])

@router.post("/", response_model=BillingResponse)
def create_billing(billing: BillingCreate, db: Session = Depends(get_db), user: User = Depends(billing_staff_only)):
    """Create a new billing record."""
    patient = db.query(Patient).filter(Patient.id == billing.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    new_billing = Billing(**billing.model_dump())
    db.add(new_billing)
    db.commit()
    db.refresh(new_billing)
    return new_billing

@router.get("/", response_model=list[BillingResponse])
def list_billing(db: Session = Depends(get_db), user: User = Depends(billing_staff_only)):
    """Retrieve all billing records."""
    return db.query(Billing).all()

@router.put("/{billing_id}/status", response_model=BillingResponse)
def update_billing_status(billing_id: int, status: BillingStatus, db: Session = Depends(get_db), user: User = Depends(billing_staff_only)):
    """Update the status of a billing record."""
    billing = db.query(Billing).filter(Billing.id == billing_id).first()
    if not billing:
        raise HTTPException(status_code=404, detail="Billing record not found")

    billing.status = status
    db.commit()
    db.refresh(billing)
    return billing

@router.delete("/{billing_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_billing(billing_id: int, db: Session = Depends(get_db), user: User = Depends(billing_staff_only)):
    """Delete a billing record."""
    billing = db.query(Billing).filter(Billing.id == billing_id).first()
    if not billing:
        raise HTTPException(status_code=404, detail="Billing record not found")

    db.delete(billing)
    db.commit()