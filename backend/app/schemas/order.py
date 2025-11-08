from .base import PhoenixBaseModel as BaseModel
from pydantic import Field, validator, model_validator
from datetime import datetime
from typing import List, Optional
from enum import Enum
from ..core.validators import sanitize_text, validate_name

# OrderPerson Schemas
class OrderPersonBase(BaseModel):
    name: Optional[str] = Field(None, max_length=100, description="Person name (e.g., 'Persona 1', 'Juan')")
    position: int = Field(1, ge=1, le=20, description="Position/order of person (1-20)")
    
    @validator('name')
    def sanitize_person_name(cls, v):
        """Remove potentially dangerous characters from person name."""
        return sanitize_text(v) if v else v

class OrderPersonCreate(OrderPersonBase):
    items: List['OrderItemCreate'] = Field(default_factory=list, description="Items for this person")

class OrderPersonUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    position: Optional[int] = Field(None, ge=1, le=20)
    
    @validator('name')
    def sanitize_person_name_update(cls, v):
        return sanitize_text(v) if v else v

class OrderPerson(OrderPersonBase):
    id: int
    order_id: int
    created_at: datetime
    updated_at: datetime
    items: List['OrderItem'] = []
    
    class Config:
        orm_mode = True

# Order Item Extra Schemas
class OrderItemExtraBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Extra name (e.g., 'Extra tortillas')")
    price: float = Field(..., ge=0, description="Price must be non-negative")
    quantity: int = Field(1, ge=1, le=10, description="Quantity must be between 1 and 10")
    
    @validator('name')
    def sanitize_extra_name(cls, v):
        """Remove potentially dangerous characters from extra name."""
        return sanitize_text(v)

class OrderItemExtraCreate(OrderItemExtraBase):
    pass

class OrderItemExtraUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    price: Optional[float] = Field(None, ge=0)
    quantity: Optional[int] = Field(None, ge=1, le=10)
    
    @validator('name')
    def sanitize_extra_name_update(cls, v):
        """Remove potentially dangerous characters from extra name."""
        return sanitize_text(v) if v else v

class OrderItemExtra(OrderItemExtraBase):
    id: int
    order_item_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class OrderStatus(str, Enum):
    PENDING = "pending"
    PREPARING = "preparing"
    READY = "ready"
    COMPLETED = "completed"  # Final state (served/delivered + paid)
    CANCELLED = "cancelled"

class PaymentMethod(str, Enum):
    CASH = "cash"
    CARD = "card"
    DIGITAL = "digital"
    OTHER = "other"

class OrderItemBase(BaseModel):
    menu_item_id: int = Field(..., ge=1, description="Menu item ID must be positive")
    variant_id: Optional[int] = Field(None, ge=1, description="Variant ID must be positive")
    quantity: int = Field(..., ge=1, le=100, description="Quantity must be between 1 and 100")
    special_instructions: Optional[str] = Field(None, max_length=200)
    status: OrderStatus = OrderStatus.PENDING
    person_id: Optional[int] = Field(None, ge=1, description="Person ID for multi-diner orders")
    
    @validator('special_instructions')
    def sanitize_instructions(cls, v):
        """Remove potentially dangerous characters from special instructions."""
        return sanitize_text(v)

class OrderItemCreate(OrderItemBase):
    extras: List[OrderItemExtraCreate] = []

class OrderItemUpdate(BaseModel):
    quantity: Optional[int] = Field(None, gt=0)
    special_instructions: Optional[str] = None
    status: Optional[OrderStatus] = None

class OrderItemInDBBase(OrderItemBase):
    id: int
    order_id: int
    person_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class MenuItemBase(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    category: Optional[str] = None
    category_visible_in_kitchen: bool = True
    image_url: Optional[str] = None
    is_available: bool = True

    class Config:
        orm_mode = True

class VariantBase(BaseModel):
    id: int
    name: str
    price: float
    description: Optional[str] = None
    
    class Config:
        orm_mode = True

class OrderItem(OrderItemInDBBase):
    variant: Optional[VariantBase] = None
    unit_price: Optional[float] = None
    menu_item: Optional[MenuItemBase] = None
    extras: List[OrderItemExtra] = []
    
    class Config:
        orm_mode = True

class OrderBase(BaseModel):
    table_id: Optional[int] = Field(None, ge=1, description="Table ID must be positive")
    notes: Optional[str] = Field(None, max_length=500)
    status: OrderStatus = OrderStatus.PENDING
    is_paid: bool = False
    payment_method: Optional[PaymentMethod] = None
    
    @validator('notes')
    def sanitize_notes(cls, v):
        """Remove potentially dangerous characters from notes."""
        return sanitize_text(v)

class OrderCreate(OrderBase):
    customer_name: Optional[str] = Field(None, max_length=100)
    items: List[OrderItemCreate] = Field(default_factory=list, description="Direct items (legacy support)")
    persons: List[OrderPersonCreate] = Field(default_factory=list, description="Persons with their items")
    
    @model_validator(mode='after')
    def validate_has_items(self):
        """Ensure order has items either directly or through persons."""
        items = self.items or []
        persons = self.persons or []
        
        if not items and not persons:
            raise ValueError('Order must have items either directly or through persons')
        
        # Check total items don't exceed limit
        total_items = len(items)
        for person in persons:
            total_items += len(person.items)
        if total_items > 50:
            raise ValueError('Order cannot have more than 50 total items')
        
        return self
    
    @validator('customer_name')
    def validate_customer_name(cls, v):
        """Validate customer name contains only allowed characters."""
        return validate_name(v, 'Customer name') if v else v

class OrderUpdate(BaseModel):
    table_id: Optional[int] = None
    customer_name: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None
    status: Optional[OrderStatus] = None
    is_paid: Optional[bool] = None
    payment_method: Optional[PaymentMethod] = None
    order_type: Optional[str] = Field(None, max_length=50)
    
    @validator('customer_name')
    def validate_customer_name_update(cls, v):
        """Validate customer name contains only allowed characters."""
        return validate_name(v, 'Customer name') if v else v

class OrderInDBBase(OrderBase):
    id: int
    order_number: int
    created_at: datetime
    updated_at: datetime
    total_amount: float = 0.0
    subtotal: float = 0.0
    tax: float = 0.0
    taxRate: float = 0.0
    total: float = 0.0
    table_number: Optional[int] = None
    customer_name: Optional[str] = None
    user_id: Optional[int] = None
    order_type: Optional[str] = None
    sort: int = 50
    deleted_at: Optional[datetime] = None
    items: List[OrderItem] = []
    persons: List[OrderPerson] = []

    class Config:
        orm_mode = True

class Order(OrderInDBBase):
    pass

class OrderInDB(OrderInDBBase):
    pass

# Update forward references for circular dependencies
OrderPersonCreate.update_forward_refs()
OrderPerson.update_forward_refs()
OrderItem.update_forward_refs()
