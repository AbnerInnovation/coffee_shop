"""
Pydantic schemas for subscription system
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ==================== ENUMS ====================

class PlanTierEnum(str, Enum):
    TRIAL = "trial"
    STARTER = "starter"
    BASIC = "basic"
    PRO = "pro"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"


class AddonTypeEnum(str, Enum):
    MODULE = "module"
    RESOURCE = "resource"
    SERVICE = "service"


class AddonCategoryEnum(str, Enum):
    INVENTORY = "inventory"
    REPORTS = "reports"
    KITCHEN = "kitchen"
    USERS = "users"
    TABLES = "tables"
    PRODUCTS = "products"
    TRAINING = "training"
    SETUP = "setup"
    DESIGN = "design"


class SubscriptionStatusEnum(str, Enum):
    TRIAL = "trial"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class BillingCycleEnum(str, Enum):
    MONTHLY = "monthly"
    ANNUAL = "annual"


# ==================== SUBSCRIPTION PLAN SCHEMAS ====================

class SubscriptionPlanBase(BaseModel):
    name: str
    tier: PlanTierEnum
    display_name: str
    description: Optional[str] = None
    monthly_price: float
    annual_price: Optional[float] = None
    
    # User limits
    max_admin_users: int = 1
    max_waiter_users: int = 1
    max_cashier_users: int = 0
    max_kitchen_users: int = 0
    max_owner_users: int = 0
    
    # Resource limits
    max_tables: int = 10
    max_menu_items: int = 50
    max_categories: int = 10
    
    # Features
    has_kitchen_module: bool = False
    has_ingredients_module: bool = False
    has_inventory_module: bool = False
    has_advanced_reports: bool = False
    has_multi_branch: bool = False
    has_priority_support: bool = False
    
    report_retention_days: int = 7
    support_hours_monthly: float = 0.0
    
    is_trial: bool = False
    trial_duration_days: int = 14
    is_popular: bool = False
    
    features: Optional[Dict[str, Any]] = None


class SubscriptionPlanResponse(SubscriptionPlanBase):
    id: int
    is_active: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime
    total_max_users: int
    annual_discount_percentage: float
    
    class Config:
        from_attributes = True


# ==================== SUBSCRIPTION ADDON SCHEMAS ====================

class SubscriptionAddonBase(BaseModel):
    name: str
    code: str
    display_name: str
    description: Optional[str] = None
    addon_type: AddonTypeEnum
    category: AddonCategoryEnum
    monthly_price: float
    is_recurring: bool = True
    is_quantifiable: bool = False
    min_quantity: int = 1
    max_quantity: Optional[int] = None
    
    provides_users: int = 0
    provides_tables: int = 0
    provides_menu_items: int = 0
    
    enables_inventory: bool = False
    enables_advanced_reports: bool = False
    enables_kitchen: bool = False
    
    available_for_plans: Optional[Dict[str, Any]] = None
    addon_metadata: Optional[Dict[str, Any]] = None


class SubscriptionAddonResponse(SubscriptionAddonBase):
    id: int
    is_active: bool
    is_featured: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== RESTAURANT ADDON SCHEMAS ====================

class RestaurantAddonBase(BaseModel):
    addon_id: int
    quantity: int = 1


class RestaurantAddonCreate(RestaurantAddonBase):
    pass


class RestaurantAddonResponse(BaseModel):
    id: int
    subscription_id: int
    addon_id: int
    quantity: int
    unit_price: float
    total_price: float
    is_active: bool
    addon: SubscriptionAddonResponse
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== RESTAURANT SUBSCRIPTION SCHEMAS ====================

class RestaurantSubscriptionBase(BaseModel):
    plan_id: int
    billing_cycle: BillingCycleEnum = BillingCycleEnum.MONTHLY
    discount_code: Optional[str] = None


class RestaurantSubscriptionCreate(RestaurantSubscriptionBase):
    pass


class RestaurantSubscriptionResponse(BaseModel):
    id: int
    restaurant_id: int
    plan_id: int
    status: SubscriptionStatusEnum
    billing_cycle: BillingCycleEnum
    
    start_date: datetime
    trial_end_date: Optional[datetime]
    current_period_start: datetime
    current_period_end: datetime
    cancelled_at: Optional[datetime]
    
    base_price: float
    total_price: float
    discount_percentage: float
    discount_amount: float
    discount_code: Optional[str]
    auto_renew: bool
    
    # Relationships
    plan: SubscriptionPlanResponse
    addons: List[RestaurantAddonResponse] = []
    
    # Computed properties
    is_trial: bool
    is_active: bool
    days_until_renewal: int
    trial_days_remaining: int
    
    subscription_metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== REQUEST SCHEMAS ====================

class UpgradeSubscriptionRequest(BaseModel):
    new_plan_id: int


class AddAddonRequest(BaseModel):
    addon_code: str
    quantity: int = 1
    
    @validator('quantity')
    def quantity_must_be_positive(cls, v):
        if v < 1:
            raise ValueError('Quantity must be at least 1')
        return v


class RemoveAddonRequest(BaseModel):
    addon_code: str


class CalculateCostRequest(BaseModel):
    plan_id: int
    billing_cycle: BillingCycleEnum = BillingCycleEnum.MONTHLY
    addons: Optional[List[Dict[str, Any]]] = None
    discount_code: Optional[str] = None


class CalculateCostResponse(BaseModel):
    plan: Dict[str, Any]
    addons: List[Dict[str, Any]]
    subtotal: float
    discount: Dict[str, Any]
    total: float
    currency: str = "MXN"


class SubscriptionLimitsResponse(BaseModel):
    max_admin_users: int
    max_waiter_users: int
    max_cashier_users: int
    max_kitchen_users: int
    max_owner_users: int
    max_tables: int
    max_menu_items: int
    max_categories: int
    has_kitchen_module: bool
    has_ingredients_module: bool
    has_inventory_module: bool
    has_advanced_reports: bool
    has_multi_branch: bool
    report_retention_days: int
    
    # Current usage (optional)
    current_admin_users: Optional[int] = None
    current_waiter_users: Optional[int] = None
    current_cashier_users: Optional[int] = None
    current_kitchen_users: Optional[int] = None
    current_tables: Optional[int] = None
    current_menu_items: Optional[int] = None
    current_categories: Optional[int] = None
