from enum import Enum
from typing import Optional, TYPE_CHECKING
from sqlalchemy import Integer, String, Float, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .base import BaseModel, Base

if TYPE_CHECKING:
    from .order import Order
    from .menu import MenuItem, MenuItemVariant

# Enum for item status
class OrderItemStatus(str, Enum):
    PENDING = "pending"
    PREPARING = "preparing"
    READY = "ready"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class OrderItem(Base, BaseModel):
    __tablename__ = "order_items"
    __table_args__ = {"extend_existing": True}  # avoids reload errors during dev

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    menu_item_id: Mapped[int] = mapped_column(
        ForeignKey("menu_items.id"), nullable=False
    )
    variant_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("menu_item_variants.id"), nullable=True
    )
    quantity: Mapped[int] = mapped_column(default=1, nullable=False)
    unit_price: Mapped[float] = mapped_column(nullable=False)
    special_instructions: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    status: Mapped[OrderItemStatus] = mapped_column(
        SQLEnum(OrderItemStatus, name="order_item_status"),
        default=OrderItemStatus.PENDING,
        nullable=False,
    )

    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="items")
    menu_item: Mapped["MenuItem"] = relationship("MenuItem", back_populates="order_items")
    variant: Mapped[Optional["MenuItemVariant"]] = relationship(
        "MenuItemVariant", back_populates="order_items"
    )

    def __repr__(self) -> str:
        return (
            f"<OrderItem(id={self.id}, order_id={self.order_id}, "
            f"menu_item_id={self.menu_item_id}, quantity={self.quantity}, status={self.status})>"
        )
