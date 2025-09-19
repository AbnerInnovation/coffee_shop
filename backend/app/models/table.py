from sqlalchemy import Integer, String, Boolean, Column
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import List
from .base import BaseModel
from .order import Order

class Table(BaseModel):
    __tablename__ = "tables"
    
    number: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    location: Mapped[str] = mapped_column(String(50), nullable=False)
    is_occupied: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Relationships
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="table", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Table(id={self.id}, number={self.number}, capacity={self.capacity}, is_occupied={self.is_occupied})>"
