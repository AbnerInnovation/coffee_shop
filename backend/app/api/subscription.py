"""
Subscription API endpoints for restaurant users.
Allows restaurants to view their subscription, usage, and upgrade options.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.db.base import get_db
from app.models import (
    User, Restaurant, RestaurantSubscription, SubscriptionPlan,
    MenuItem, Table, Category, SubscriptionStatus
)
from app.services.subscription_service import SubscriptionService
from app.api.deps import get_current_user, get_current_restaurant

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.get("/my-subscription")
def get_my_subscription(
    current_user: User = Depends(get_current_user),
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
):
    """Get current restaurant's subscription details"""
    
    subscription = db.query(RestaurantSubscription).filter(
        RestaurantSubscription.restaurant_id == restaurant.id,
        RestaurantSubscription.status.in_([SubscriptionStatus.TRIAL, SubscriptionStatus.ACTIVE])
    ).first()
    
    if not subscription:
        return {
            "has_subscription": False,
            "message": "No active subscription found"
        }
    
    return {
        "has_subscription": True,
        "subscription": {
            "id": subscription.id,
            "plan": {
                "id": subscription.plan.id,
                "name": subscription.plan.display_name,
                "tier": subscription.plan.tier.value,
                "is_trial": subscription.plan.is_trial
            },
            "status": subscription.status.value,
            "billing_cycle": subscription.billing_cycle.value,
            "total_price": subscription.total_price,
            "start_date": subscription.start_date.isoformat(),
            "current_period_end": subscription.current_period_end.isoformat() if subscription.current_period_end else None,
            "trial_end_date": subscription.trial_end_date.isoformat() if subscription.trial_end_date else None,
            "auto_renew": subscription.auto_renew,
            "days_until_renewal": subscription.days_until_renewal
        }
    }


@router.get("/usage")
def get_subscription_usage(
    current_user: User = Depends(get_current_user),
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
):
    """Get current usage vs limits for the restaurant"""
    
    # Check if restaurant has an active subscription
    subscription = db.query(RestaurantSubscription).filter(
        RestaurantSubscription.restaurant_id == restaurant.id,
        RestaurantSubscription.status.in_([SubscriptionStatus.TRIAL, SubscriptionStatus.ACTIVE])
    ).first()
    
    if not subscription:
        return {
            "has_subscription": False,
            "message": "No active subscription found. Please choose a plan to continue."
        }
    
    service = SubscriptionService(db)
    limits = service.get_subscription_limits(restaurant.id)
    
    # Get current usage
    usage = {
        "users": {
            "admin": db.query(User).filter(
                User.restaurant_id == restaurant.id,
                User.role == "admin",
                User.deleted_at.is_(None)
            ).count(),
            "waiter": db.query(User).filter(
                User.restaurant_id == restaurant.id,
                User.role == "waiter",
                User.deleted_at.is_(None)
            ).count(),
            "cashier": db.query(User).filter(
                User.restaurant_id == restaurant.id,
                User.role == "cashier",
                User.deleted_at.is_(None)
            ).count(),
            "kitchen": db.query(User).filter(
                User.restaurant_id == restaurant.id,
                User.role == "kitchen",
                User.deleted_at.is_(None)
            ).count(),
            "owner": db.query(User).filter(
                User.restaurant_id == restaurant.id,
                User.role == "owner",
                User.deleted_at.is_(None)
            ).count(),
        },
        "tables": db.query(Table).filter(
            Table.restaurant_id == restaurant.id,
            Table.deleted_at.is_(None)
        ).count(),
        "menu_items": db.query(MenuItem).filter(
            MenuItem.restaurant_id == restaurant.id,
            MenuItem.deleted_at.is_(None)
        ).count(),
        "categories": db.query(Category).filter(
            Category.restaurant_id == restaurant.id,
            Category.deleted_at.is_(None)
        ).count()
    }
    
    # Calculate percentages
    def calc_percentage(current: int, max_val: int) -> float:
        if max_val == -1:
            return 0  # Unlimited
        if max_val == 0:
            return 100
        return round((current / max_val) * 100, 1)
    
    return {
        "has_subscription": True,
        "limits": limits,
        "usage": usage,
        "percentages": {
            "admin_users": calc_percentage(usage["users"]["admin"], limits.get("max_admin_users", -1)),
            "waiter_users": calc_percentage(usage["users"]["waiter"], limits.get("max_waiter_users", -1)),
            "cashier_users": calc_percentage(usage["users"]["cashier"], limits.get("max_cashier_users", -1)),
            "kitchen_users": calc_percentage(usage["users"]["kitchen"], limits.get("max_kitchen_users", -1)),
            "owner_users": calc_percentage(usage["users"]["owner"], limits.get("max_owner_users", -1)),
            "tables": calc_percentage(usage["tables"], limits.get("max_tables", -1)),
            "menu_items": calc_percentage(usage["menu_items"], limits.get("max_menu_items", -1)),
            "categories": calc_percentage(usage["categories"], limits.get("max_categories", -1))
        }
    }


