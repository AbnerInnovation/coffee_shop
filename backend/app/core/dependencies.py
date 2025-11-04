from fastapi import Request, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from ..models.restaurant import Restaurant
from ..models.user import User, UserRole
from ..middleware.restaurant import get_restaurant_from_request
from ..middleware.subscription_status import SubscriptionStatusMiddleware
from ..services.user import get_current_active_user
from ..db.base import get_db


async def get_current_restaurant(request: Request) -> Restaurant:
    """
    Dependency to get the current restaurant from the request subdomain.
    Raises HTTPException if no restaurant found.
    """
    restaurant = await get_restaurant_from_request(request)
    
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant context required. Please access via subdomain (e.g., restaurant1.example.com)"
        )
    
    return restaurant


async def get_optional_restaurant(request: Request) -> Optional[Restaurant]:
    """
    Dependency to optionally get the current restaurant from the request subdomain.
    Returns None if no restaurant found (doesn't raise exception).
    """
    return await get_restaurant_from_request(request)


async def get_current_user_with_restaurant(
    current_user: User = Depends(get_current_active_user),
    restaurant: Restaurant = Depends(get_current_restaurant)
) -> User:
    """
    Dependency to get current user and validate they have access to the current restaurant.
    
    - SYSADMIN: Can access any restaurant
    - Other roles: Must belong to the current restaurant (or have multi-branch access in future)
    
    Raises HTTPException if user doesn't have access.
    """
    # SYSADMIN can access any restaurant
    if current_user.role == UserRole.SYSADMIN:
        return current_user
    
    # Other roles must belong to the current restaurant
    if current_user.restaurant_id != restaurant.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this restaurant"
        )
    
    return current_user


async def get_current_user_with_active_subscription(
    current_user: User = Depends(get_current_user_with_restaurant),
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current user and validate:
    1. They have access to the current restaurant
    2. The restaurant has an active subscription
    
    - SYSADMIN: Bypasses subscription check
    - Other roles: Requires active subscription
    
    Raises HTTPException if subscription is expired or suspended.
    """
    # Check subscription status (SYSADMIN bypasses this check)
    SubscriptionStatusMiddleware.check_active_subscription(
        db=db,
        restaurant_id=restaurant.id,
        user_role=current_user.role.value
    )
    
    return current_user


def require_admin_or_sysadmin(
    current_user: User = Depends(get_current_user_with_restaurant)
) -> User:
    """
    Dependency to ensure user is ADMIN or SYSADMIN.
    Already validates restaurant access via get_current_user_with_restaurant.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.SYSADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can perform this action"
        )
    return current_user


def require_sysadmin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Dependency to ensure user is SYSADMIN.
    """
    if current_user.role != UserRole.SYSADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only system administrators can perform this action"
        )
    return current_user


def require_staff_or_admin(
    current_user: User = Depends(get_current_user_with_restaurant)
) -> User:
    """
    Dependency to ensure user is STAFF, ADMIN, or SYSADMIN.
    Already validates restaurant access via get_current_user_with_restaurant.
    """
    if current_user.role not in [UserRole.STAFF, UserRole.ADMIN, UserRole.SYSADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to perform this action"
        )
    return current_user


def require_role(*allowed_roles: UserRole):
    """
    Factory function to create a dependency that requires specific roles.
    
    Usage:
        @router.post("/items/")
        async def create_item(
            current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.SYSADMIN))
        ):
            ...
    """
    def role_checker(
        current_user: User = Depends(get_current_user_with_restaurant)
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {', '.join([r.value for r in allowed_roles])}"
            )
        return current_user
    return role_checker
