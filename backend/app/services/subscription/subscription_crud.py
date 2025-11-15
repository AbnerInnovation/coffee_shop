"""
Subscription CRUD - Single Responsibility: Subscription Lifecycle Management

Handles all CRUD operations for subscriptions:
- Creating subscriptions (trial, paid)
- Retrieving subscriptions
- Updating subscriptions (upgrade, downgrade)
- Canceling subscriptions
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.models import (
    RestaurantSubscription,
    SubscriptionPlan,
    SubscriptionStatus,
    BillingCycle,
    PlanTier
)
from app.core.exceptions import ResourceNotFoundError, ValidationError, ConflictError

logger = logging.getLogger(__name__)


def get_restaurant_subscription(db: Session, restaurant_id: int) -> Optional[RestaurantSubscription]:
    """
    Get active or trial subscription for a restaurant.
    
    Args:
        db: Database session
        restaurant_id: ID of the restaurant
        
    Returns:
        Active or trial subscription, or None if not found
    """
    return db.query(RestaurantSubscription).filter(
        RestaurantSubscription.restaurant_id == restaurant_id,
        RestaurantSubscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIAL])
    ).first()


def create_trial_subscription(
    db: Session,
    restaurant_id: int,
    trial_days: int = 14
) -> RestaurantSubscription:
    """
    Create a trial subscription for a new restaurant.
    
    Args:
        db: Database session
        restaurant_id: ID of the restaurant
        trial_days: Number of trial days (14, 30, or 60)
        
    Returns:
        Created trial subscription
        
    Raises:
        ConflictError: If restaurant already has a subscription
        ValidationError: If trial plan not found
    """
    # Lazy import to avoid circular dependency
    from .plan_service import get_plan_by_tier
    
    # Check if restaurant already has a subscription
    existing = db.query(RestaurantSubscription).filter(
        RestaurantSubscription.restaurant_id == restaurant_id
    ).first()
    
    if existing:
        raise ConflictError("Restaurant already has a subscription")
    
    # Get trial plan
    trial_plan = get_plan_by_tier(db, PlanTier.TRIAL)
    if not trial_plan:
        raise ValidationError("Trial plan not found in system")
    
    # Calculate dates
    now = datetime.utcnow()
    trial_end = now + timedelta(days=trial_days)
    
    # Create subscription
    subscription = RestaurantSubscription(
        restaurant_id=restaurant_id,
        plan_id=trial_plan.id,
        status=SubscriptionStatus.TRIAL,
        billing_cycle=BillingCycle.MONTHLY,
        start_date=now,
        trial_end_date=trial_end,
        current_period_start=now,
        current_period_end=trial_end,
        base_price=0.0,
        total_price=0.0,
        auto_renew=True
    )
    
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    
    logger.info(f"Created trial subscription for restaurant {restaurant_id}")
    return subscription


def create_paid_subscription(
    db: Session,
    restaurant_id: int,
    plan_id: int,
    billing_cycle: BillingCycle = BillingCycle.MONTHLY,
    discount_code: Optional[str] = None
) -> RestaurantSubscription:
    """
    Create a paid subscription for a restaurant.
    
    Args:
        db: Database session
        restaurant_id: ID of the restaurant
        plan_id: ID of the subscription plan
        billing_cycle: Monthly or annual billing
        discount_code: Optional discount code
        
    Returns:
        Created subscription
        
    Raises:
        ResourceNotFoundError: If plan not found
    """
    # Lazy imports to avoid circular dependency
    from .plan_service import get_plan_by_id
    from .cost_calculator import calculate_subscription_cost, apply_discount
    
    # Get plan
    plan = get_plan_by_id(db, plan_id)
    
    # Calculate price
    base_price, total_price = calculate_subscription_cost(plan, billing_cycle, discount_code)
    
    # Calculate dates
    now = datetime.utcnow()
    if billing_cycle == BillingCycle.MONTHLY:
        period_end = now + timedelta(days=30)
    else:
        period_end = now + timedelta(days=365)
    
    # Create subscription
    subscription = RestaurantSubscription(
        restaurant_id=restaurant_id,
        plan_id=plan_id,
        status=SubscriptionStatus.ACTIVE,
        billing_cycle=billing_cycle,
        start_date=now,
        trial_end_date=None,
        current_period_start=now,
        current_period_end=period_end,
        base_price=base_price,
        total_price=total_price,
        discount_code=discount_code,
        auto_renew=True
    )
    
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    
    logger.info(f"Created paid subscription for restaurant {restaurant_id}")
    return subscription


def upgrade_subscription(
    db: Session,
    subscription_id: int,
    new_plan_id: int
) -> RestaurantSubscription:
    """
    Change subscription plan (handles both upgrades and downgrades with validation).
    
    Args:
        db: Database session
        subscription_id: ID of the subscription to upgrade
        new_plan_id: ID of the new plan
        
    Returns:
        Updated subscription
        
    Raises:
        ResourceNotFoundError: If subscription or plan not found
        ValidationError: If downgrade violates current usage limits
    """
    # Lazy imports to avoid circular dependency
    from .plan_service import get_plan_by_id
    from .limit_validator import validate_plan_limits
    
    subscription = db.query(RestaurantSubscription).filter(
        RestaurantSubscription.id == subscription_id
    ).first()
    
    if not subscription:
        raise ResourceNotFoundError("RestaurantSubscription", subscription_id)
    
    new_plan = get_plan_by_id(db, new_plan_id)
    old_plan = subscription.plan
    
    # Determine if it's an upgrade or downgrade
    tier_order = ["trial", "starter", "basic", "pro", "business", "enterprise"]
    old_tier_index = tier_order.index(old_plan.tier.value)
    new_tier_index = tier_order.index(new_plan.tier.value)
    
    is_downgrade = new_tier_index < old_tier_index
    
    # If downgrade, validate current usage
    if is_downgrade:
        violations = validate_plan_limits(db, subscription.restaurant_id, new_plan)
        
        if violations:
            error_msg = "No puedes cambiar a este plan porque excedes los siguientes límites:\n"
            error_msg += "\n".join(f"• {v}" for v in violations)
            error_msg += "\n\nPor favor elimina algunos recursos antes de cambiar de plan."
            raise ValidationError(error_msg)
    
    # Update subscription
    subscription.plan_id = new_plan_id
    
    # Recalculate price
    if subscription.billing_cycle == BillingCycle.ANNUAL and new_plan.annual_price:
        subscription.base_price = new_plan.annual_price
    else:
        subscription.base_price = new_plan.monthly_price
    
    subscription.total_price = subscription.calculate_total_cost()
    
    # If was trial, change to active
    if subscription.status == SubscriptionStatus.TRIAL:
        subscription.status = SubscriptionStatus.ACTIVE
        subscription.trial_end_date = None
    
    db.commit()
    db.refresh(subscription)
    
    logger.info(f"Upgraded subscription {subscription_id} to plan {new_plan_id}")
    return subscription


def downgrade_subscription(
    db: Session,
    subscription_id: int,
    new_plan_id: int
) -> RestaurantSubscription:
    """
    Schedule a downgrade to a lower tier (effective at end of current period).
    
    Args:
        db: Database session
        subscription_id: ID of the subscription
        new_plan_id: ID of the new (lower tier) plan
        
    Returns:
        Updated subscription with pending downgrade metadata
        
    Raises:
        ResourceNotFoundError: If subscription or plan not found
        ValidationError: If current usage exceeds new plan limits
    """
    # Lazy imports to avoid circular dependency
    from .plan_service import get_plan_by_id
    from .limit_validator import validate_plan_limits
    
    subscription = db.query(RestaurantSubscription).filter(
        RestaurantSubscription.id == subscription_id
    ).first()
    
    if not subscription:
        raise ResourceNotFoundError("RestaurantSubscription", subscription_id)
    
    new_plan = get_plan_by_id(db, new_plan_id)
    
    # Validate current usage against new plan limits
    violations = validate_plan_limits(db, subscription.restaurant_id, new_plan)
    
    if violations:
        error_msg = "No puedes cambiar a este plan porque excedes los siguientes límites:\n"
        error_msg += "\n".join(f"• {v}" for v in violations)
        error_msg += "\n\nPor favor elimina algunos recursos antes de cambiar de plan."
        raise ValidationError(error_msg)
    
    # Store downgrade info in metadata for processing at period end
    if not subscription.subscription_metadata:
        subscription.subscription_metadata = {}
    
    subscription.subscription_metadata['pending_downgrade'] = {
        'new_plan_id': new_plan_id,
        'scheduled_date': subscription.current_period_end.isoformat()
    }
    
    db.commit()
    db.refresh(subscription)
    
    logger.info(f"Scheduled downgrade for subscription {subscription_id} to plan {new_plan_id}")
    return subscription


def cancel_subscription(
    db: Session,
    subscription_id: int,
    immediate: bool = False
) -> RestaurantSubscription:
    """
    Cancel a subscription.
    
    Args:
        db: Database session
        subscription_id: ID of the subscription to cancel
        immediate: If True, cancel immediately; if False, cancel at period end
        
    Returns:
        Updated subscription
        
    Raises:
        ResourceNotFoundError: If subscription not found
    """
    subscription = db.query(RestaurantSubscription).filter(
        RestaurantSubscription.id == subscription_id
    ).first()
    
    if not subscription:
        raise ResourceNotFoundError("RestaurantSubscription", subscription_id)
    
    if immediate:
        subscription.status = SubscriptionStatus.CANCELLED
        subscription.cancelled_at = datetime.utcnow()
        subscription.current_period_end = datetime.utcnow()
        logger.info(f"Immediately cancelled subscription {subscription_id}")
    else:
        # Cancel at end of period
        subscription.auto_renew = False
        subscription.cancelled_at = datetime.utcnow()
        if not subscription.subscription_metadata:
            subscription.subscription_metadata = {}
        subscription.subscription_metadata['cancel_at_period_end'] = True
        logger.info(f"Scheduled cancellation for subscription {subscription_id} at period end")
    
    db.commit()
    db.refresh(subscription)
    
    return subscription


def reactivate_subscription(
    db: Session,
    subscription_id: int
) -> RestaurantSubscription:
    """
    Reactivate a cancelled subscription (only if not yet expired).
    
    Args:
        db: Database session
        subscription_id: ID of the subscription to reactivate
        
    Returns:
        Reactivated subscription
        
    Raises:
        ResourceNotFoundError: If subscription not found
        ValidationError: If subscription cannot be reactivated
    """
    subscription = db.query(RestaurantSubscription).filter(
        RestaurantSubscription.id == subscription_id
    ).first()
    
    if not subscription:
        raise ResourceNotFoundError("RestaurantSubscription", subscription_id)
    
    # Can only reactivate if current period hasn't ended
    if subscription.current_period_end < datetime.utcnow():
        raise ValidationError("Cannot reactivate expired subscription")
    
    # Reactivate
    subscription.status = SubscriptionStatus.ACTIVE
    subscription.auto_renew = True
    subscription.cancelled_at = None
    
    # Remove cancellation metadata
    if subscription.subscription_metadata and 'cancel_at_period_end' in subscription.subscription_metadata:
        del subscription.subscription_metadata['cancel_at_period_end']
    
    db.commit()
    db.refresh(subscription)
    
    logger.info(f"Reactivated subscription {subscription_id}")
    return subscription
