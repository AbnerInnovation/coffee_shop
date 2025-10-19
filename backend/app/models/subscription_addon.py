from sqlalchemy import String, Integer, Float, Boolean, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import List, Optional, Dict, Any
from enum import Enum as PyEnum
from .base import BaseModel

class AddonType(str, PyEnum):
    """Addon type enumeration"""
    MODULE = "module"  # Feature modules (inventory, advanced reports, etc.)
    RESOURCE = "resource"  # Additional resources (users, tables, products)
    SERVICE = "service"  # One-time services (training, menu setup)

class AddonCategory(str, PyEnum):
    """Addon category for organization"""
    INVENTORY = "inventory"
    REPORTS = "reports"
    KITCHEN = "kitchen"
    USERS = "users"
    TABLES = "tables"
    PRODUCTS = "products"
    TRAINING = "training"
    SETUP = "setup"
    DESIGN = "design"

class SubscriptionAddon(BaseModel):
    """
    Add-ons that can be purchased in addition to subscription plans.
    Can be recurring (monthly) or one-time purchases.
    """
    __tablename__ = "subscription_addons"
    
    # Basic info
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Type and category
    addon_type: Mapped[AddonType] = mapped_column(
        SQLEnum(AddonType, name='addon_type', values_callable=lambda obj: [e.value for e in obj]),
        nullable=False
    )
    category: Mapped[AddonCategory] = mapped_column(
        SQLEnum(AddonCategory, name='addon_category', values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        index=True
    )
    
    # Pricing
    monthly_price: Mapped[float] = mapped_column(Float, nullable=False)
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Quantity settings
    is_quantifiable: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    min_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    max_quantity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # NULL = unlimited
    
    # What this addon provides
    provides_users: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    provides_tables: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    provides_menu_items: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # Feature flags (for module addons)
    enables_inventory: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    enables_advanced_reports: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    enables_kitchen: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Availability (which plans can purchase this)
    available_for_plans: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    # Example: {"tiers": ["starter", "basic", "pro"]} or {"exclude_tiers": ["enterprise"]}
    
    # Display settings
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # Additional metadata
    addon_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Relationships
    restaurant_addons: Mapped[List["RestaurantAddon"]] = relationship(
        "RestaurantAddon",
        back_populates="addon",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<SubscriptionAddon(id={self.id}, code='{self.code}', price=${self.monthly_price})>"
    
    def is_available_for_plan(self, plan_tier: str) -> bool:
        """Check if this addon is available for a specific plan tier"""
        if not self.available_for_plans:
            return True  # Available for all if not specified
        
        if "tiers" in self.available_for_plans:
            return plan_tier in self.available_for_plans["tiers"]
        
        if "exclude_tiers" in self.available_for_plans:
            return plan_tier not in self.available_for_plans["exclude_tiers"]
        
        return True
