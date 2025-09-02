from sqlalchemy import String, Float, Boolean, Integer, ForeignKey, Column, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import List, Optional, TYPE_CHECKING
from .base import BaseModel, Base

if TYPE_CHECKING:
    from .order_item import OrderItem

class Category(Base, BaseModel):
    __tablename__ = "categories"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationship to menu items
    menu_items: Mapped[List["MenuItem"]] = relationship(
        "MenuItem", 
        back_populates="category",
        cascade="all, delete-orphan"
    )
    
    def __init__(self, name: str, description: Optional[str] = None):
        self.name = name.upper()  # Store category names in uppercase for consistency
        self.description = description
        
    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name='{self.name}')>"

class MenuItem(Base, BaseModel):
    __tablename__ = "menu_items"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    price: Mapped[float] = mapped_column(nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    is_available: Mapped[bool] = mapped_column(default=True, nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Relationships
    category: Mapped["Category"] = relationship("Category", back_populates="menu_items")
    variants: Mapped[List["MenuItemVariant"]] = relationship(
        "MenuItemVariant", 
        back_populates="menu_item", 
        cascade="all, delete-orphan"
    )
    order_items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="menu_item")
    
    def __repr__(self) -> str:
        return f"<MenuItem(id={self.id}, name='{self.name}', price={self.price})>"

class MenuItemVariant(Base, BaseModel):
    __tablename__ = "menu_item_variants"

    menu_item_id: Mapped[int] = mapped_column(ForeignKey("menu_items.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g. "Small", "Medium", "Large"
    price: Mapped[float] = mapped_column(nullable=False)
    is_available: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Relationships
    menu_item: Mapped["MenuItem"] = relationship("MenuItem", back_populates="variants")
    order_items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="variant")
    
    def __repr__(self) -> str:
        return f"<MenuItemVariant(id={self.id}, name='{self.name}', price={self.price}, menu_item_id={self.menu_item_id})>"
    order_items = relationship("OrderItem", back_populates="variant")
