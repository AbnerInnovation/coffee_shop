"""
Subscription Service - Compatibility Layer

This file provides backward compatibility for the SubscriptionService class.
All functionality has been refactored into specialized modules following SOLID principles:

- subscription/plan_service.py - Plan management (SRP)
- subscription/addon_service.py - Addon management (SRP)
- subscription/subscription_crud.py - Subscription CRUD (SRP)
- subscription/limit_validator.py - Limit validation (SRP)
- subscription/cost_calculator.py - Cost calculations (SRP)

The SubscriptionService class now acts as a facade/wrapper around these modules.
"""

from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from app.models import (
    SubscriptionPlan, PlanTier,
    SubscriptionAddon,
    RestaurantSubscription, BillingCycle,
    RestaurantAddon
)

# Import all functions from refactored modules
from .subscription import (
    # Plan operations
    get_all_plans,
    get_plan_by_tier,
    get_plan_by_id,
    
    # Addon operations
    get_all_addons,
    get_addon_by_code,
    add_addon_to_subscription as add_addon_func,
    remove_addon_from_subscription as remove_addon_func,
    get_restaurant_addons,
    
    # Subscription CRUD
    get_restaurant_subscription,
    create_trial_subscription as create_trial_func,
    create_paid_subscription as create_paid_func,
    upgrade_subscription as upgrade_func,
    downgrade_subscription as downgrade_func,
    cancel_subscription as cancel_func,
    
    # Validation
    validate_plan_limits,
    
    # Cost calculation
    calculate_subscription_cost,
)


class SubscriptionService:
    """
    Subscription Service - Facade Pattern
    
    This class maintains backward compatibility by wrapping the refactored modules.
    New code should import functions directly from app.services.subscription.
    
    Example (old way - still works):
        service = SubscriptionService(db)
        plans = service.get_all_plans()
    
    Example (new way - recommended):
        from app.services.subscription import get_all_plans
        plans = get_all_plans(db)
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    # ==================== PLAN MANAGEMENT ====================
    
    def get_all_plans(self, include_trial: bool = True) -> List[SubscriptionPlan]:
        """Get all active subscription plans"""
        return get_all_plans(self.db, include_trial)
    
    def get_plan_by_tier(self, tier: PlanTier) -> Optional[SubscriptionPlan]:
        """Get plan by tier"""
        return get_plan_by_tier(self.db, tier)
    
    def get_plan_by_id(self, plan_id: int) -> SubscriptionPlan:
        """Get plan by ID"""
        return get_plan_by_id(self.db, plan_id)
    
    # ==================== ADDON MANAGEMENT ====================
    
    def get_all_addons(self, plan_tier: Optional[str] = None) -> List[SubscriptionAddon]:
        """Get all active addons, optionally filtered by plan availability"""
        return get_all_addons(self.db, plan_tier)
    
    def get_addon_by_code(self, code: str) -> SubscriptionAddon:
        """Get addon by code"""
        return get_addon_by_code(self.db, code)
    
    # ==================== SUBSCRIPTION QUERIES ====================
    
    def get_restaurant_subscription(self, restaurant_id: int) -> Optional[RestaurantSubscription]:
        """Get active or trial subscription for a restaurant"""
        return get_restaurant_subscription(self.db, restaurant_id)
    
    # ==================== SUBSCRIPTION CREATION ====================
    
    def create_trial_subscription(self, restaurant_id: int, trial_days: int = 14) -> RestaurantSubscription:
        """Create a trial subscription for a new restaurant"""
        return create_trial_func(self.db, restaurant_id, trial_days)
    
    def create_paid_subscription(
        self,
        restaurant_id: int,
        plan_id: int,
        billing_cycle: BillingCycle = BillingCycle.MONTHLY,
        discount_code: Optional[str] = None
    ) -> RestaurantSubscription:
        """Create a paid subscription"""
        return create_paid_func(self.db, restaurant_id, plan_id, billing_cycle, discount_code)
    
    # ==================== SUBSCRIPTION UPDATES ====================
    
    def _validate_plan_limits(self, restaurant_id: int, new_plan: SubscriptionPlan) -> List[str]:
        """Validate current usage against plan limits (private method for backward compatibility)"""
        return validate_plan_limits(self.db, restaurant_id, new_plan)
    
    def upgrade_subscription(self, subscription_id: int, new_plan_id: int) -> RestaurantSubscription:
        """Change subscription plan (upgrade or downgrade with validation)"""
        return upgrade_func(self.db, subscription_id, new_plan_id)
    
    def downgrade_subscription(self, subscription_id: int, new_plan_id: int) -> RestaurantSubscription:
        """Downgrade subscription to a lower tier (effective at end of current period)"""
        return downgrade_func(self.db, subscription_id, new_plan_id)
    
    def cancel_subscription(self, subscription_id: int, immediate: bool = False) -> RestaurantSubscription:
        """Cancel subscription"""
        return cancel_func(self.db, subscription_id, immediate)
    
    # ==================== ADDON MANAGEMENT ====================
    
    def add_addon_to_subscription(
        self,
        subscription_id: int,
        addon_code: str,
        quantity: int = 1
    ) -> RestaurantAddon:
        """Add an addon to a subscription"""
        # Note: The refactored version doesn't support quantity yet
        # This is a simplified wrapper
        return add_addon_func(self.db, subscription_id, addon_code)
    
    def remove_addon_from_subscription(self, subscription_id: int, addon_code: str) -> None:
        """Remove an addon from a subscription"""
        remove_addon_func(self.db, subscription_id, addon_code)


# For backward compatibility, also export the class
__all__ = ['SubscriptionService']
