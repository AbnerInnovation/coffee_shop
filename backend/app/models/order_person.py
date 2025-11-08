from typing import List, Optional, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .base import BaseModel

if TYPE_CHECKING:
    from .order import Order
    from .order_item import OrderItem

class OrderPerson(BaseModel):
    """
    Represents a diner/person in an order.
    Allows splitting items by person for better kitchen organization and future individual billing.
    """
    __tablename__ = "order_persons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # "Persona 1", "Juan", etc.
    position: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # Order of persons (1, 2, 3...)
    
    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="persons")
    items: Mapped[List["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="person",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<OrderPerson(id={self.id}, order_id={self.order_id}, name='{self.name}', position={self.position})>"
