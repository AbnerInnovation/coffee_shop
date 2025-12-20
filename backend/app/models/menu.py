from sqlalchemy import String, Float, Boolean, Integer, ForeignKey, Column, Text, and_, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import List, Optional, TYPE_CHECKING
from .base import BaseModel

if TYPE_CHECKING:
    from .order_item import OrderItem
    from .restaurant import Restaurant
    from .printer import Printer

class Category(BaseModel):
    __tablename__ = "categories"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    visible_in_kitchen: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Multi-tenant support
    restaurant_id: Mapped[int] = mapped_column(Integer, ForeignKey("restaurants.id"), nullable=False, index=True)
    
    # Relationships
    restaurant: Mapped["Restaurant"] = relationship("Restaurant", back_populates="categories")
    menu_items: Mapped[List["MenuItem"]] = relationship(
        "MenuItem", 
        back_populates="category",
        cascade="all, delete-orphan"
    )
    printers: Mapped[List["Printer"]] = relationship(
        "Printer",
        secondary="category_printer",
        back_populates="categories"
    )
    
    def __init__(self, name: str, restaurant_id: int, description: Optional[str] = None, visible_in_kitchen: bool = True):
        self.name = name.upper()  # Store category names in uppercase for consistency
        self.restaurant_id = restaurant_id
        self.description = description
        self.visible_in_kitchen = visible_in_kitchen
        
    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name='{self.name}')>"

class MenuItem(BaseModel):
    __tablename__ = "menu_items"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    price: Mapped[float] = mapped_column(nullable=False)
    discount_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=None)  # Promotional price
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    is_available: Mapped[bool] = mapped_column(default=True, nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Ingredients configuration (JSON field for flexibility and performance)
    # Structure: {"options": [{"name": str, "choices": [str], "default": str}], "removable": [str]}
    ingredients: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=None)
    
    # Multi-tenant support
    restaurant_id: Mapped[int] = mapped_column(Integer, ForeignKey("restaurants.id"), nullable=False, index=True)
    
    # Relationships
    restaurant: Mapped["Restaurant"] = relationship("Restaurant", back_populates="menu_items")
    category: Mapped["Category"] = relationship(
        "Category", 
        back_populates="menu_items",
        lazy="joined"  # Eager load category with menu item
    )
    variants: Mapped[List["MenuItemVariant"]] = relationship(
        "MenuItemVariant", 
        back_populates="menu_item", 
        cascade="all, delete-orphan",
        primaryjoin="and_(MenuItem.id==MenuItemVariant.menu_item_id, MenuItemVariant.deleted_at==None)",
        lazy="selectin"  # Efficient eager loading for collections
    )
    order_items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="menu_item")
    
    def get_effective_price(self) -> float:
        """Returns discount_price if set and > 0, otherwise returns regular price"""
        if self.discount_price is not None and self.discount_price > 0:
            return self.discount_price
        return self.price
    
    def __repr__(self) -> str:
        return f"<MenuItem(id={self.id}, name='{self.name}', price={self.price})>"

class MenuItemVariant(BaseModel):
    __tablename__ = "menu_item_variants"

    menu_item_id: Mapped[int] = mapped_column(ForeignKey("menu_items.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g. "Small", "Medium", "Large"
    price: Mapped[float] = mapped_column(nullable=False)
    discount_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=None)  # Promotional price
    is_available: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Relationships
    menu_item: Mapped["MenuItem"] = relationship("MenuItem", back_populates="variants")
    order_items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="variant")
    
    def get_effective_price(self) -> float:
        """Returns discount_price if set and > 0, otherwise returns regular price"""
        if self.discount_price is not None and self.discount_price > 0:
            return self.discount_price
        return self.price
    
    def __repr__(self) -> str:
        return f"<MenuItemVariant(id={self.id}, name='{self.name}', price={self.price}, menu_item_id={self.menu_item_id})>"
