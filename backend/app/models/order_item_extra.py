from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone
from sqlalchemy import Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from ..db.base import Base

if TYPE_CHECKING:
    from .order_item import OrderItem

class OrderItemExtra(Base):
    """
    Represents an extra/add-on for an order item.
    Examples: Extra tortillas, Extra guacamole, Extra cheese, etc.
    
    Note: Does not inherit from BaseModel to avoid soft delete (deleted_at column).
    Extras are permanently deleted when removed.
    """
    __tablename__ = "order_item_extras"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    order_item_id: Mapped[int] = mapped_column(
        ForeignKey("order_items.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        onupdate=lambda: datetime.now(timezone.utc), 
        nullable=False
    )

    # Relationships
    order_item: Mapped["OrderItem"] = relationship("OrderItem", back_populates="extras")

    def __repr__(self) -> str:
        return (
            f"<OrderItemExtra(id={self.id}, name='{self.name}', "
            f"price={self.price}, quantity={self.quantity})>"
        )
