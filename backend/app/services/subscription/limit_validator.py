"""
Limit Validator - Single Responsibility: Plan Limit Validation

Handles all validation logic for subscription plan limits:
- Validating current usage against plan limits
- Checking individual resource limits
- Generating violation messages
"""

from sqlalchemy.orm import Session
from typing import List, Dict, Tuple
import logging

from app.models import (
    SubscriptionPlan,
    User, Table, MenuItem, Category
)

logger = logging.getLogger(__name__)


def validate_plan_limits(
    db: Session,
    restaurant_id: int,
    new_plan: SubscriptionPlan
) -> List[str]:
    """
    Validate current restaurant usage against a plan's limits.
    
    Args:
        db: Database session
        restaurant_id: ID of the restaurant to validate
        new_plan: The plan to validate against
        
    Returns:
        List of violation messages (empty if no violations)
    """
    violations = []
    
    # Check tables
    table_violation = _check_table_limit(db, restaurant_id, new_plan)
    if table_violation:
        violations.append(table_violation)
    
    # Check menu items
    menu_violation = _check_menu_item_limit(db, restaurant_id, new_plan)
    if menu_violation:
        violations.append(menu_violation)
    
    # Check categories
    category_violation = _check_category_limit(db, restaurant_id, new_plan)
    if category_violation:
        violations.append(category_violation)
    
    # Check users by role
    user_violations = _check_user_limits(db, restaurant_id, new_plan)
    violations.extend(user_violations)
    
    return violations


def check_resource_limit(
    db: Session,
    restaurant_id: int,
    resource_type: str,
    plan: SubscriptionPlan
) -> Tuple[bool, str]:
    """
    Check if a specific resource type is within plan limits.
    
    Args:
        db: Database session
        restaurant_id: ID of the restaurant
        resource_type: Type of resource ("tables", "menu_items", "categories", "users")
        plan: Subscription plan to check against
        
    Returns:
        Tuple of (is_within_limit, message)
    """
    if resource_type == "tables":
        violation = _check_table_limit(db, restaurant_id, plan)
        return (violation is None, violation or "")
    
    elif resource_type == "menu_items":
        violation = _check_menu_item_limit(db, restaurant_id, plan)
        return (violation is None, violation or "")
    
    elif resource_type == "categories":
        violation = _check_category_limit(db, restaurant_id, plan)
        return (violation is None, violation or "")
    
    elif resource_type.startswith("users_"):
        role = resource_type.replace("users_", "")
        violations = _check_user_limits(db, restaurant_id, plan, specific_role=role)
        return (len(violations) == 0, violations[0] if violations else "")
    
    return (True, "")


def get_current_usage(db: Session, restaurant_id: int) -> Dict[str, int]:
    """
    Get current resource usage for a restaurant.
    
    Args:
        db: Database session
        restaurant_id: ID of the restaurant
        
    Returns:
        Dictionary with current usage counts
    """
    usage = {}
    
    # Tables
    usage['tables'] = db.query(Table).filter(
        Table.restaurant_id == restaurant_id,
        Table.deleted_at.is_(None)
    ).count()
    
    # Menu items
    usage['menu_items'] = db.query(MenuItem).filter(
        MenuItem.restaurant_id == restaurant_id,
        MenuItem.deleted_at.is_(None)
    ).count()
    
    # Categories
    usage['categories'] = db.query(Category).filter(
        Category.restaurant_id == restaurant_id,
        Category.deleted_at.is_(None)
    ).count()
    
    # Users by role/staff_type
    # Admin users
    usage['users_admin'] = db.query(User).filter(
        User.restaurant_id == restaurant_id,
        User.role == 'admin',
        User.deleted_at.is_(None)
    ).count()
    
    # Staff users by staff_type
    usage['users_waiter'] = db.query(User).filter(
        User.restaurant_id == restaurant_id,
        User.role == 'staff',
        User.staff_type == 'waiter',
        User.deleted_at.is_(None)
    ).count()
    
    usage['users_cashier'] = db.query(User).filter(
        User.restaurant_id == restaurant_id,
        User.role == 'staff',
        User.staff_type == 'cashier',
        User.deleted_at.is_(None)
    ).count()
    
    usage['users_kitchen'] = db.query(User).filter(
        User.restaurant_id == restaurant_id,
        User.role == 'staff',
        User.staff_type == 'kitchen',
        User.deleted_at.is_(None)
    ).count()
    
    # Owner users
    usage['users_owner'] = db.query(User).filter(
        User.restaurant_id == restaurant_id,
        User.role == 'owner',
        User.deleted_at.is_(None)
    ).count()
    
    return usage


# ==================== PRIVATE HELPER FUNCTIONS ====================


