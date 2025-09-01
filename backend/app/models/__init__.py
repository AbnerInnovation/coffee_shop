# Import all models to ensure they are registered with SQLAlchemy
from .base import BaseModel
from ..db.base import Base
from .user import User, UserRole
from .menu import MenuItem, MenuItemVariant, Category
from .table import Table
from .order import Order, OrderItem, OrderStatus

# Make models available for import from app.models
__all__ = [
    "Base", "BaseModel", 
    "User", "UserRole",
    "MenuItem", "MenuItemVariant", "Category",
    "Table",
    "Order", "OrderItem", "OrderStatus"
]
