from enum import Enum as PyEnum
from sqlalchemy import String, Boolean, Column, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import List, Optional, TYPE_CHECKING
from .base import BaseModel, Base

if TYPE_CHECKING:
    from .order import Order

# Define UserRole enum
class UserRole(str, PyEnum):
    ADMIN = "admin"
    STAFF = "staff"
    CUSTOMER = "customer"

class User(Base, BaseModel):
    __tablename__ = "users"
    
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, name='user_role'), 
        default=UserRole.STAFF, 
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    
    # Relationships
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="user")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
