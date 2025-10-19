from sqlalchemy import String, Integer, Float, Boolean, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import List, Optional, Dict, Any
from enum import Enum as PyEnum
from .base import BaseModel

class PlanTier(str, PyEnum):
    """Plan tier enumeration"""
    TRIAL = "trial"
    STARTER = "starter"
    BASIC = "basic"
    PRO = "pro"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"

class SubscriptionPlan(BaseModel):
    """
    Subscription plans available for restaurants.
    Each plan has different limits and features.
    """
    __tablename__ = "subscription_plans"
    
    # Basic info
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    tier: Mapped[PlanTier] = mapped_column(
        SQLEnum(PlanTier, name='plan_tier', values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        index=True
    )
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Pricing
    monthly_price: Mapped[float] = mapped_column(Float, nullable=False)
    annual_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 25% discount
    
    # User limits
    max_admin_users: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    max_waiter_users: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    max_cashier_users: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_kitchen_users: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_owner_users: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # Resource limits
    max_tables: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    max_menu_items: Mapped[int] = mapped_column(Integer, nullable=False, default=50)
    max_categories: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    
    # Feature flags
    has_kitchen_module: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_ingredients_module: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_inventory_module: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_advanced_reports: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_multi_branch: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_priority_support: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Report retention (in days, -1 for unlimited)
    report_retention_days: Mapped[int] = mapped_column(Integer, nullable=False, default=7)
    
    # Support hours per month
    support_hours_monthly: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    
    # Trial settings (only for trial plan)
    is_trial: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    trial_duration_days: Mapped[int] = mapped_column(Integer, nullable=False, default=14)
    
    # Display settings
    is_popular: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # Additional features as JSON
    features: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Relationships
    subscriptions: Mapped[List["RestaurantSubscription"]] = relationship(
        "RestaurantSubscription", 
        back_populates="plan",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<SubscriptionPlan(id={self.id}, name='{self.name}', tier='{self.tier}', price=${self.monthly_price})>"
    
    @property
    def total_max_users(self) -> int:
        """Calculate total maximum users allowed"""
        return (
            self.max_admin_users + 
            self.max_waiter_users + 
            self.max_cashier_users + 
            self.max_kitchen_users +
            self.max_owner_users
        )
    
    @property
    def annual_discount_percentage(self) -> float:
        """Calculate annual discount percentage"""
        if self.annual_price and self.monthly_price > 0:
            monthly_total = self.monthly_price * 12
            discount = ((monthly_total - self.annual_price) / monthly_total) * 100
            return round(discount, 2)
        return 0.0
