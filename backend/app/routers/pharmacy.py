from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from models.pharmacy import Prescription, PrescriptionStatus, Inventory
from models.patient import Patient
from models.user import User
from models.doctor import Doctor
from schemas.pharmacy import PrescriptionCreate, PrescriptionResponse
from schemas.inventory import InventoryCreate, InventoryResponse
from core.database import get_db
from core.dependencies import RoleChecker

router = APIRouter(prefix="/pharmacy", tags=["Pharmacy"])

pharmacist_only = RoleChecker(["pharmacy"])
doctor_only = RoleChecker(["doctor"])

### **Create Prescription (Doctor)**
@router.post("/prescriptions/", response_model=PrescriptionResponse)
def create_prescription(prescription: PrescriptionCreate, db: Session = Depends(get_db),
                        user: User = Depends(doctor_only)):
    patient = db.query(Patient).filter(Patient.id == prescription.patient_id).first()
    doctor = db.query(Doctor).filter(Doctor.id == prescription.prescribed_by).first()
    drug = db.query(Inventory).filter(Inventory.drug_name == prescription.drug_name).first()

    if not patient or not doctor:
        raise HTTPException(status_code=400, detail="Invalid patient or doctor ID")
    
    if not drug:
        raise HTTPException(status_code=400, detail="Drug not available in inventory")

    new_prescription = Prescription(**prescription.model_dump())
    db.add(new_prescription)
    db.commit()
    db.refresh(new_prescription)
    return new_prescription

### **Get Prescriptions**
@router.get("/prescriptions/", response_model=List[PrescriptionResponse])
def get_prescriptions(db: Session = Depends(get_db)):
    return db.query(Prescription).all()

### **Dispense Prescription & Update Inventory**
@router.put("/prescriptions/{prescription_id}/dispense", response_model=PrescriptionResponse)
def dispense_prescription(prescription_id: int, db: Session = Depends(get_db),
                          user: User = Depends(pharmacist_only)):
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    
    if prescription.status == PrescriptionStatus.DISPENSED:
        raise HTTPException(status_code=400, detail="Prescription already dispensed")

    # Check drug availability in inventory
    drug_item = db.query(Inventory).filter(Inventory.drug_name == prescription.drug_name).first()
    
    if not drug_item:
        raise HTTPException(status_code=404, detail=f"'{prescription.drug_name}' is not available in inventory")
    
    if drug_item.quantity <= 0:
        raise HTTPException(status_code=400, detail=f"'{prescription.drug_name}' is out of stock. Cannot dispense.")


    # Dispense the drug and update inventory
    prescription.status = PrescriptionStatus.DISPENSED
    #drug_item.quantity -= 1  # Reduce inventory quantity
    db.commit()
    db.refresh(prescription)
    return prescription




### **Delete Prescription**
@router.delete("/prescriptions/{prescription_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prescription(prescription_id: int, db: Session = Depends(get_db)):
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")

    db.delete(prescription)
    db.commit()
    return

### **Add Inventory (Pharmacist)**
@router.post("/inventory/", response_model=InventoryResponse)
def add_inventory(item: InventoryCreate, db: Session = Depends(get_db),
                  user: User = Depends(pharmacist_only)):
    existing_item = db.query(Inventory).filter(Inventory.drug_name == item.drug_name).first()

    if existing_item:
        existing_item.quantity += item.quantity  # Update quantity
    else:
        
        new_item = Inventory(
            drug_name = item.drug_name,
            quantity = item.quantity,
            added_by = item.added_by
        )
        db.add(new_item)

    db.commit()
    return db.query(Inventory).filter(Inventory.drug_name == item.drug_name).first()


### **Get Inventory**
@router.get("/inventory/", response_model=List[InventoryResponse])
def get_inventory(db: Session = Depends(get_db)):
    return db.query(Inventory).all()

### **Update Drug Quantity Inventory**

@router.put("/inventory/{inventory_id}", response_model=List[InventoryResponse])
def get_inventory(inventory_id :int, quantity: int, db: Session = Depends(get_db)):
    item = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if not item:
         raise HTTPException(status_code=404, detail="Inventory not found")
    new_quantity = Inventory.quantity = quantity
    
    db.add(new_quantity)
    db.commit()
    return new_quantity

    