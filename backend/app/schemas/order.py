from .base import PhoenixBaseModel as BaseModel
from pydantic import Field, validator
from datetime import datetime
from typing import List, Optional
from enum import Enum
import re

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
    
    @validator('special_instructions')
    def sanitize_instructions(cls, v):
        """Remove potentially dangerous characters from special instructions."""
        if v:
            # Remove HTML tags and script content
            v = re.sub(r'<[^>]*>', '', v)
            v = re.sub(r'[<>]', '', v)
        return v.strip() if v else v

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemUpdate(BaseModel):
    quantity: Optional[int] = Field(None, gt=0)
    special_instructions: Optional[str] = None
    status: Optional[OrderStatus] = None

class OrderItemInDBBase(OrderItemBase):
    id: int
    order_id: int
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
        if v:
            # Remove HTML tags and script content
            v = re.sub(r'<[^>]*>', '', v)
            v = re.sub(r'[<>]', '', v)
        return v.strip() if v else v

class OrderCreate(OrderBase):
    customer_name: Optional[str] = Field(None, max_length=100)
    items: List[OrderItemCreate] = Field(..., min_items=1, max_items=50, description="Order must have 1-50 items")
    
    @validator('customer_name')
    def validate_customer_name(cls, v):
        """Validate customer name contains only allowed characters."""
        if v:
            # Allow letters, spaces, hyphens, apostrophes, and periods
            if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\-\'.]+$', v):
                raise ValueError('Customer name contains invalid characters')
        return v.strip() if v else v

class OrderUpdate(BaseModel):
    table_id: Optional[int] = None
    notes: Optional[str] = None
    status: Optional[OrderStatus] = None
    is_paid: Optional[bool] = None
    payment_method: Optional[PaymentMethod] = None

class OrderInDBBase(OrderBase):
    id: int
    created_at: datetime
    updated_at: datetime
    total_amount: float = 0.0
    table_number: Optional[int] = None
    customer_name: Optional[str] = None
    user_id: Optional[int] = None
    order_type: Optional[str] = None
    deleted_at: Optional[datetime] = None
    items: List[OrderItem] = []

    class Config:
        orm_mode = True

class Order(OrderInDBBase):
    pass

class OrderInDB(OrderInDBBase):
    pass
