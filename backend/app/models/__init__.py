# Import all models to ensure they are registered with SQLAlchemy
from .base import BaseModel
from ..db.base import Base
from .user import User, UserRole
from .menu import MenuItem, MenuItemVariant, Category
from .table import Table
from .order import Order, OrderItem, OrderStatus
from .cash_register import (
    CashRegisterSession,
    CashTransaction,
    CashRegisterReport,
    SessionStatus,
    TransactionType,
    ReportType
)
from .special_note_stats import SpecialNoteStats
from .subscription_plan import SubscriptionPlan, PlanTier
from .subscription_addon import SubscriptionAddon, AddonType, AddonCategory
from .restaurant_subscription import RestaurantSubscription, SubscriptionStatus, BillingCycle
from .restaurant_addon import RestaurantAddon
from .restaurant import Restaurant

# Make models available for import from app.models
__all__ = [
    "Base", "BaseModel",
    "User", "UserRole",
    "MenuItem", "MenuItemVariant", "Category",
    "Table",
    "Order", "OrderItem", "OrderStatus",
    "CashRegisterSession",
    "CashTransaction",
    "CashRegisterReport",
    "SessionStatus",
    "TransactionType",
    "ReportType",
    "SpecialNoteStats",
    "Restaurant",
    "SubscriptionPlan", "PlanTier",
    "SubscriptionAddon", "AddonType", "AddonCategory",
    "RestaurantSubscription", "SubscriptionStatus", "BillingCycle",
    "RestaurantAddon"
]
