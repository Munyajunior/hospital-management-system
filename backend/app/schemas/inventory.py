from pydantic import BaseModel
from datetime import datetime


class DrugCategoryBase(BaseModel):
    name: str

class DrugCategoryCreate(DrugCategoryBase):
    pass

class DrugCategoryResponse(DrugCategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class InventoryBase(BaseModel):
    drug_name: str
    quantity: int
    added_by: int
    category_id: int  

class InventoryCreate(InventoryBase):
    pass

class InventoryUpdate(BaseModel):
    drug_name: str
    quantity: int
    category_id: int  

class InventoryQuantityUpdate(BaseModel):
    quantity: int
    
class CategoryResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class InventoryResponse(InventoryBase):
    id: int
    category: CategoryResponse  # Include category information
    added_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True