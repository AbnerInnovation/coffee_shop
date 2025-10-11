from enum import Enum as PyEnum
from typing import List, Optional, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import Integer, String, Float, ForeignKey, Enum as SQLEnum, DateTime, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .base import BaseModel

# Import the single source of OrderItem
from .order_item import OrderItem

if TYPE_CHECKING:
    from .restaurant import Restaurant

# Enum for order status
class OrderStatus(str, PyEnum):
    PENDING = "pending"
    PREPARING = "preparing"
    READY = "ready"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

# Enum for payment method
class PaymentMethod(str, PyEnum):
    CASH = "cash"
    CARD = "card"
    DIGITAL = "digital"
    OTHER = "other"

class Order(BaseModel):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    table_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("tables.id"), nullable=True)
    customer_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    order_type: Mapped[str] = mapped_column(String(50), default="dine_in", nullable=False)
    status: Mapped[OrderStatus] = mapped_column(
        SQLEnum(OrderStatus, name='order_status'),
        default=OrderStatus.PENDING,
        nullable=False
    )
    notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    total_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    is_paid: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    payment_method: Mapped[Optional[PaymentMethod]] = mapped_column(
        SQLEnum(PaymentMethod, name='payment_method'),
        nullable=True
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Multi-tenant support
    restaurant_id: Mapped[int] = mapped_column(Integer, ForeignKey("restaurants.id"), nullable=False, index=True)

    # Relationships
    restaurant: Mapped["Restaurant"] = relationship("Restaurant", back_populates="orders")
    table: Mapped["Table"] = relationship("Table", back_populates="orders")
    items: Mapped[List[OrderItem]] = relationship(
        "app.models.order_item.OrderItem",  # fully-qualified to avoid registry conflicts
        back_populates="order",
        cascade="all, delete-orphan"
    )
    user: Mapped[Optional["User"]] = relationship("User", back_populates="orders")

    def __repr__(self) -> str:
        return f"<Order(id={self.id}, status='{self.status}', table_id={self.table_id})>"
