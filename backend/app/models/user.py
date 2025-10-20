from enum import Enum as PyEnum
from sqlalchemy import String, Boolean, Column, Enum as SQLEnum, Integer, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import TYPE_CHECKING, Optional
from .base import BaseModel

if TYPE_CHECKING:
    from .order import Order
    from .restaurant import Restaurant

# Define UserRole enum
class UserRole(str, PyEnum):
    SYSADMIN = "sysadmin"
    ADMIN = "admin"
    STAFF = "staff"
    CUSTOMER = "customer"

# Define StaffType enum for staff sub-roles
class StaffType(str, PyEnum):
    WAITER = "waiter"      # Mesero: Crear/editar pedidos, gestionar mesas
    CASHIER = "cashier"    # Cajero: Procesar pagos, acceder a caja registradora
    KITCHEN = "kitchen"    # Cocina: Ver pedidos de cocina, marcar items preparados
    GENERAL = "general"    # General: Solo lectura

class User(BaseModel):
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(
        SQLEnum(UserRole, name='user_role', values_callable=lambda obj: [e.value for e in obj]), 
        default=UserRole.STAFF, 
        nullable=False
    )
    staff_type: Mapped[Optional[str]] = mapped_column(
        SQLEnum(StaffType, name='staff_type', values_callable=lambda obj: [e.value for e in obj]),
        nullable=True,
        comment="Sub-role for STAFF users (waiter, cashier, kitchen, general)"
    )
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Multi-tenant support
    restaurant_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("restaurants.id"), nullable=True, index=True)
    
    # Relationships
    restaurant: Mapped[Optional["Restaurant"]] = relationship("Restaurant", back_populates="users")
    orders = relationship("Order", back_populates="user")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
