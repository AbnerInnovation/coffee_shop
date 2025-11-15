"""
API endpoints for subscription management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.base import get_db
# New modular imports - SOLID refactoring
from app.services.subscription import (
    get_all_plans as get_plans_func,
    get_plan_by_id,
    get_all_addons as get_addons_func,
    get_addon_by_code,
    get_restaurant_subscription as get_sub_func,
    create_trial_subscription as create_trial_func,
    create_paid_subscription as create_paid_func,
    upgrade_subscription as upgrade_func,
    downgrade_subscription as downgrade_func,
    cancel_subscription as cancel_func,
    add_addon_to_subscription,
    remove_addon_from_subscription,
)
from app.schemas.subscription import (
    SubscriptionPlanResponse,
    SubscriptionAddonResponse,
    RestaurantSubscriptionResponse,
    RestaurantSubscriptionCreate,
    UpgradeSubscriptionRequest,
    AddAddonRequest,
    RemoveAddonRequest,
    CalculateCostRequest,
    CalculateCostResponse,
    SubscriptionLimitsResponse
)
from app.core.exceptions import ResourceNotFoundError, ValidationError, ConflictError
from app.models import BillingCycle

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


# ==================== PLANS ====================

@router.get("/plans", response_model=List[SubscriptionPlanResponse])
def get_all_plans(
    include_trial: bool = True,
    db: Session = Depends(get_db)
):
    """Get all available subscription plans"""
    plans = get_plans_func(db, include_trial=include_trial)
    return plans


@router.get("/plans/{plan_id}", response_model=SubscriptionPlanResponse)
def get_plan(
    plan_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific subscription plan"""
    try:
        plan = get_plan_by_id(db, plan_id)
        return plan
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ==================== ADDONS ====================

@router.get("/addons", response_model=List[SubscriptionAddonResponse])
def get_all_addons(
    plan_tier: str = None,
    db: Session = Depends(get_db)
):
    """Get all available add-ons, optionally filtered by plan tier"""
    addons = get_addons_func(db, plan_tier=plan_tier)
    return addons


@router.get("/addons/{addon_code}", response_model=SubscriptionAddonResponse)
def get_addon(
    addon_code: str,
    db: Session = Depends(get_db)
):
    """Get a specific add-on by code"""
    try:
        addon = get_addon_by_code(db, addon_code)
        return addon
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ==================== RESTAURANT SUBSCRIPTIONS ====================

