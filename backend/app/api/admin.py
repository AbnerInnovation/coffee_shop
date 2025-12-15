"""
API endpoints for SysAdmin restaurant and subscription management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime

from app.db.base import get_db
from app.models import Restaurant, User, RestaurantSubscription, SubscriptionPlan
from app.models.user import UserRole
from app.models.restaurant_subscription import SubscriptionStatus
from app.core.exceptions import UnauthorizedError, ResourceNotFoundError
from app.services.subscription_service import SubscriptionService
from app.schemas.subscription import (
    RestaurantSubscriptionResponse,
    RestaurantSubscriptionCreate,
    UpgradeSubscriptionRequest
)
from pydantic import BaseModel

router = APIRouter(prefix="/admin", tags=["admin"])


# ==================== SCHEMAS ====================

class RestaurantWithSubscription(BaseModel):
    """Restaurant with subscription details"""
    id: int
    name: str
    subdomain: str
    email: Optional[str]
    phone: Optional[str]
    is_active: bool
    created_at: datetime
    
    # Subscription info (nullable if no subscription)
    subscription_id: Optional[int] = None
    plan_name: Optional[str] = None
    plan_tier: Optional[str] = None
    subscription_status: Optional[str] = None
    monthly_price: Optional[float] = None
    trial_end_date: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    days_until_renewal: Optional[int] = None
    is_trial: Optional[bool] = None
    
    class Config:
        from_attributes = True


class AdminStats(BaseModel):
    """System-wide statistics"""
    total_restaurants: int
    restaurants_with_subscription: int
    restaurants_without_subscription: int
    
    total_subscriptions: int
    active_subscriptions: int
    trial_subscriptions: int
    cancelled_subscriptions: int
    expired_subscriptions: int
    
    total_monthly_revenue: float
    total_annual_revenue: float
    
    plans_distribution: dict  # {plan_name: count}


# ==================== DEPENDENCIES ====================

def get_current_sysadmin(
    current_user: User = Depends(lambda: None)  # Replace with your auth dependency
) -> User:
    """Verify current user is SysAdmin"""
    # TODO: Replace with actual authentication
    # For now, this is a placeholder
    # You should use your existing auth system here
    
    if not current_user or current_user.role != UserRole.SYSADMIN:
        raise UnauthorizedError("SysAdmin access required")
    
    return current_user


# ==================== ENDPOINTS ====================

@router.get("/stats", response_model=AdminStats)
def get_system_stats(
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_sysadmin)  # Uncomment when auth is ready
):
    """Get system-wide statistics (SysAdmin only)"""
    
    # Count restaurants
    total_restaurants = db.query(func.count(Restaurant.id)).scalar()
    
    # Count subscriptions
    total_subscriptions = db.query(func.count(RestaurantSubscription.id)).scalar()
    restaurants_with_sub = db.query(
        func.count(func.distinct(RestaurantSubscription.restaurant_id))
    ).scalar()
    
    # Count by status (count unique restaurants, not subscriptions)
    active_subs = db.query(func.count(func.distinct(RestaurantSubscription.restaurant_id))).filter(
        RestaurantSubscription.status == SubscriptionStatus.ACTIVE
    ).scalar()
    
    trial_subs = db.query(func.count(func.distinct(RestaurantSubscription.restaurant_id))).filter(
        RestaurantSubscription.status == SubscriptionStatus.TRIAL
    ).scalar()
    
    cancelled_subs = db.query(func.count(func.distinct(RestaurantSubscription.restaurant_id))).filter(
        RestaurantSubscription.status == SubscriptionStatus.CANCELLED
    ).scalar()
    
    expired_subs = db.query(func.count(func.distinct(RestaurantSubscription.restaurant_id))).filter(
        RestaurantSubscription.status == SubscriptionStatus.EXPIRED
    ).scalar()
    
    # Calculate revenue
    total_monthly = db.query(func.sum(RestaurantSubscription.total_price)).filter(
        RestaurantSubscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIAL])
    ).scalar() or 0.0
    
    # Plans distribution (count unique restaurants per plan)
    plans_dist = {}
    plan_counts = db.query(
        SubscriptionPlan.display_name,
        func.count(func.distinct(RestaurantSubscription.restaurant_id))
    ).join(
        RestaurantSubscription
    ).filter(
        RestaurantSubscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIAL])
    ).group_by(
        SubscriptionPlan.display_name
    ).all()
    
    for plan_name, count in plan_counts:
        plans_dist[plan_name] = count
    
    return AdminStats(
        total_restaurants=total_restaurants,
        restaurants_with_subscription=restaurants_with_sub,
        restaurants_without_subscription=total_restaurants - restaurants_with_sub,
        total_subscriptions=total_subscriptions,
        active_subscriptions=active_subs,
        trial_subscriptions=trial_subs,
        cancelled_subscriptions=cancelled_subs,
        expired_subscriptions=expired_subs,
        total_monthly_revenue=total_monthly,
        total_annual_revenue=total_monthly * 12,
        plans_distribution=plans_dist
    )


@router.get("/restaurants", response_model=List[RestaurantWithSubscription])
def list_all_restaurants(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    has_subscription: Optional[bool] = None,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_sysadmin)  # Uncomment when auth is ready
):
    """List all restaurants with subscription info (SysAdmin only)"""
    
    # Subquery to get the most recent subscription for each restaurant
    latest_subscription_subquery = db.query(
        RestaurantSubscription.restaurant_id,
        func.max(RestaurantSubscription.id).label('max_id')
    ).group_by(RestaurantSubscription.restaurant_id).subquery()
    
    query = db.query(
        Restaurant.id,
        Restaurant.name,
        Restaurant.subdomain,
        Restaurant.email,
        Restaurant.phone,
        Restaurant.is_active,
        Restaurant.created_at,
        RestaurantSubscription.id.label('subscription_id'),
        SubscriptionPlan.display_name.label('plan_name'),
        SubscriptionPlan.tier.label('plan_tier'),
        RestaurantSubscription.status.label('subscription_status'),
        RestaurantSubscription.total_price.label('monthly_price'),
        RestaurantSubscription.trial_end_date,
        RestaurantSubscription.current_period_end,
        SubscriptionPlan.is_trial
    ).outerjoin(
        latest_subscription_subquery,
        Restaurant.id == latest_subscription_subquery.c.restaurant_id
    ).outerjoin(
        RestaurantSubscription,
        RestaurantSubscription.id == latest_subscription_subquery.c.max_id
    ).outerjoin(
        SubscriptionPlan,
        RestaurantSubscription.plan_id == SubscriptionPlan.id
    ).filter(
        Restaurant.deleted_at.is_(None)  # Only show non-deleted restaurants
    )
    
    # Apply filters
    if search:
        query = query.filter(
            (Restaurant.name.ilike(f"%{search}%")) |
            (Restaurant.subdomain.ilike(f"%{search}%")) |
            (Restaurant.email.ilike(f"%{search}%"))
        )
    
    if has_subscription is not None:
        if has_subscription:
            query = query.filter(RestaurantSubscription.id.isnot(None))
        else:
            query = query.filter(RestaurantSubscription.id.is_(None))
    
    results = query.offset(skip).limit(limit).all()
    
    # Update subscription status for all subscriptions before returning
    subscription_ids = [row.subscription_id for row in results if row.subscription_id]
    if subscription_ids:
        subscriptions = db.query(RestaurantSubscription).filter(
            RestaurantSubscription.id.in_(subscription_ids)
        ).all()
        for sub in subscriptions:
            sub.update_status(db)
    
    # Re-fetch results after status updates
    results = query.offset(skip).limit(limit).all()
    
    # Convert to response model
    restaurants = []
    for row in results:
        # Calculate days until renewal
        days_until_renewal = None
        if row.current_period_end and row.subscription_status:
            # Only calculate for active/trial subscriptions
            if row.subscription_status in ['active', 'trial', 'past_due', 'pending_payment']:
                delta = row.current_period_end - datetime.utcnow()
                # Only show positive days, if negative it means expired
                days_until_renewal = max(0, delta.days)
            # For expired/cancelled subscriptions, don't show days
        
        restaurants.append(RestaurantWithSubscription(
            id=row.id,
            name=row.name,
            subdomain=row.subdomain,
            email=row.email,
            phone=row.phone,
            is_active=row.is_active,
            created_at=row.created_at,
            subscription_id=row.subscription_id,
            plan_name=row.plan_name,
            plan_tier=row.plan_tier,
            subscription_status=row.subscription_status,
            monthly_price=row.monthly_price,
            trial_end_date=row.trial_end_date,
            current_period_end=row.current_period_end,
            days_until_renewal=days_until_renewal,
            is_trial=row.is_trial
        ))
    
    return restaurants


@router.get("/restaurants/{restaurant_id}/subscription", response_model=RestaurantSubscriptionResponse)
def get_restaurant_subscription(
    restaurant_id: int,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_sysadmin)  # Uncomment when auth is ready
):
    """Get detailed subscription info for a restaurant (SysAdmin only)"""
    
    service = SubscriptionService(db)
    subscription = service.get_restaurant_subscription(restaurant_id)
    
    if not subscription:
        raise ResourceNotFoundError("Subscription", restaurant_id)
    
    return subscription


@router.post("/restaurants/{restaurant_id}/subscription", response_model=RestaurantSubscriptionResponse)
def create_or_update_restaurant_subscription(
    restaurant_id: int,
    subscription_data: RestaurantSubscriptionCreate,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_sysadmin)  # Uncomment when auth is ready
):
    """Create or update a subscription for a restaurant (SysAdmin only)"""
    
    # Verify restaurant exists
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise ResourceNotFoundError("Restaurant", restaurant_id)
    
    # Check if already has subscription
    existing = db.query(RestaurantSubscription).filter(
        RestaurantSubscription.restaurant_id == restaurant_id
    ).first()
    
    service = SubscriptionService(db)
    
    if existing:
        # Update existing subscription (upgrade/change plan)
        subscription = service.upgrade_subscription(
            subscription_id=existing.id,
            new_plan_id=subscription_data.plan_id
        )
        # Update billing cycle if provided
        if subscription_data.billing_cycle:
            existing.billing_cycle = subscription_data.billing_cycle
            db.commit()
            db.refresh(existing)
    else:
        # Create new subscription
        subscription = service.create_paid_subscription(
            restaurant_id=restaurant_id,
            plan_id=subscription_data.plan_id,
            billing_cycle=subscription_data.billing_cycle or BillingCycle.MONTHLY
        )
    
    return subscription


@router.put("/restaurants/{restaurant_id}/subscription/upgrade", response_model=RestaurantSubscriptionResponse)
def upgrade_restaurant_subscription(
    restaurant_id: int,
    upgrade_data: UpgradeSubscriptionRequest,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_sysadmin)  # Uncomment when auth is ready
):
    """Upgrade/change a restaurant's subscription plan (SysAdmin only)"""
    
    # Get current subscription
    subscription = db.query(RestaurantSubscription).filter(
        RestaurantSubscription.restaurant_id == restaurant_id
    ).first()
    
    if not subscription:
        raise ResourceNotFoundError("Subscription", restaurant_id)
    
    service = SubscriptionService(db)
    updated_subscription = service.upgrade_subscription(
        subscription.id,
        upgrade_data.new_plan_id
    )
    
    return updated_subscription


