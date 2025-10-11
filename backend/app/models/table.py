from sqlalchemy import Integer, String, Boolean, Column, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import List, TYPE_CHECKING
from .base import BaseModel
from .order import Order

if TYPE_CHECKING:
    from .restaurant import Restaurant

class Table(BaseModel):
    __tablename__ = "tables"
    
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    location: Mapped[str] = mapped_column(String(50), nullable=False)
    is_occupied: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Multi-tenant support
    restaurant_id: Mapped[int] = mapped_column(Integer, ForeignKey("restaurants.id"), nullable=False, index=True)
    
    # Relationships
    restaurant: Mapped["Restaurant"] = relationship("Restaurant", back_populates="tables")
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="table", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Table(id={self.id}, number={self.number}, capacity={self.capacity}, is_occupied={self.is_occupied})>"
