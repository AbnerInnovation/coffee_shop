from sqlalchemy import String, Boolean, Column, Text, Integer
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import List, Optional, TYPE_CHECKING
from .base import BaseModel

if TYPE_CHECKING:
    from .user import User
    from .menu import MenuItem, Category
    from .order import Order
    from .table import Table
    from .restaurant_subscription import RestaurantSubscription
    from .subscription_payment import SubscriptionPayment
    from .subscription_alert import SubscriptionAlert

class Restaurant(BaseModel):
    """
    Restaurant model for multi-tenant support.
    Each restaurant has its own subdomain and isolated data.
    """
    __tablename__ = "restaurants"
    
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    subdomain: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    business_type: Mapped[str] = mapped_column(String(50), default="restaurant", nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Timezone for the restaurant (default to America/Los_Angeles)
    timezone: Mapped[str] = mapped_column(String(50), default="America/Los_Angeles", nullable=False)
    
    # Business settings
    currency: Mapped[str] = mapped_column(String(3), default="MXN", nullable=False)
    tax_rate: Mapped[Optional[float]] = mapped_column(nullable=True, default=0.0)
    
    # Kitchen settings
    kitchen_print_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    kitchen_print_paper_width: Mapped[int] = mapped_column(Integer, default=80, nullable=False)  # 58mm or 80mm
    
    # Customer receipt settings
    customer_print_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    customer_print_paper_width: Mapped[int] = mapped_column(Integer, default=80, nullable=False)  # 58mm or 80mm
    
    # Order settings
    allow_dine_in_without_table: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Relationships
    users: Mapped[List["User"]] = relationship("User", back_populates="restaurant", cascade="all, delete-orphan")
    menu_items: Mapped[List["MenuItem"]] = relationship("MenuItem", back_populates="restaurant", cascade="all, delete-orphan")
    categories: Mapped[List["Category"]] = relationship("Category", back_populates="restaurant", cascade="all, delete-orphan")
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="restaurant", cascade="all, delete-orphan")
    tables: Mapped[List["Table"]] = relationship("Table", back_populates="restaurant", cascade="all, delete-orphan")
    subscription: Mapped[Optional["RestaurantSubscription"]] = relationship("RestaurantSubscription", back_populates="restaurant", uselist=False)
    payments: Mapped[List["SubscriptionPayment"]] = relationship("SubscriptionPayment", back_populates="restaurant", cascade="all, delete-orphan")
    alerts: Mapped[List["SubscriptionAlert"]] = relationship("SubscriptionAlert", back_populates="restaurant", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Restaurant(id={self.id}, name='{self.name}', subdomain='{self.subdomain}')>"
