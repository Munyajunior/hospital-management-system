from pydantic import BaseModel

class InventoryBase(BaseModel):
    drug_name: str
    quantity: int
    added_by: int

class InventoryCreate(InventoryBase):
    pass

class InventoryResponse(InventoryBase):
    id: int
    
    class Config:
        from_attributes = True