def _check_table_limit(
    db: Session,
    restaurant_id: int,
    plan: SubscriptionPlan
) -> str | None:
    """Check table limit. Returns violation message or None."""
    current_tables = db.query(Table).filter(
        Table.restaurant_id == restaurant_id,
        Table.deleted_at.is_(None)
    ).count()
    
    if plan.max_tables != -1 and current_tables > plan.max_tables:
        return (
            f"Tienes {current_tables} mesas pero el plan {plan.display_name} "
            f"solo permite {plan.max_tables}"
        )
    return None


def _check_menu_item_limit(
    db: Session,
    restaurant_id: int,
    plan: SubscriptionPlan
) -> str | None:
    """Check menu item limit. Returns violation message or None."""
    current_items = db.query(MenuItem).filter(
        MenuItem.restaurant_id == restaurant_id,
        MenuItem.deleted_at.is_(None)
    ).count()
    
    if plan.max_menu_items != -1 and current_items > plan.max_menu_items:
        return (
            f"Tienes {current_items} productos pero el plan {plan.display_name} "
            f"solo permite {plan.max_menu_items}"
        )
    return None


def _check_category_limit(
    db: Session,
    restaurant_id: int,
    plan: SubscriptionPlan
) -> str | None:
    """Check category limit. Returns violation message or None."""
    current_categories = db.query(Category).filter(
        Category.restaurant_id == restaurant_id,
        Category.deleted_at.is_(None)
    ).count()
    
    if plan.max_categories != -1 and current_categories > plan.max_categories:
        return (
            f"Tienes {current_categories} categorías pero el plan {plan.display_name} "
            f"solo permite {plan.max_categories}"
        )
    return None


def _check_user_limits(
    db: Session,
    restaurant_id: int,
    plan: SubscriptionPlan,
    specific_role: str | None = None
) -> List[str]:
    """
    Check user limits by role. Returns list of violation messages.
    
    Args:
        db: Database session
        restaurant_id: ID of the restaurant
        plan: Subscription plan
        specific_role: Optional specific role to check (if None, checks all roles)
    """
    violations = []
    
    role_limits = {
        'admin': ('max_admin_users', 'administradores'),
        'waiter': ('max_waiter_users', 'meseros'),
        'cashier': ('max_cashier_users', 'cajeros'),
        'kitchen': ('max_kitchen_users', 'usuarios de cocina'),
        'owner': ('max_owner_users', 'dueños')
    }
    
    # Filter to specific role if provided
    if specific_role:
        if specific_role in role_limits:
            role_limits = {specific_role: role_limits[specific_role]}
        else:
            return []
    
    for role, (limit_key, role_name) in role_limits.items():
        # Count users based on role type
        if role == 'admin':
            current_users = db.query(User).filter(
                User.restaurant_id == restaurant_id,
                User.role == 'admin',
                User.deleted_at.is_(None)
            ).count()
        elif role in ['waiter', 'cashier', 'kitchen']:
            # Staff users - check by staff_type
            current_users = db.query(User).filter(
                User.restaurant_id == restaurant_id,
                User.role == 'staff',
                User.staff_type == role,
                User.deleted_at.is_(None)
            ).count()
        elif role == 'owner':
            current_users = db.query(User).filter(
                User.restaurant_id == restaurant_id,
                User.role == 'owner',
                User.deleted_at.is_(None)
            ).count()
        else:
            current_users = 0
        
        max_users = getattr(plan, limit_key, -1)
        
        if max_users != -1 and current_users > max_users:
            violations.append(
                f"Tienes {current_users} {role_name} pero el plan {plan.display_name} "
                f"solo permite {max_users}"
            )
    
    return violations


def can_add_resource(
    db: Session,
    restaurant_id: int,
    resource_type: str,
    plan: SubscriptionPlan
) -> bool:
    """
    Check if a new resource can be added without exceeding plan limits.
    
    Args:
        db: Database session
        restaurant_id: ID of the restaurant
        resource_type: Type of resource to add
        plan: Current subscription plan
        
    Returns:
        True if resource can be added, False otherwise
    """
    usage = get_current_usage(db, restaurant_id)
    
    if resource_type == "tables":
        return plan.max_tables == -1 or usage['tables'] < plan.max_tables
    
    elif resource_type == "menu_items":
        return plan.max_menu_items == -1 or usage['menu_items'] < plan.max_menu_items
    
    elif resource_type == "categories":
        return plan.max_categories == -1 or usage['categories'] < plan.max_categories
    
    elif resource_type.startswith("users_"):
        role = resource_type.replace("users_", "")
        limit_key = f"max_{role}_users"
        max_users = getattr(plan, limit_key, -1)
        return max_users == -1 or usage.get(f'users_{role}', 0) < max_users
    
    return False
