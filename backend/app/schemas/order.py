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

class OrderItem(OrderItemInDBBase):
    variant_name: Optional[str] = None
    variant_price: Optional[float] = None

class OrderBase(BaseModel):
    table_id: int
    notes: Optional[str] = None
    status: OrderStatus = OrderStatus.PENDING

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class OrderUpdate(BaseModel):
    table_id: Optional[int] = None
    notes: Optional[str] = None
    status: Optional[OrderStatus] = None

class OrderInDBBase(OrderBase):
    id: int
    created_at: datetime
    updated_at: datetime
    total_amount: float

    class Config:
        orm_mode = True

class Order(OrderInDBBase):
    items: List[OrderItem] = []

class OrderInDB(OrderInDBBase):
    pass
