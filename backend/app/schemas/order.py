from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
from enum import Enum

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
    menu_item_id: int
    variant_id: Optional[int] = None
    quantity: int = Field(..., gt=0)
    special_instructions: Optional[str] = None
    status: OrderStatus = OrderStatus.PENDING

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
    table_id: int
    notes: Optional[str] = None
    status: OrderStatus = OrderStatus.PENDING
    is_paid: bool = False
    payment_method: Optional[PaymentMethod] = None

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

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
