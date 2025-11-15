"""
Addon Service - Single Responsibility: Subscription Addon Management

Handles all operations related to subscription addons:
- Retrieving addons (all, by code, by plan)
- Adding/removing addons to subscriptions
- Addon availability checks
"""

from datetime import datetime
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.models import (
    SubscriptionAddon,
    RestaurantAddon,
    RestaurantSubscription
)
from app.core.exceptions import ResourceNotFoundError, ValidationError, ConflictError

logger = logging.getLogger(__name__)


def get_all_addons(db: Session, plan_tier: Optional[str] = None) -> List[SubscriptionAddon]:
    """
    Get all active addons, optionally filtered by plan availability.
    
    Args:
        db: Database session
        plan_tier: Optional plan tier to filter addons by availability
        
    Returns:
        List of active addons ordered by sort_order
    """
    addons = db.query(SubscriptionAddon).filter(
        SubscriptionAddon.is_active == True
    ).order_by(SubscriptionAddon.sort_order).all()
    
    if plan_tier:
        # Filter addons available for this plan
        return [addon for addon in addons if addon.is_available_for_plan(plan_tier)]
    
    return addons


def get_addon_by_code(db: Session, code: str) -> SubscriptionAddon:
    """
    Get an active addon by its unique code.
    
    Args:
        db: Database session
        code: Addon code (e.g., "EXTRA_TABLES", "KITCHEN_MODULE")
        
    Returns:
        Subscription addon
        
    Raises:
        ResourceNotFoundError: If addon not found
    """
    addon = db.query(SubscriptionAddon).filter(
        SubscriptionAddon.code == code,
        SubscriptionAddon.is_active == True
    ).first()
    if not addon:
        raise ResourceNotFoundError("SubscriptionAddon", code)
    return addon


def get_restaurant_addons(db: Session, restaurant_id: int) -> List[RestaurantAddon]:
    """
    Get all active addons for a restaurant.
    
    Args:
        db: Database session
        restaurant_id: ID of the restaurant
        
    Returns:
        List of restaurant addons with their subscription addon details
    """
    return db.query(RestaurantAddon).join(
        SubscriptionAddon
    ).filter(
        RestaurantAddon.restaurant_id == restaurant_id,
        RestaurantAddon.is_active == True
    ).all()


def add_addon_to_subscription(
    db: Session,
    subscription_id: int,
    addon_code: str
) -> RestaurantAddon:
    """
    Add an addon to a restaurant's subscription.
    
    Args:
        db: Database session
        subscription_id: ID of the restaurant subscription
        addon_code: Code of the addon to add
        
    Returns:
        Created restaurant addon
        
    Raises:
        ResourceNotFoundError: If subscription or addon not found
        ConflictError: If addon already exists for this subscription
        ValidationError: If addon not compatible with current plan
    """
    # Get subscription
    subscription = db.query(RestaurantSubscription).filter(
        RestaurantSubscription.id == subscription_id
    ).first()
    if not subscription:
        raise ResourceNotFoundError("RestaurantSubscription", subscription_id)
    
    # Get addon
    addon = get_addon_by_code(db, addon_code)
    
    # Check if addon is compatible with current plan
    if not addon.is_available_for_plan(subscription.plan.tier.value):
        raise ValidationError(
            f"Addon '{addon.display_name}' is not available for plan '{subscription.plan.display_name}'"
        )
    
    # Check if addon already exists
    existing = db.query(RestaurantAddon).filter(
        RestaurantAddon.subscription_id == subscription_id,
        RestaurantAddon.addon_id == addon.id,
        RestaurantAddon.is_active == True
    ).first()
    
    if existing:
        raise ConflictError(f"Addon '{addon.display_name}' is already active for this subscription")
    
    # Calculate addon price based on subscription billing cycle
    from .cost_calculator import calculate_addon_cost
    addon_price = calculate_addon_cost(addon, subscription.billing_cycle)
    
    # Create restaurant addon
    restaurant_addon = RestaurantAddon(
        subscription_id=subscription_id,
        restaurant_id=subscription.restaurant_id,
        addon_id=addon.id,
        price=addon_price,
        is_active=True,
        activated_at=datetime.utcnow()
    )
    
    db.add(restaurant_addon)
    
    # Update subscription total price
    subscription.total_price += addon_price
    
    db.commit()
    db.refresh(restaurant_addon)
    
    logger.info(f"Added addon '{addon_code}' to subscription {subscription_id}")
    return restaurant_addon


def remove_addon_from_subscription(
    db: Session,
    subscription_id: int,
    addon_code: str
) -> bool:
    """
    Remove an addon from a restaurant's subscription.
    
    Args:
        db: Database session
        subscription_id: ID of the restaurant subscription
        addon_code: Code of the addon to remove
        
    Returns:
        True if removed successfully
        
    Raises:
        ResourceNotFoundError: If addon not found for this subscription
    """
    # Get addon
    addon = get_addon_by_code(db, addon_code)
    
    # Find restaurant addon
    restaurant_addon = db.query(RestaurantAddon).filter(
        RestaurantAddon.subscription_id == subscription_id,
        RestaurantAddon.addon_id == addon.id,
        RestaurantAddon.is_active == True
    ).first()
    
    if not restaurant_addon:
        raise ResourceNotFoundError(
            "RestaurantAddon",
            f"subscription={subscription_id}, addon={addon_code}"
        )
    
    # Get subscription to update total price
    subscription = db.query(RestaurantSubscription).filter(
        RestaurantSubscription.id == subscription_id
    ).first()
    
    # Deactivate addon
    restaurant_addon.is_active = False
    restaurant_addon.deactivated_at = datetime.utcnow()
    
    # Update subscription total price
    if subscription:
        subscription.total_price -= restaurant_addon.price
    
    db.commit()
    
    logger.info(f"Removed addon '{addon_code}' from subscription {subscription_id}")
    return True


def get_available_addons_for_subscription(
    db: Session,
    subscription_id: int
) -> List[SubscriptionAddon]:
    """
    Get all addons available for a specific subscription based on its plan.
    Excludes addons already active for this subscription.
    
    Args:
        db: Database session
        subscription_id: ID of the restaurant subscription
        
    Returns:
        List of available addons
    """
    # Get subscription with plan
    subscription = db.query(RestaurantSubscription).filter(
        RestaurantSubscription.id == subscription_id
    ).first()
    if not subscription:
        raise ResourceNotFoundError("RestaurantSubscription", subscription_id)
    
    # Get all addons available for this plan tier
    available_addons = get_all_addons(db, plan_tier=subscription.plan.tier.value)
    
    # Get currently active addons for this subscription
    active_addon_ids = [
        ra.addon_id for ra in db.query(RestaurantAddon).filter(
            RestaurantAddon.subscription_id == subscription_id,
            RestaurantAddon.is_active == True
        ).all()
    ]
    
    # Filter out already active addons
    return [addon for addon in available_addons if addon.id not in active_addon_ids]
