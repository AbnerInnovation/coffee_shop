"""
Restaurant Users Management API
Allows restaurant admins to manage users within their restaurant.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ...db.base import get_db
from ...models.user import User as UserModel, UserRole
from ...models.restaurant import Restaurant
from ...schemas.user import User, UserCreate, UserUpdate
from ...core.dependencies import (
    get_current_restaurant,
    get_current_user_with_restaurant,
    require_admin_or_sysadmin
)
from ...middleware.subscription_limits import SubscriptionLimitsMiddleware
from ...services import user as user_service

router = APIRouter(
    prefix="/restaurant-users",
    tags=["restaurant-users"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=List[User])
async def list_restaurant_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    restaurant: Restaurant = Depends(get_current_restaurant),
    current_user: UserModel = Depends(require_admin_or_sysadmin)
) -> List[User]:
    """
    List all users for the current restaurant.
    Only accessible by restaurant admin or sysadmin.
    """
    # SYSADMIN can see all users, others only see their restaurant's users
    if current_user.role == UserRole.SYSADMIN:
        query = db.query(UserModel)
    else:
        query = db.query(UserModel).filter(UserModel.restaurant_id == restaurant.id)
    
    users = query.offset(skip).limit(limit).all()
    return users


@router.get("/by-role/{role}", response_model=List[User])
async def list_users_by_role(
    role: UserRole,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    restaurant: Restaurant = Depends(get_current_restaurant),
    current_user: UserModel = Depends(require_admin_or_sysadmin)
) -> List[User]:
    """
    List users by role for the current restaurant.
    Only accessible by restaurant admin or sysadmin.
    """
    query = db.query(UserModel).filter(
        UserModel.restaurant_id == restaurant.id,
        UserModel.role == role
    )
    
    users = query.offset(skip).limit(limit).all()
    return users


@router.get("/count-by-role")
async def count_users_by_role(
    db: Session = Depends(get_db),
    restaurant: Restaurant = Depends(get_current_restaurant),
    current_user: UserModel = Depends(require_admin_or_sysadmin)
):
    """
    Get count of users by role for the current restaurant.
    Useful for checking subscription limits.
    """
    counts = {}
    for role in UserRole:
        if role == UserRole.SYSADMIN:
            continue  # Don't count sysadmins
        
        count = db.query(UserModel).filter(
            UserModel.restaurant_id == restaurant.id,
            UserModel.role == role
        ).count()
        counts[role.value] = count
    
    return counts


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_restaurant_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    restaurant: Restaurant = Depends(get_current_restaurant),
    current_user: UserModel = Depends(require_admin_or_sysadmin)
) -> User:
    """
    Create a new user for the current restaurant.
    Only accessible by restaurant admin or sysadmin.
    Validates subscription limits before creation.
    """
    # Prevent creating SYSADMIN users (only existing sysadmins can do that elsewhere)
    if user.role == UserRole.SYSADMIN and current_user.role != UserRole.SYSADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only system administrators can create sysadmin users"
        )
    
    # Check subscription limit for this user role
    if user.role != UserRole.SYSADMIN:
        SubscriptionLimitsMiddleware.check_user_limit(db, restaurant.id, user.role.value)
    
    # Check if user with this email already exists
    db_user = user_service.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Force restaurant_id to current restaurant (prevent cross-restaurant user creation)
    user.restaurant_id = restaurant.id
    
    return user_service.create_user(db=db, user=user)


@router.get("/{user_id}", response_model=User)
async def get_restaurant_user(
    user_id: int,
    db: Session = Depends(get_db),
    restaurant: Restaurant = Depends(get_current_restaurant),
    current_user: UserModel = Depends(require_admin_or_sysadmin)
) -> User:
    """
    Get a specific user by ID.
    Only accessible by restaurant admin or sysadmin.
    Users can only access users from their own restaurant (except sysadmin).
    """
    db_user = user_service.get_user(db, user_id=user_id)
    
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Validate user belongs to current restaurant (unless sysadmin)
    if current_user.role != UserRole.SYSADMIN:
        if db_user.restaurant_id != restaurant.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this user"
            )
    
    return db_user


@router.put("/{user_id}", response_model=User)
async def update_restaurant_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db),
    restaurant: Restaurant = Depends(get_current_restaurant),
    current_user: UserModel = Depends(require_admin_or_sysadmin)
) -> User:
    """
    Update a user.
    Only accessible by restaurant admin or sysadmin.
    Users can only update users from their own restaurant (except sysadmin).
    """
    db_user = user_service.get_user(db, user_id=user_id)
    
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Validate user belongs to current restaurant (unless sysadmin)
    if current_user.role != UserRole.SYSADMIN:
        if db_user.restaurant_id != restaurant.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this user"
            )
    
    # Prevent changing restaurant_id (unless sysadmin)
    if hasattr(user, 'restaurant_id') and user.restaurant_id is not None and current_user.role != UserRole.SYSADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only system administrators can change user's restaurant"
        )
    
    # Prevent non-sysadmins from creating/modifying sysadmin users
    if user.role == UserRole.SYSADMIN and current_user.role != UserRole.SYSADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only system administrators can modify sysadmin users"
        )
    
    return user_service.update_user(db=db, db_user=db_user, user=user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_restaurant_user(
    user_id: int,
    db: Session = Depends(get_db),
    restaurant: Restaurant = Depends(get_current_restaurant),
    current_user: UserModel = Depends(require_admin_or_sysadmin)
) -> None:
    """
    Delete a user.
    Only accessible by restaurant admin or sysadmin.
    Users can only delete users from their own restaurant (except sysadmin).
    Cannot delete yourself.
    """
    db_user = user_service.get_user(db, user_id=user_id)
    
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent self-deletion
    if db_user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete yourself"
        )
    
    # Validate user belongs to current restaurant (unless sysadmin)
    if current_user.role != UserRole.SYSADMIN:
        if db_user.restaurant_id != restaurant.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this user"
            )
    
    # Prevent non-sysadmins from deleting sysadmin users
    if db_user.role == UserRole.SYSADMIN and current_user.role != UserRole.SYSADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only system administrators can delete sysadmin users"
        )
    
    user_service.delete_user(db=db, db_user=db_user)
