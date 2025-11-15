"""
Subscription Service Module

This module provides specialized services for subscription management:
- plan_service: Subscription plan operations (get, filter)
- addon_service: Addon management (get, filter by plan)
- subscription_crud: Subscription CRUD operations (create, update, cancel)
- limit_validator: Plan limit validation against current usage
- cost_calculator: Price and discount calculations
"""

from .plan_service import (
    get_all_plans,
    get_plan_by_tier,
    get_plan_by_id,
)

from .addon_service import (
    get_all_addons,
    get_addon_by_code,
    add_addon_to_subscription,
    remove_addon_from_subscription,
    get_restaurant_addons,
)

from .subscription_crud import (
    get_restaurant_subscription,
    create_trial_subscription,
    create_paid_subscription,
    upgrade_subscription,
    downgrade_subscription,
    cancel_subscription,
)

from .limit_validator import (
    validate_plan_limits,
    check_resource_limit,
)

from .cost_calculator import (
    calculate_subscription_cost,
    apply_discount,
    calculate_addon_cost,
)

__all__ = [
    # Plan operations
    'get_all_plans',
    'get_plan_by_tier',
    'get_plan_by_id',
    
    # Addon operations
    'get_all_addons',
    'get_addon_by_code',
    'add_addon_to_subscription',
    'remove_addon_from_subscription',
    'get_restaurant_addons',
    
    # Subscription CRUD
    'get_restaurant_subscription',
    'create_trial_subscription',
    'create_paid_subscription',
    'upgrade_subscription',
    'downgrade_subscription',
    'cancel_subscription',
    
    # Validation
    'validate_plan_limits',
    'check_resource_limit',
    
    # Cost calculation
    'calculate_subscription_cost',
    'apply_discount',
    'calculate_addon_cost',
]
