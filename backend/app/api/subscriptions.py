"""
API endpoints for subscription management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.base import get_db
from app.services.subscription_service import SubscriptionService
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
    service = SubscriptionService(db)
    plans = service.get_all_plans(include_trial=include_trial)
    return plans


@router.get("/plans/{plan_id}", response_model=SubscriptionPlanResponse)
def get_plan(
    plan_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific subscription plan"""
    service = SubscriptionService(db)
    try:
        plan = service.get_plan_by_id(plan_id)
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
    service = SubscriptionService(db)
    addons = service.get_all_addons(plan_tier=plan_tier)
    return addons


@router.get("/addons/{addon_code}", response_model=SubscriptionAddonResponse)
def get_addon(
    addon_code: str,
    db: Session = Depends(get_db)
):
    """Get a specific add-on by code"""
    service = SubscriptionService(db)
    try:
        addon = service.get_addon_by_code(addon_code)
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
    service = SubscriptionService(db)
    try:
        subscription = service.create_trial_subscription(restaurant_id)
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
    service = SubscriptionService(db)
    try:
        subscription = service.create_paid_subscription(
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
    service = SubscriptionService(db)
    try:
        subscription = service.upgrade_subscription(subscription_id, data.new_plan_id)
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
    service = SubscriptionService(db)
    try:
        subscription = service.downgrade_subscription(subscription_id, data.new_plan_id)
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
    service = SubscriptionService(db)
    try:
        subscription = service.cancel_subscription(subscription_id, immediate=immediate)
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
    service = SubscriptionService(db)
    try:
        service.add_addon_to_subscription(
            subscription_id=subscription_id,
            addon_code=data.addon_code,
            quantity=data.quantity
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
    service = SubscriptionService(db)
    try:
        service.remove_addon_from_subscription(subscription_id, addon_code)
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
    service = SubscriptionService(db)
    limits = service.get_subscription_limits(restaurant_id)
    
    # TODO: Add current usage counts
    # For now, just return limits
    return SubscriptionLimitsResponse(**limits)


@router.post("/calculate-cost", response_model=CalculateCostResponse)
def calculate_cost(
    data: CalculateCostRequest,
    db: Session = Depends(get_db)
):
    """Calculate total subscription cost with addons and discounts"""
    service = SubscriptionService(db)
    try:
        cost = service.calculate_subscription_cost(
            plan_id=data.plan_id,
            billing_cycle=BillingCycle(data.billing_cycle.value),
            addon_codes=data.addons,
            discount_code=data.discount_code
        )
        return CalculateCostResponse(**cost)
    except (ResourceNotFoundError, ValidationError) as e:
        raise HTTPException(status_code=400, detail=str(e))
