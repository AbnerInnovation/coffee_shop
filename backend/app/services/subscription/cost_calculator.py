"""
Cost Calculator - Single Responsibility: Price and Discount Calculations

Handles all financial calculations for subscriptions:
- Subscription cost calculation
- Discount application
- Addon cost calculation
- Proration calculations
"""

from datetime import datetime
from typing import Optional, Tuple
import logging

from app.models import (
    SubscriptionPlan,
    SubscriptionAddon,
    RestaurantSubscription,
    BillingCycle
)

logger = logging.getLogger(__name__)


def calculate_subscription_cost(
    plan: SubscriptionPlan,
    billing_cycle: BillingCycle,
    discount_code: Optional[str] = None
) -> Tuple[float, float]:
    """
    Calculate subscription cost based on plan and billing cycle.
    
    Args:
        plan: Subscription plan
        billing_cycle: Monthly or annual billing
        discount_code: Optional discount code
        
    Returns:
        Tuple of (base_price, total_price_after_discount)
    """
    # Get base price based on billing cycle
    if billing_cycle == BillingCycle.ANNUAL and plan.annual_price:
        base_price = plan.annual_price
    else:
        base_price = plan.monthly_price
    
    # Apply discount if provided
    if discount_code:
        total_price = apply_discount(base_price, discount_code)
    else:
        total_price = base_price
    
    return (base_price, total_price)


def apply_discount(base_price: float, discount_code: str) -> float:
    """
    Apply a discount code to a base price.
    
    Args:
        base_price: Original price before discount
        discount_code: Discount code to apply
        
    Returns:
        Price after discount
        
    Note:
        This is a simplified implementation. In production, you would:
        - Validate discount code against a database
        - Check expiration dates
        - Check usage limits
        - Support percentage and fixed amount discounts
    """
    # TODO: Implement proper discount code validation and application
    # For now, return base price unchanged
    logger.warning(f"Discount code '{discount_code}' not implemented yet")
    return base_price


def calculate_addon_cost(
    addon: SubscriptionAddon,
    billing_cycle: BillingCycle
) -> float:
    """
    Calculate addon cost based on billing cycle.
    
    Args:
        addon: Subscription addon
        billing_cycle: Monthly or annual billing
        
    Returns:
        Addon price for the billing cycle
    """
    if billing_cycle == BillingCycle.ANNUAL and addon.annual_price:
        return addon.annual_price
    return addon.monthly_price


def calculate_prorated_cost(
    old_price: float,
    new_price: float,
    days_remaining: int,
    total_days: int
) -> float:
    """
    Calculate prorated cost for plan changes mid-cycle.
    
    Args:
        old_price: Current plan price
        new_price: New plan price
        days_remaining: Days remaining in current billing period
        total_days: Total days in billing period
        
    Returns:
        Prorated amount to charge/credit
        
    Example:
        If upgrading from $10/month to $20/month with 15 days remaining in a 30-day period:
        - Unused credit: $10 * (15/30) = $5
        - New cost: $20 * (15/30) = $10
        - Amount to charge: $10 - $5 = $5
    """
    if total_days == 0:
        return 0.0
    
    # Calculate unused portion of old plan
    unused_credit = old_price * (days_remaining / total_days)
    
    # Calculate cost for new plan for remaining period
    new_cost = new_price * (days_remaining / total_days)
    
    # Return the difference (positive = charge, negative = credit)
    return new_cost - unused_credit


def calculate_upgrade_cost(
    current_subscription: RestaurantSubscription,
    new_plan: SubscriptionPlan
) -> Tuple[float, float, float]:
    """
    Calculate costs for upgrading a subscription.
    
    Args:
        current_subscription: Current active subscription
        new_plan: Plan to upgrade to
        
    Returns:
        Tuple of (prorated_credit, new_plan_cost, total_due)
    """
    # Calculate days remaining in current period
    now = datetime.utcnow()
    days_remaining = (current_subscription.current_period_end - now).days
    
    # Calculate total days in billing period
    if current_subscription.billing_cycle == BillingCycle.MONTHLY:
        total_days = 30
    else:
        total_days = 365
    
    # Get new plan price
    _, new_price = calculate_subscription_cost(new_plan, current_subscription.billing_cycle)
    
    # Calculate prorated amount
    prorated_amount = calculate_prorated_cost(
        current_subscription.total_price,
        new_price,
        days_remaining,
        total_days
    )
    
    # Calculate credit from unused portion of old plan
    prorated_credit = current_subscription.total_price * (days_remaining / total_days)
    
    # Calculate cost for new plan for remaining period
    new_plan_cost = new_price * (days_remaining / total_days)
    
    # Total due is the difference
    total_due = max(0, prorated_amount)
    
    return (prorated_credit, new_plan_cost, total_due)


def calculate_total_subscription_cost(
    subscription: RestaurantSubscription
) -> float:
    """
    Calculate total cost including base plan and all active addons.
    
    Args:
        subscription: Restaurant subscription with addons
        
    Returns:
        Total monthly or annual cost
    """
    total = subscription.base_price
    
    # Add addon costs
    if hasattr(subscription, 'restaurant_addons'):
        for addon in subscription.restaurant_addons:
            if addon.is_active:
                total += addon.price
    
    return total


def calculate_annual_savings(plan: SubscriptionPlan) -> float:
    """
    Calculate savings when choosing annual billing vs monthly.
    
    Args:
        plan: Subscription plan
        
    Returns:
        Amount saved per year (positive number)
    """
    if not plan.annual_price:
        return 0.0
    
    monthly_cost_per_year = plan.monthly_price * 12
    annual_cost = plan.annual_price
    
    return max(0, monthly_cost_per_year - annual_cost)


def calculate_savings_percentage(plan: SubscriptionPlan) -> float:
    """
    Calculate percentage saved with annual billing.
    
    Args:
        plan: Subscription plan
        
    Returns:
        Percentage saved (e.g., 20.0 for 20%)
    """
    savings = calculate_annual_savings(plan)
    if savings == 0:
        return 0.0
    
    monthly_cost_per_year = plan.monthly_price * 12
    if monthly_cost_per_year == 0:
        return 0.0
    
    return (savings / monthly_cost_per_year) * 100
