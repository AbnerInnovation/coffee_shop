import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

# Set up logging
logger = logging.getLogger(__name__)

from app.db.base import get_db
from app.models.menu import MenuItem as MenuItemModel
from app.schemas.menu import MenuItem, MenuItemCreate, MenuItemUpdate, Category
from app.services.menu import (
    get_menu_items,
    get_menu_item,
    create_menu_item,
    update_menu_item as update_menu_item_service,
    delete_menu_item as delete_menu_item_service,
    get_categories
)
from app.services.menu_variant import (
    get_variants as get_variants_service,
    get_variant as get_variant_service,
    create_variant as create_variant_service,
    update_variant as update_variant_service,
    delete_variant as delete_variant_service
)
from app.schemas.menu import (
    MenuItemVariant, MenuItemVariantCreate, MenuItemVariantUpdate
)
from app.models.user import User, UserRole
from app.services.user import get_current_active_user

# Create a router for menu endpoints
router = APIRouter(
    prefix="",
    tags=["menu"],
)

# Create a sub-router for menu items
items_router = APIRouter()

def check_admin(user: User):
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

@items_router.get("/", response_model=List[MenuItem])
async def read_menu_items(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, le=100, description="Max items to return"),
    category: Optional[Category] = None,
    available: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[MenuItem]:
    """
    Retrieve menu items with optional filtering.
    """
    items = get_menu_items(
        db=db,
        skip=skip,
        limit=limit,
        category=category.value if category else None,
        available=available
    )

    for item in items:
        if not hasattr(item, 'category'):
            db.refresh(item, ['category'])
        if not hasattr(item, 'variants'):
            db.refresh(item, ['variants'])

    return items

@items_router.post("/", response_model=MenuItem, status_code=status.HTTP_201_CREATED)
async def create_menu_item(
    menu_item: MenuItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> MenuItem:
    """
    Create a new menu item with variants.
    Requires admin privileges.
    """
    check_admin(current_user)

    if not menu_item.category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category is required"
        )

    try:
        with db.begin():
            db_item = create_menu_item(db=db, menu_item=menu_item)
            db.refresh(db_item, ['category', 'variants'])
            return db_item
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating menu item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@items_router.get("/{item_id}", response_model=MenuItem)
async def read_menu_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> MenuItem:
    """
    Get a specific menu item by ID.
    """
    db_item = get_menu_item(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Menu item not found")

    if not hasattr(db_item, 'category'):
        db.refresh(db_item, ['category'])
    if not hasattr(db_item, 'variants'):
        db.refresh(db_item, ['variants'])

    return db_item

@items_router.put("/{item_id}", response_model=MenuItem)
async def update_menu_item(
    item_id: int,
    menu_item: MenuItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> MenuItem:
    """
    Update a menu item and its variants.
    Requires admin privileges.
    """
    check_admin(current_user)
    db_item = get_menu_item(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Menu item with ID {item_id} not found"
        )

    try:
        # Get the existing item first to ensure it exists
        db_item = get_menu_item(db, item_id=item_id)
        if db_item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Menu item with ID {item_id} not found"
            )
            
        # Update the item in a transaction
        updated_item = update_menu_item_service(db=db, item_id=item_id, menu_item=menu_item)
        # No need to refresh since we're using the same session and relationships are loaded
        return updated_item
            
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error updating menu item: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@items_router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_menu_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a menu item.
    Requires admin privileges.
    """
    check_admin(current_user)
    db_item = get_menu_item(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Menu item not found")

    try:
        delete_menu_item_service(db=db, db_item=db_item)
        db.commit()
        return {"ok": True}
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting menu item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# Create a sub-router for variants
variants_router = APIRouter(prefix="/{item_id}/variants")

@variants_router.get("/", response_model=List[MenuItemVariant])
async def read_variants(
    item_id: int,
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, le=100, description="Max items to return"),
    available: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[MenuItemVariant]:
    """
    Get all variants for a menu item.
    """
    menu_item = get_menu_item(db, item_id)
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    return get_variants_service(
        db=db,
        menu_item_id=item_id,
        skip=skip,
        limit=limit,
        available=available
    )

@variants_router.post("/", response_model=MenuItemVariant, status_code=status.HTTP_201_CREATED)
async def create_variant(
    item_id: int,
    variant: MenuItemVariantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> MenuItemVariant:
    """
    Create a new variant for a menu item.
    Requires admin privileges.
    """
    check_admin(current_user)

    try:
        result = create_variant_service(db=db, variant=variant, menu_item_id=item_id)
        db.commit()
        db.refresh(result, ['menu_item'])
        return result
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating variant: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e) or "Error creating variant"
        )

@variants_router.get("/{variant_id}", response_model=MenuItemVariant)
async def read_variant(
    item_id: int,
    variant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> MenuItemVariant:
    """
    Get a specific variant by ID.
    """
    variant = get_variant_service(db, variant_id, menu_item_id=item_id)
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")
    return variant

@variants_router.put("/{variant_id}", response_model=MenuItemVariant)
async def update_variant(
    item_id: int,
    variant_id: int,
    variant: MenuItemVariantUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> MenuItemVariant:
    """
    Update a variant.
    Requires admin privileges.
    """
    check_admin(current_user)

    db_variant = get_variant_service(db, variant_id, menu_item_id=item_id)
    if not db_variant:
        raise HTTPException(status_code=404, detail="Variant not found")

    try:
        result = update_variant_service(db=db, db_variant=db_variant, variant=variant)
        db.commit()
        db.refresh(result, ['menu_item'])
        return result
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating variant {variant_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e) or "Error updating variant"
        )

@variants_router.delete("/{variant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_variant(
    item_id: int,
    variant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> None:
    """
    Delete a variant.
    Requires admin privileges.
    """
    check_admin(current_user)

    db_variant = get_variant_service(db, variant_id, menu_item_id=item_id)
    if not db_variant:
        raise HTTPException(status_code=404, detail="Variant not found")

    try:
        if not delete_variant_service(db=db, db_variant=db_variant):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete variant"
            )
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting variant {variant_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e) or "Error deleting variant"
        )

# Include the routers
router.include_router(items_router)
router.include_router(variants_router)
