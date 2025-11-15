"""
Plan Service - Single Responsibility: Subscription Plan Management

Handles all operations related to subscription plans:
- Retrieving plans (all, by tier, by ID)
- Filtering plans
- Plan availability checks
"""

from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.models import SubscriptionPlan, PlanTier
from app.core.exceptions import ResourceNotFoundError

logger = logging.getLogger(__name__)


def get_all_plans(db: Session, include_trial: bool = True) -> List[SubscriptionPlan]:
    """
    Get all active subscription plans.
    
    Args:
        db: Database session
        include_trial: Whether to include trial plans in results
        
    Returns:
        List of active subscription plans ordered by sort_order
    """
    query = db.query(SubscriptionPlan).filter(SubscriptionPlan.is_active == True)
    
    if not include_trial:
        query = query.filter(SubscriptionPlan.is_trial == False)
    
    return query.order_by(SubscriptionPlan.sort_order).all()


def get_plan_by_tier(db: Session, tier: PlanTier) -> Optional[SubscriptionPlan]:
    """
    Get an active plan by its tier level.
    
    Args:
        db: Database session
        tier: Plan tier (TRIAL, STARTER, PRO, BUSINESS, ENTERPRISE)
        
    Returns:
        Subscription plan or None if not found
    """
    return db.query(SubscriptionPlan).filter(
        SubscriptionPlan.tier == tier,
        SubscriptionPlan.is_active == True
    ).first()


def get_plan_by_id(db: Session, plan_id: int) -> SubscriptionPlan:
    """
    Get a subscription plan by ID.
    
    Args:
        db: Database session
        plan_id: ID of the plan
        
    Returns:
        Subscription plan
        
    Raises:
        ResourceNotFoundError: If plan not found
    """
    plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == plan_id).first()
    if not plan:
        raise ResourceNotFoundError("SubscriptionPlan", plan_id)
    return plan


def get_plans_by_price_range(
    db: Session,
    min_price: float,
    max_price: float,
    billing_cycle: str = "monthly"
) -> List[SubscriptionPlan]:
    """
    Get plans within a specific price range.
    
    Args:
        db: Database session
        min_price: Minimum price
        max_price: Maximum price
        billing_cycle: "monthly" or "annual"
        
    Returns:
        List of plans within the price range
    """
    query = db.query(SubscriptionPlan).filter(SubscriptionPlan.is_active == True)
    
    if billing_cycle == "annual":
        query = query.filter(
            SubscriptionPlan.annual_price >= min_price,
            SubscriptionPlan.annual_price <= max_price
        )
    else:
        query = query.filter(
            SubscriptionPlan.monthly_price >= min_price,
            SubscriptionPlan.monthly_price <= max_price
        )
    
    return query.order_by(SubscriptionPlan.sort_order).all()


def is_plan_available_for_restaurant(
    db: Session,
    plan_id: int,
    restaurant_id: int
) -> bool:
    """
    Check if a plan is available for a specific restaurant.
    Can be extended to include business logic like region restrictions, etc.
    
    Args:
        db: Database session
        plan_id: ID of the plan
        restaurant_id: ID of the restaurant
        
    Returns:
        True if plan is available, False otherwise
    """
    plan = get_plan_by_id(db, plan_id)
    
    # Basic check: plan must be active
    if not plan.is_active:
        return False
    
    # Trial plans are only for new restaurants
    if plan.is_trial:
        # Lazy import to avoid circular dependency
        from .subscription_crud import get_restaurant_subscription
        existing_subscription = get_restaurant_subscription(db, restaurant_id)
        # Trial only available if no subscription exists
        return existing_subscription is None
    
    return True
