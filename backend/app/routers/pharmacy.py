from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from models.pharmacy import Prescription, PrescriptionStatus, Inventory, DrugCategory
from models.patient import Patient
from models.user import User
from models.doctor import Doctor
from schemas.pharmacy import PrescriptionCreate, PrescriptionResponse
from schemas.inventory import DrugCategoryCreate, DrugCategoryResponse, InventoryCreate, InventoryResponse, InventoryUpdate, InventoryQuantityUpdate
from core.database import get_db
from core.dependencies import RoleChecker

router = APIRouter(prefix="/pharmacy", tags=["Pharmacy"])

pharmacist_only = RoleChecker(["pharmacist"])
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
    """
    Dispenses a prescription and updates the inventory.
    """
    # Fetch the prescription
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    
    if prescription.status == PrescriptionStatus.DISPENSED:
        raise HTTPException(status_code=400, detail="Prescription already dispensed")

    # Fetch the drug from inventory
    drug_item = db.query(Inventory).filter(Inventory.drug_name == prescription.drug_name).first()
    if not drug_item:
        raise HTTPException(status_code=404, detail=f"'{prescription.drug_name}' is not available in inventory")
    
    if drug_item.quantity <= 0:
        raise HTTPException(status_code=400, detail=f"'{prescription.drug_name}' is out of stock. Cannot dispense.")

    # Update the inventory quantity
    new_quantity = drug_item.quantity - 1
    update_data = InventoryQuantityUpdate(quantity=new_quantity) 
    update_inventory_quantity(drug_item.id, update_data, db, user)

    # Update the prescription status
    prescription.status = PrescriptionStatus.DISPENSED
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


### **Create Drug Category**
@router.post("/categories/", response_model=DrugCategoryResponse)
def create_drug_category(category: DrugCategoryCreate, db: Session = Depends(get_db),
                         user: User = Depends(pharmacist_only)):
    existing_category = db.query(DrugCategory).filter(DrugCategory.name == category.name).first()
    if existing_category:
        raise HTTPException(status_code=400, detail="Category already exists")
    
    new_category = DrugCategory(**category.model_dump())
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category


### **Get All Drug Categories**
@router.get("/categories/", response_model=List[DrugCategoryResponse])
def get_drug_categories(db: Session = Depends(get_db)):
    return db.query(DrugCategory).all()


### **Delete a Drug Category**
@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def get_drug_categories(category_id: int, db: Session = Depends(get_db), user: User = Depends(pharmacist_only)):
    category = db.query(DrugCategory).filter(DrugCategory.id == category_id).first()

    db.delete(category)
    db.commit()
    return 


### **Add Inventory (Pharmacist)**
@router.post("/inventory/", response_model=InventoryResponse)
def add_inventory(item: InventoryCreate, db: Session = Depends(get_db),
                  user: User = Depends(pharmacist_only)):
    # Check if the drug category exists
    category = db.query(DrugCategory).filter(DrugCategory.id == item.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Drug category not found")

    existing_item = db.query(Inventory).filter(Inventory.drug_name == item.drug_name).first()
    if existing_item:
        existing_item.quantity += item.quantity  # Update quantity
    else:
        new_item = Inventory(**item.model_dump())
        db.add(new_item)

    db.commit()
    return db.query(Inventory).filter(Inventory.drug_name == item.drug_name).first()



### **Get Inventory**
@router.get("/inventory/", response_model=List[InventoryResponse])
def get_inventory(db: Session = Depends(get_db)):
    inventory = db.query(Inventory).options(joinedload(Inventory.category)).all()
    return inventory

@router.put("/inventory/{inventory_id}/update-quantity", response_model=InventoryResponse)
def update_inventory_quantity(
    inventory_id: int, 
    update: InventoryQuantityUpdate, 
    db: Session = Depends(get_db),
    user: User = Depends(pharmacist_only)
):
    """
    Updates the quantity of a drug in the inventory.
    """
    # Fetch the inventory item
    inventory_item = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if not inventory_item:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    # Update the quantity
    inventory_item.quantity = update.quantity  
    db.commit()
    db.refresh(inventory_item)

    return inventory_item


### **Update Inventory**
@router.put("/inventory/{inventory_id}", response_model=InventoryResponse)
def update_inventory(inventory_id: int, update: InventoryUpdate, db: Session = Depends(get_db)):
    item = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Inventory not found")
    
    # Check if the new category exists
    category = db.query(DrugCategory).filter(DrugCategory.id == update.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Drug category not found")

    item.drug_name = update.drug_name
    item.quantity = update.quantity
    item.category_id = update.category_id  # Update category

    db.commit()
    db.refresh(item)
    return item

### **Delete Drug from Inventory**
@router.delete("/inventory/{inventory_id}", status_code=status.HTTP_204_NO_CONTENT)
def get_inventory(inventory_id :int, db: Session = Depends(get_db)):
    item = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if not item:
         raise HTTPException(status_code=404, detail="Inventory not found")
    
    db.delete(item)
    db.commit()
    return

    