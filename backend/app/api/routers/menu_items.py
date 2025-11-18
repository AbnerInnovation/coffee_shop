"""
Menu Items Router

Handles CRUD operations for menu items.
Separated from menu.py for better organization and maintainability.
"""

import logging
from fastapi import APIRouter, Depends, status, Query, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.exceptions import ResourceNotFoundError, ValidationError, DatabaseError

from app.db.base import get_db
from app.models.menu import MenuItem as MenuItemModel
from app.schemas.menu import MenuItem, MenuItemCreate, MenuItemUpdate
from app.middleware.subscription_limits import SubscriptionLimitsMiddleware
from app.services.menu import (
    get_menu_items,
    get_menu_item,
    create_menu_item as create_menu_item_service,
    update_menu_item as update_menu_item_service,
    delete_menu_item as delete_menu_item_service
)
from app.models.user import User
from app.models.restaurant import Restaurant
from app.services.user import get_current_active_user
from app.core.dependencies import (
    get_current_restaurant,
    require_admin_or_sysadmin
)

# Set up logging
logger = logging.getLogger(__name__)

# Create router
# Note: prefix is set in main api router (__init__.py), so we don't need it here
router = APIRouter(
    prefix="",
    tags=["menu-items"]
)


@router.get("/", response_model=List[MenuItem])
async def read_menu_items(
    request: Request,
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, le=100, description="Max items to return"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    available: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    restaurant: Restaurant = Depends(get_current_restaurant)
) -> List[MenuItem]:
    """
    Retrieve menu items with optional filtering (filtered by restaurant).
    """
    items = get_menu_items(
        db=db,
        restaurant_id=restaurant.id,
        skip=skip,
        limit=limit,
        category_id=category_id,
        available=available
    )
    
    # No need for db.refresh() - relationships are eager loaded with lazy='joined' and lazy='selectin'
    return items


@router.post("/", response_model=MenuItem, status_code=status.HTTP_201_CREATED)
async def create_menu_item(
    request: Request,
    menu_item: MenuItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_sysadmin),
    restaurant: Restaurant = Depends(get_current_restaurant)
) -> MenuItem:
    """
    Create a new menu item with variants.
    Requires admin or sysadmin privileges.
    """
    
    # Check subscription limit for menu items
    SubscriptionLimitsMiddleware.check_menu_item_limit(db, restaurant.id)

    if not menu_item.category_id:
        raise ValidationError("Category ID is required", field="category_id")

    try:
        db_item = create_menu_item_service(db=db, menu_item=menu_item, restaurant_id=restaurant.id)
        db.commit()
        db.refresh(db_item)  # Refresh to get generated ID and timestamps
        return db_item
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating menu item: {str(e)}")
        raise DatabaseError(f"Failed to create menu item: {str(e)}", operation="create")


@router.get("/{item_id}", response_model=MenuItem)
async def read_menu_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    restaurant: Restaurant = Depends(get_current_restaurant)
) -> MenuItem:
    """
    Get a specific menu item by ID.
    """
    db_item = get_menu_item(db, item_id=item_id, restaurant_id=restaurant.id)
    if db_item is None:
        raise ResourceNotFoundError("Menu item", item_id)
    
    # Relationships are eager loaded automatically
    return db_item


class AvailabilityUpdate(BaseModel):
    """Schema for updating menu item availability"""
    is_available: bool


@router.patch("/{item_id}/availability", response_model=MenuItem)
async def update_menu_item_availability(
    item_id: int,
    availability: AvailabilityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_sysadmin),
    restaurant: Restaurant = Depends(get_current_restaurant)
) -> MenuItem:
    """
    Update only the availability flag of a menu item.
    Requires admin or sysadmin privileges.
    """
    db_item = get_menu_item(db, item_id=item_id, restaurant_id=restaurant.id)
    if db_item is None:
        raise ResourceNotFoundError("Menu item", item_id)
    
    try:
        db_item.is_available = availability.is_available
        db.add(db_item)
        db.commit()
        db.refresh(db_item)  # Refresh to get updated timestamps
        return db_item
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating availability for menu item {item_id}: {str(e)}")
        raise DatabaseError(f"Failed to update menu item availability: {str(e)}", operation="update")


@router.put("/{item_id}", response_model=MenuItem)
async def update_menu_item(
    item_id: int,
    menu_item: MenuItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_sysadmin),
    restaurant: Restaurant = Depends(get_current_restaurant)
) -> MenuItem:
    """
    Update a menu item and its variants.
    Requires admin or sysadmin privileges.
    """
    db_item = get_menu_item(db, item_id=item_id, restaurant_id=restaurant.id)
    if db_item is None:
        raise ResourceNotFoundError("Menu item", item_id)

    try:
        # Update the item in a transaction
        updated_item = update_menu_item_service(db=db, item_id=item_id, menu_item=menu_item, restaurant_id=restaurant.id)
        # No need to refresh since we're using the same session and relationships are loaded
        return updated_item
    except Exception as e:
        logger.error(f"Error updating menu item: {str(e)}", exc_info=True)
        raise DatabaseError(f"Failed to update menu item: {str(e)}", operation="update")


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_menu_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_sysadmin),
    restaurant: Restaurant = Depends(get_current_restaurant)
):
    """
    Delete a menu item.
    Requires admin or sysadmin privileges.
    """
    db_item = get_menu_item(db, item_id=item_id, restaurant_id=restaurant.id)
    if db_item is None:
        raise ResourceNotFoundError("Menu item", item_id)

    try:
        delete_menu_item_service(db=db, db_item=db_item)
        db.commit()
        return {"ok": True}
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting menu item: {str(e)}")
        raise DatabaseError(f"Failed to delete menu item: {str(e)}", operation="delete")
