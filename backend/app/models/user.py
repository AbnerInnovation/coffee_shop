from enum import Enum as PyEnum
from sqlalchemy import String, Boolean, Column, Enum as SQLEnum
from sqlalchemy.orm import relationship
from typing import TYPE_CHECKING
from .base import BaseModel

if TYPE_CHECKING:
    from .order import Order

# Define UserRole enum
class UserRole(str, PyEnum):
    ADMIN = "admin"
    STAFF = "staff"
    CUSTOMER = "customer"

class User(BaseModel):
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(
        SQLEnum(UserRole, name='user_role'), 
        default=UserRole.STAFF, 
        nullable=False
    )
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    orders = relationship("Order", back_populates="user")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
