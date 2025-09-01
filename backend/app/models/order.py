from enum import Enum as PyEnum
from sqlalchemy import Integer, String, Float, ForeignKey, Column, Enum as SQLEnum
from sqlalchemy.orm import relationship
from .base import BaseModel
from ..db.base import Base

# Define DB-safe enum
class OrderStatus(str, PyEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Order(Base, BaseModel):
    __tablename__ = "orders"

    table_id = Column(Integer, ForeignKey("tables.id"), nullable=False)
    status = Column(SQLEnum(OrderStatus, name='order_status'), default=OrderStatus.PENDING, nullable=False)
    notes = Column(String(500), nullable=True)
    total_amount = Column(Float, default=0.0, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    table = relationship("Table", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    user = relationship("User", back_populates="orders")

class OrderItem(Base, BaseModel):
    __tablename__ = "order_items"

    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)
    variant_id = Column(Integer, ForeignKey("menu_item_variants.id"), nullable=True)
    quantity = Column(Integer, default=1, nullable=False)
    unit_price = Column(Float, nullable=False)
    special_instructions = Column(String(500), nullable=True)
    status = Column(SQLEnum(OrderStatus, name='order_item_status'), default=OrderStatus.PENDING, nullable=False)

    # Relationships
    order = relationship("Order", back_populates="items")
    menu_item = relationship("MenuItem", back_populates="order_items")
    variant = relationship("MenuItemVariant", back_populates="order_items")
