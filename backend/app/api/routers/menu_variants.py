"""
Menu Variants Router

Handles CRUD operations for menu item variants.
Separated from menu.py for better organization and maintainability.
"""

import logging
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.exceptions import ResourceNotFoundError, ValidationError, DatabaseError, ForbiddenError

from app.db.base import get_db
from app.services.menu import get_menu_item
from app.services.menu_variant import (
    get_variants as get_variants_service,
    get_variant as get_variant_service,
    create_variant as create_variant_service,
    update_variant as update_variant_service,
    delete_variant as delete_variant_service
)
from app.schemas.menu import (
    MenuItemVariant,
    MenuItemVariantCreate,
    MenuItemVariantUpdate
)
from app.models.user import User, UserRole
from app.models.restaurant import Restaurant
from app.services.user import get_current_active_user
from app.core.dependencies import get_current_restaurant

# Set up logging
logger = logging.getLogger(__name__)

# Create router  
# Note: This will be included in menu_items router, so prefix is relative
router = APIRouter(
    prefix="/{item_id}/variants",
    tags=["menu-variants"]
)


def check_admin(current_user: User) -> None:
    """
    Check if the current user has admin privileges.
    
    Args:
        current_user: The current authenticated user
        
    Raises:
        ForbiddenError: If user is not admin or sysadmin
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.SYSADMIN]:
        raise ForbiddenError("Admin privileges required", required_permission="admin")


@router.get("/", response_model=List[MenuItemVariant])
async def read_variants(
    item_id: int,
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, le=100, description="Max items to return"),
    available: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    restaurant: Restaurant = Depends(get_current_restaurant)
) -> List[MenuItemVariant]:
    """
    Get all variants for a menu item.
    """
    menu_item = get_menu_item(db, item_id, restaurant_id=restaurant.id)
    if not menu_item:
        raise ResourceNotFoundError("Menu item", item_id)

    return get_variants_service(
        db=db,
        menu_item_id=item_id,
        skip=skip,
        limit=limit,
        available=available
    )


@router.post("/", response_model=MenuItemVariant, status_code=status.HTTP_201_CREATED)
async def create_variant(
    item_id: int,
    variant: MenuItemVariantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    restaurant: Restaurant = Depends(get_current_restaurant)
) -> MenuItemVariant:
    """
    Create a new variant for a menu item.
    Requires admin privileges.
    """
    check_admin(current_user)

    try:
        result = create_variant_service(db=db, variant=variant, menu_item_id=item_id)
        db.commit()
        db.refresh(result)  # Refresh to get generated ID and timestamps
        return result
    except ValueError as e:
        db.rollback()
        raise ValidationError(str(e))
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating variant: {str(e)}")
        raise DatabaseError(f"Failed to create variant: {str(e)}", operation="create")


@router.get("/{variant_id}", response_model=MenuItemVariant)
async def read_variant(
    item_id: int,
    variant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    restaurant: Restaurant = Depends(get_current_restaurant)
) -> MenuItemVariant:
    """
    Get a specific variant by ID.
    """
    variant = get_variant_service(db, variant_id, menu_item_id=item_id)
    if not variant:
        raise ResourceNotFoundError("Variant", variant_id)
    return variant


@router.put("/{variant_id}", response_model=MenuItemVariant)
async def update_variant(
    item_id: int,
    variant_id: int,
    variant: MenuItemVariantUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    restaurant: Restaurant = Depends(get_current_restaurant)
) -> MenuItemVariant:
    """
    Update a variant.
    Requires admin privileges.
    """
    check_admin(current_user)

    db_variant = get_variant_service(db, variant_id, menu_item_id=item_id)
    if not db_variant:
        raise ResourceNotFoundError("Variant", variant_id)

    try:
        result = update_variant_service(db=db, db_variant=db_variant, variant=variant)
        db.commit()
        db.refresh(result)  # Refresh to get updated timestamps
        return result
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating variant {variant_id}: {str(e)}")
        raise DatabaseError(f"Failed to update variant: {str(e)}", operation="update")


@router.delete("/{variant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_variant(
    item_id: int,
    variant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    restaurant: Restaurant = Depends(get_current_restaurant)
) -> None:
    """
    Delete a variant.
    Requires admin privileges.
    """
    check_admin(current_user)

    db_variant = get_variant_service(db, variant_id, menu_item_id=item_id)
    if not db_variant:
        raise ResourceNotFoundError("Variant", variant_id)

    try:
        if not delete_variant_service(db=db, db_variant=db_variant):
            raise DatabaseError("Failed to delete variant", operation="delete")
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting variant {variant_id}: {str(e)}")
        raise DatabaseError(f"Failed to delete variant: {str(e)}", operation="delete")
