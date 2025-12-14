"""
Middleware for enforcing subscription limits.
Checks if restaurant has reached limits before allowing certain actions.
"""
from fastapi import Request, HTTPException, status
from sqlalchemy.orm import Session
from typing import Callable, Optional, Dict

from app.models import Restaurant, User, MenuItem, Table, Category
# New modular imports - SOLID refactoring
from app.services.subscription import get_restaurant_subscription
from app.core.operation_modes import OperationMode, is_feature_enabled


def _get_subscription_limits(db: Session, restaurant_id: int) -> Dict[str, any]:
    """
    Helper function to get subscription limits for a restaurant.
    Returns a dict with all plan limits including operation_mode.
    """
    subscription = get_restaurant_subscription(db, restaurant_id)
    
    # Check if subscription exists AND can operate (is active/valid)
    # If expired (trial or active), we treat it as no subscription to enforce default restrictive limits
    if subscription and not subscription.can_operate:
        subscription = None
    
    if not subscription or not subscription.plan:
        # No subscription or plan, return default limits (very restrictive)
        return {
            'operation_mode': OperationMode.FULL_RESTAURANT,
            'max_admin_users': 1,
            'max_waiter_users': 0,
            'max_cashier_users': 0,
            'max_kitchen_users': 0,
            'max_owner_users': 1,
            'max_tables': 5,
            'max_menu_items': 10,
            'max_categories': 3,
            'has_kitchen_module': False,
            'has_ingredients_module': False,
            'has_inventory_module': False,
            'has_advanced_reports': False,
            'has_multi_branch': False
        }
    
    plan = subscription.plan
    return {
        'operation_mode': plan.operation_mode,
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


class SubscriptionLimitsMiddleware:
    """Middleware to enforce subscription limits"""
    
    @staticmethod
    def check_user_limit(db: Session, restaurant_id: int, role: str, staff_type: str = None) -> None:
        """Check if restaurant can add more users of this role/staff_type"""
        limits = _get_subscription_limits(db, restaurant_id)
        
        # Determine which type of user we're checking
        # For staff users, we check by staff_type (waiter, cashier, kitchen)
        # For other roles, we check by role (admin, customer, etc.)
        check_type = staff_type if staff_type and role == 'staff' else role
        
        # Count current non-deleted users only
        if staff_type and role == 'staff':
            # Count staff users by staff_type
            current_count = db.query(User).filter(
                User.restaurant_id == restaurant_id,
                User.role == 'staff',
                User.staff_type == staff_type,
                User.deleted_at.is_(None)
            ).count()
        else:
            # Count users by role
            current_count = db.query(User).filter(
                User.restaurant_id == restaurant_id,
                User.role == role,
                User.deleted_at.is_(None)
            ).count()
        
        # Map role/staff_type to limit key
        limit_map = {
            'admin': 'max_admin_users',
            'waiter': 'max_waiter_users',
            'cashier': 'max_cashier_users',
            'kitchen': 'max_kitchen_users',
            'customer': -1  # Usually unlimited
        }
        
        limit_key = limit_map.get(check_type)
        if not limit_key:
            return  # Unknown type, allow
        
        max_allowed = limits.get(limit_key, -1) if isinstance(limit_key, str) else limit_key
        
        # -1 means unlimited
        if max_allowed == -1:
            return
        
        if current_count >= max_allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Subscription limit reached: Maximum {max_allowed} {check_type} users allowed. Please upgrade your plan."
            )
    
    @staticmethod
    def check_table_limit(db: Session, restaurant_id: int) -> None:
        """Check if restaurant can add more tables"""
        limits = _get_subscription_limits(db, restaurant_id)
        
        current_count = db.query(Table).filter(
            Table.restaurant_id == restaurant_id,
            Table.deleted_at.is_(None)
        ).count()
        
        max_allowed = limits.get('max_tables', -1)
        
        if max_allowed == -1:
            return
        
        if current_count >= max_allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Subscription limit reached: Maximum {max_allowed} tables allowed. Please upgrade your plan."
            )
    
    @staticmethod
    def check_menu_item_limit(db: Session, restaurant_id: int) -> None:
        """Check if restaurant can add more menu items"""
        limits = _get_subscription_limits(db, restaurant_id)
        
        current_count = db.query(MenuItem).filter(
            MenuItem.restaurant_id == restaurant_id,
            MenuItem.deleted_at.is_(None)
        ).count()
        
        max_allowed = limits.get('max_menu_items', -1)
        
        if max_allowed == -1:
            return
        
        if current_count >= max_allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Subscription limit reached: Maximum {max_allowed} menu items allowed. Please upgrade your plan."
            )
    
    @staticmethod
    def check_category_limit(db: Session, restaurant_id: int) -> None:
        """Check if restaurant can add more categories"""
        limits = _get_subscription_limits(db, restaurant_id)
        
        current_count = db.query(Category).filter(
            Category.restaurant_id == restaurant_id,
            Category.deleted_at.is_(None)
        ).count()
        
        max_allowed = limits.get('max_categories', -1)
        
        if max_allowed == -1:
            return
        
        if current_count >= max_allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Subscription limit reached: Maximum {max_allowed} categories allowed. Please upgrade your plan."
            )
    
    @staticmethod
    def check_feature_access(db: Session, restaurant_id: int, feature: str) -> None:
        """Check if restaurant has access to a specific feature"""
        limits = _get_subscription_limits(db, restaurant_id)
        operation_mode = limits.get('operation_mode', OperationMode.FULL_RESTAURANT)
        
        # Check if feature is enabled in operation mode
        mode_feature_map = {
            'tables': 'show_tables',
            'kitchen': 'show_kitchen',
            'waiters': 'show_waiters',
            'delivery': 'show_delivery'
        }
        
        mode_feature = mode_feature_map.get(feature)
        if mode_feature and not is_feature_enabled(operation_mode, mode_feature):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Feature '{feature}' is not available in {operation_mode.value} mode."
            )
        
        # Check plan-level feature flags
        feature_map = {
            'kitchen': 'has_kitchen_module',
            'ingredients': 'has_ingredients_module',
            'inventory': 'has_inventory_module',
            'advanced_reports': 'has_advanced_reports',
            'multi_branch': 'has_multi_branch'
        }
        
        limit_key = feature_map.get(feature)
        if not limit_key:
            return  # Unknown feature, allow
        
        has_access = limits.get(limit_key, False)
        
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Feature not available: '{feature}' is not included in your current plan. Please upgrade your plan to access this feature."
            )


# Helper functions for dependency injection
def check_user_limit(role: str):
    """Dependency to check user limit"""
    def _check(request: Request, db: Session):
        restaurant_id = request.state.restaurant_id
        SubscriptionLimitsMiddleware.check_user_limit(db, restaurant_id, role)
    return _check


def check_table_limit(request: Request, db: Session):
    """Dependency to check table limit"""
    restaurant_id = request.state.restaurant_id
    SubscriptionLimitsMiddleware.check_table_limit(db, restaurant_id)


def check_menu_item_limit(request: Request, db: Session):
    """Dependency to check menu item limit"""
    restaurant_id = request.state.restaurant_id
    SubscriptionLimitsMiddleware.check_menu_item_limit(db, restaurant_id)


def check_category_limit(request: Request, db: Session):
    """Dependency to check category limit"""
    restaurant_id = request.state.restaurant_id
    SubscriptionLimitsMiddleware.check_category_limit(db, restaurant_id)


def check_feature_access(feature: str):
    """Dependency to check feature access"""
    def _check(request: Request, db: Session):
        restaurant_id = request.state.restaurant_id
        SubscriptionLimitsMiddleware.check_feature_access(db, restaurant_id, feature)
    return _check
