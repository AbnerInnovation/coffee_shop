from enum import Enum as PyEnum
from sqlalchemy import String, Float, Boolean, Integer, ForeignKey, Column
from sqlalchemy.orm import relationship
from .base import BaseModel
from ..db.base import Base

# Define Category model
class Category(Base, BaseModel):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)
    
    # Relationship to menu items
    menu_items = relationship("MenuItem", back_populates="category")
    
    def __init__(self, name: str, description: str = None):
        self.name = name.upper()  # Store category names in uppercase for consistency
        self.description = description

class MenuItem(Base, BaseModel):
    __tablename__ = "menu_items"

    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    price = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)
    image_url = Column(String(500), nullable=True)
    
    # Relationships
    category = relationship("Category", back_populates="menu_items")
    variants = relationship(
        "MenuItemVariant", 
        back_populates="menu_item", 
        cascade="all, delete-orphan"
    )
    order_items = relationship("OrderItem", back_populates="menu_item")

class MenuItemVariant(Base, BaseModel):
    __tablename__ = "menu_item_variants"

    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)
    name = Column(String(50), nullable=False)  # e.g. "Small", "Medium", "Large"
    price = Column(Float, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)

    # Relationships
    menu_item = relationship("MenuItem", back_populates="variants")
    order_items = relationship("OrderItem", back_populates="variant")