@router.get("/plans")
def get_available_plans(
    db: Session = Depends(get_db)
):
    """Get all available subscription plans"""
    service = SubscriptionService(db)
    plans = service.get_all_plans(include_trial=False)
    
    return [
        {
            "id": plan.id,
            "name": plan.display_name,
            "tier": plan.tier.value,
            "description": plan.description,
            "monthly_price": plan.monthly_price,
            "annual_price": plan.annual_price,
            "is_popular": plan.is_popular,
            "limits": {
                "max_admin_users": plan.max_admin_users,
                "max_waiter_users": plan.max_waiter_users,
                "max_cashier_users": plan.max_cashier_users,
                "max_kitchen_users": plan.max_kitchen_users,
                "max_owner_users": plan.max_owner_users,
                "max_tables": plan.max_tables,
                "max_menu_items": plan.max_menu_items,
                "max_categories": plan.max_categories
            },
            "features": {
                "has_kitchen_module": plan.has_kitchen_module,
                "has_ingredients_module": plan.has_ingredients_module,
                "has_inventory_module": plan.has_inventory_module,
                "has_advanced_reports": plan.has_advanced_reports,
                "has_multi_branch": plan.has_multi_branch,
                "has_priority_support": plan.has_priority_support
            }
        }
        for plan in plans
    ]


@router.get("/addons")
def get_available_addons(
    current_user: User = Depends(get_current_user),
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
):
    """Get available add-ons for current plan"""
    
    subscription = db.query(RestaurantSubscription).filter(
        RestaurantSubscription.restaurant_id == restaurant.id,
        RestaurantSubscription.status.in_([SubscriptionStatus.TRIAL, SubscriptionStatus.ACTIVE])
    ).first()
    
    if not subscription:
        return []
    
    service = SubscriptionService(db)
    plan_tier = subscription.plan.tier.value
    addons = service.get_all_addons(plan_tier=plan_tier)
    
    return [
        {
            "id": addon.id,
            "code": addon.code,
            "name": addon.display_name,
            "description": addon.description,
            "type": addon.addon_type.value,
            "category": addon.category.value,
            "monthly_price": addon.monthly_price,
            "is_recurring": addon.is_recurring,
            "is_quantifiable": addon.is_quantifiable,
            "min_quantity": addon.min_quantity,
            "max_quantity": addon.max_quantity,
            "is_featured": addon.is_featured
        }
        for addon in addons
    ]


@router.post("/upgrade")
def upgrade_subscription(
    plan_id: int,
    billing_cycle: str,
    current_user: User = Depends(get_current_user),
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
):
    """
    Upgrade or change subscription plan for the restaurant.
    Creates new subscription if none exists.
    Validates downgrade limits before allowing the change.
    """
    from app.services.subscription_service import SubscriptionService
    from app.core.exceptions import ValidationError, ResourceNotFoundError
    
    # Validate billing cycle
    if billing_cycle not in ['monthly', 'annual']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid billing cycle. Must be 'monthly' or 'annual'"
        )
    
    service = SubscriptionService(db)
    
    # Get ALL active/trial subscriptions for this restaurant
    existing_subscriptions = db.query(RestaurantSubscription).filter(
        RestaurantSubscription.restaurant_id == restaurant.id,
        RestaurantSubscription.status.in_([SubscriptionStatus.TRIAL, SubscriptionStatus.ACTIVE])
    ).all()
    
    try:
        if existing_subscriptions:
            # Use the most recent subscription
            existing_subscription = max(existing_subscriptions, key=lambda s: s.created_at)
            
            # Cancel all other subscriptions to avoid duplicates
            from datetime import datetime
            for sub in existing_subscriptions:
                if sub.id != existing_subscription.id:
                    sub.status = SubscriptionStatus.CANCELLED
                    sub.cancelled_at = datetime.utcnow()
            db.commit()
            # Use the service method which includes downgrade validation
            subscription = service.upgrade_subscription(
                existing_subscription.id,
                plan_id
            )
            
            # Update billing cycle if changed
            if subscription.billing_cycle != billing_cycle:
                subscription.billing_cycle = billing_cycle
                # Recalculate price
                new_plan = subscription.plan
                if billing_cycle == 'annual' and new_plan.annual_price:
                    subscription.base_price = new_plan.annual_price
                else:
                    subscription.base_price = new_plan.monthly_price
                subscription.total_price = subscription.calculate_total_cost()
                db.commit()
                db.refresh(subscription)
        else:
            # Create new subscription
            subscription = service.create_paid_subscription(
                restaurant_id=restaurant.id,
                plan_id=plan_id,
                billing_cycle=billing_cycle
            )
        
        return {
            "success": True,
            "message": "Suscripción actualizada exitosamente",
            "subscription": {
                "id": subscription.id,
                "plan_name": subscription.plan.display_name,
                "status": subscription.status.value,
                "billing_cycle": subscription.billing_cycle,
                "price": subscription.total_price,
                "current_period_end": subscription.current_period_end.isoformat()
            }
        }
    except ValidationError as e:
        # Return validation error with details (e.g., downgrade limits exceeded)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ResourceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
