"""
Middleware for enforcing subscription limits.
Checks if restaurant has reached limits before allowing certain actions.
"""
from fastapi import Request, HTTPException, status
from sqlalchemy.orm import Session
from typing import Callable, Optional

from app.models import Restaurant, User, MenuItem, Table, Category
from app.services.subscription_service import SubscriptionService


class SubscriptionLimitsMiddleware:
    """Middleware to enforce subscription limits"""
    
    @staticmethod
    def check_user_limit(db: Session, restaurant_id: int, role: str) -> None:
        """Check if restaurant can add more users of this role"""
        service = SubscriptionService(db)
        limits = service.get_subscription_limits(restaurant_id)
        
        # Count current users by role
        current_count = db.query(User).filter(
            User.restaurant_id == restaurant_id,
            User.role == role,
            User.deleted_at.is_(None)
        ).count()
        
        # Map role to limit key
        limit_map = {
            'admin': 'max_admin_users',
            'waiter': 'max_waiter_users',
            'cashier': 'max_cashier_users',
            'kitchen': 'max_kitchen_users',
            'owner': 'max_owner_users'
        }
        
        limit_key = limit_map.get(role)
        if not limit_key:
            return  # Unknown role, allow
        
        max_allowed = limits.get(limit_key, -1)
        
        # -1 means unlimited
        if max_allowed == -1:
            return
        
        if current_count >= max_allowed:
            # Translate role names
            role_names = {
                'admin': 'administradores',
                'waiter': 'meseros',
                'cashier': 'cajeros',
                'kitchen': 'usuarios de cocina',
                'owner': 'dueños'
            }
            role_es = role_names.get(role, role)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Límite de suscripción alcanzado: Máximo {max_allowed} {role_es} permitidos. Por favor mejora tu plan."
            )
    
    @staticmethod
    def check_table_limit(db: Session, restaurant_id: int) -> None:
        """Check if restaurant can add more tables"""
        service = SubscriptionService(db)
        limits = service.get_subscription_limits(restaurant_id)
        
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
                detail=f"Límite de suscripción alcanzado: Máximo {max_allowed} mesas permitidas. Por favor mejora tu plan."
            )
    
    @staticmethod
    def check_menu_item_limit(db: Session, restaurant_id: int) -> None:
        """Check if restaurant can add more menu items"""
        service = SubscriptionService(db)
        limits = service.get_subscription_limits(restaurant_id)
        
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
                detail=f"Límite de suscripción alcanzado: Máximo {max_allowed} productos permitidos. Por favor mejora tu plan."
            )
    
    @staticmethod
    def check_category_limit(db: Session, restaurant_id: int) -> None:
        """Check if restaurant can add more categories"""
        service = SubscriptionService(db)
        limits = service.get_subscription_limits(restaurant_id)
        
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
                detail=f"Límite de suscripción alcanzado: Máximo {max_allowed} categorías permitidas. Por favor mejora tu plan."
            )
    
    @staticmethod
    def check_feature_access(db: Session, restaurant_id: int, feature: str) -> None:
        """Check if restaurant has access to a specific feature"""
        service = SubscriptionService(db)
        limits = service.get_subscription_limits(restaurant_id)
        
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
            # Translate feature names
            feature_names = {
                'kitchen': 'Módulo de Cocina',
                'ingredients': 'Módulo de Ingredientes',
                'inventory': 'Módulo de Inventario',
                'advanced_reports': 'Reportes Avanzados',
                'multi_branch': 'Multi-sucursal'
            }
            feature_es = feature_names.get(feature, feature)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Característica no disponible: '{feature_es}' no está incluida en tu plan actual. Por favor mejora tu plan para acceder a esta característica."
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