@router.delete("/restaurants/{restaurant_id}/subscription")
def cancel_restaurant_subscription(
    restaurant_id: int,
    immediate: bool = False,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_sysadmin)  # Uncomment when auth is ready
):
    """Cancel a restaurant's subscription (SysAdmin only)"""
    
    # Get current subscription
    subscription = db.query(RestaurantSubscription).filter(
        RestaurantSubscription.restaurant_id == restaurant_id
    ).first()
    
    if not subscription:
        raise ResourceNotFoundError("Subscription", restaurant_id)
    
    service = SubscriptionService(db)
    cancelled_subscription = service.cancel_subscription(subscription.id, immediate)
    
    return {
        "success": True,
        "message": f"Subscription cancelled {'immediately' if immediate else 'at end of period'}",
        "subscription": cancelled_subscription
    }


@router.post("/restaurants/{restaurant_id}/subscription/renew", response_model=RestaurantSubscriptionResponse)
def renew_restaurant_subscription(
    restaurant_id: int,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_sysadmin)  # Uncomment when auth is ready
):
    """Renew an expired or cancelled subscription (SysAdmin only)"""
    
    # Get current subscription (including expired/cancelled)
    subscription = db.query(RestaurantSubscription).filter(
        RestaurantSubscription.restaurant_id == restaurant_id
    ).first()
    
    if not subscription:
        raise ResourceNotFoundError("Subscription", restaurant_id)
    
    # Verify it's expired or cancelled
    if subscription.status not in [SubscriptionStatus.EXPIRED, SubscriptionStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot renew subscription with status: {subscription.status.value}. Only expired or cancelled subscriptions can be renewed."
        )
    
    service = SubscriptionService(db)
    renewed_subscription = service.renew_subscription(subscription.id)
    
    return renewed_subscription