@router.post("/restaurants/{restaurant_id}/trial", response_model=RestaurantSubscriptionResponse)
def create_trial_subscription(
    restaurant_id: int,
    db: Session = Depends(get_db)
):
    """Create a trial subscription for a restaurant"""
    try:
        subscription = create_trial_func(db, restaurant_id)
        return subscription
    except (ValidationError, ConflictError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/restaurants/{restaurant_id}/subscribe", response_model=RestaurantSubscriptionResponse)
def create_paid_subscription(
    restaurant_id: int,
    data: RestaurantSubscriptionCreate,
    db: Session = Depends(get_db)
):
    """Create a paid subscription for a restaurant"""
    try:
        subscription = create_paid_func(
            db,
            restaurant_id=restaurant_id,
            plan_id=data.plan_id,
            billing_cycle=BillingCycle(data.billing_cycle.value),
            discount_code=data.discount_code
        )
        return subscription
    except (ResourceNotFoundError, ValidationError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/restaurants/{restaurant_id}/subscription", response_model=RestaurantSubscriptionResponse)
def get_restaurant_subscription(
    restaurant_id: int,
    db: Session = Depends(get_db)
):
    """Get current subscription for a restaurant"""
    from app.models import RestaurantSubscription, SubscriptionStatus
    
    subscription = db.query(RestaurantSubscription).filter(
        RestaurantSubscription.restaurant_id == restaurant_id,
        RestaurantSubscription.status.in_([SubscriptionStatus.TRIAL, SubscriptionStatus.ACTIVE])
    ).first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="No active subscription found")
    
    return subscription


@router.put("/subscriptions/{subscription_id}/upgrade", response_model=RestaurantSubscriptionResponse)
def upgrade_subscription(
    subscription_id: int,
    data: UpgradeSubscriptionRequest,
    db: Session = Depends(get_db)
):
    """Upgrade subscription to a higher tier"""
    try:
        subscription = upgrade_func(db, subscription_id, data.new_plan_id)
        return subscription
    except (ResourceNotFoundError, ValidationError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/subscriptions/{subscription_id}/downgrade", response_model=RestaurantSubscriptionResponse)
def downgrade_subscription(
    subscription_id: int,
    data: UpgradeSubscriptionRequest,
    db: Session = Depends(get_db)
):
    """Downgrade subscription (effective at end of current period)"""
    try:
        subscription = downgrade_func(db, subscription_id, data.new_plan_id)
        return subscription
    except (ResourceNotFoundError, ValidationError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/subscriptions/{subscription_id}/cancel", response_model=RestaurantSubscriptionResponse)
def cancel_subscription(
    subscription_id: int,
    immediate: bool = False,
    db: Session = Depends(get_db)
):
    """Cancel subscription"""
    try:
        subscription = cancel_func(db, subscription_id, immediate=immediate)
        return subscription
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ==================== ADDON MANAGEMENT ====================

@router.post("/subscriptions/{subscription_id}/addons", response_model=RestaurantSubscriptionResponse)
def add_addon(
    subscription_id: int,
    data: AddAddonRequest,
    db: Session = Depends(get_db)
):
    """Add an addon to a subscription"""
    try:
        add_addon_to_subscription(
            db,
            subscription_id=subscription_id,
            addon_code=data.addon_code
        )
        # Return updated subscription
        from app.models import RestaurantSubscription
        subscription = db.query(RestaurantSubscription).filter(
            RestaurantSubscription.id == subscription_id
        ).first()
        return subscription
    except (ResourceNotFoundError, ValidationError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/subscriptions/{subscription_id}/addons/{addon_code}")
def remove_addon(
    subscription_id: int,
    addon_code: str,
    db: Session = Depends(get_db)
):
    """Remove an addon from a subscription"""
    try:
        remove_addon_from_subscription(db, subscription_id, addon_code)
        return {"message": "Addon removed successfully"}
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ==================== LIMITS & CALCULATIONS ====================

@router.get("/restaurants/{restaurant_id}/limits", response_model=SubscriptionLimitsResponse)
def get_subscription_limits(
    restaurant_id: int,
    db: Session = Depends(get_db)
):
    """Get subscription limits for a restaurant"""
    subscription = get_sub_func(db, restaurant_id)
    
    if not subscription or not subscription.plan:
        raise HTTPException(status_code=404, detail="No active subscription found")
    
    plan = subscription.plan
    limits = {
        'max_admin_users': plan.max_admin_users,
        'max_waiter_users': plan.max_waiter_users,
        'max_cashier_users': plan.max_cashier_users,
        'max_kitchen_users': plan.max_kitchen_users,
        'max_owner_users': plan.max_owner_users,
        'max_tables': plan.max_tables,
        'max_menu_items': plan.max_menu_items,
        'max_categories': plan.max_categories,
        'has_kitchen_module': plan.has_kitchen_module,
        'has_ingredients_module': plan.has_ingredients_module,
        'has_inventory_module': plan.has_inventory_module,
        'has_advanced_reports': plan.has_advanced_reports,
        'has_multi_branch': plan.has_multi_branch
    }
    
    return SubscriptionLimitsResponse(**limits)


@router.post("/calculate-cost", response_model=CalculateCostResponse)
def calculate_cost(
    data: CalculateCostRequest,
    db: Session = Depends(get_db)
):
    """Calculate total subscription cost with addons and discounts"""
    from app.services.subscription.cost_calculator import calculate_subscription_cost as calc_cost
    
    try:
        plan = get_plan_by_id(db, data.plan_id)
        billing_cycle_enum = BillingCycle(data.billing_cycle.value)
        
        base_price, total_price = calc_cost(plan, billing_cycle_enum, data.discount_code)
        
        # TODO: Add addon costs calculation
        # For now, return base cost
        return CalculateCostResponse(
            base_price=base_price,
            total_price=total_price,
            discount_amount=base_price - total_price if base_price > total_price else 0
        )
    except (ResourceNotFoundError, ValidationError) as e:
        raise HTTPException(status_code=400, detail=str(e))
