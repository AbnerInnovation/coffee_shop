from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.base import get_db
from app.models.menu import MenuItem as MenuItemModel
from app.schemas.menu import MenuItem, MenuItemCreate, MenuItemUpdate, Category
from app.services.menu import (
    get_menu_items,
    get_menu_item,
    create_menu_item as create_menu_item_service,
    update_menu_item as update_menu_item_service,
    delete_menu_item as delete_menu_item_service,
    get_categories
)
from app.models.user import User, UserRole
from app.services.user import get_current_active_user

# Create a router for menu endpoints
router = APIRouter(
    prefix="",
    tags=["menu"],
)

# Create a sub-router for menu items
items_router = APIRouter(prefix="/items")

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
    # Get menu items with category relationship loaded
    items = get_menu_items(
        db=db,
        skip=skip,
        limit=limit,
        category=category.value if category else None,
        available=available
    )
    
    # Ensure categories are loaded for each item
    for item in items:
        if not hasattr(item, 'category'):
            db.refresh(item)
            db.refresh(item, ['category'])
    
    return items

@items_router.post(
    "/",
    response_model=MenuItem,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_active_user)]
)
async def create_menu_item(
    menu_item: MenuItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> MenuItem:
    """
    Create a new menu item.
    Requires admin privileges.
    """
    check_admin(current_user)
    db_item = create_menu_item_service(db=db, menu_item=menu_item)
    
    # Ensure category is loaded
    db.refresh(db_item)
    db.refresh(db_item, ['category'])
    
    return db_item

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
    
    # Ensure category is loaded
    if not hasattr(db_item, 'category'):
        db.refresh(db_item)
        db.refresh(db_item, ['category'])
    
    return db_item

@items_router.put("/{item_id}", response_model=MenuItem)
async def update_menu_item(
    item_id: int,
    menu_item: MenuItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> MenuItem:
    """
    Update a menu item.
    Requires admin privileges.
    """
    check_admin(current_user)
    db_item = get_menu_item(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    return update_menu_item_service(db=db, db_item=db_item, menu_item=menu_item)

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
    
    delete_menu_item_service(db=db, db_item=db_item)
    return {"ok": True}

# Include the items router with the /items prefix
router.include_router(items_router)

@router.get("/categories/", response_model=List[str])
async def get_menu_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a list of all available menu categories.
    """
    return get_categories(db)
