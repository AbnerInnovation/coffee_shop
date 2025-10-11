from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...db.base import get_db
from ...models.user import User
from ...models.restaurant import Restaurant
from ...core.dependencies import get_current_restaurant
from ...services.user import get_current_active_user
from ...services.menu import get_categories, get_category, create_category, update_category, delete_category
from ...schemas.menu import CategoryCreate, CategoryUpdate, CategoryInDB

router = APIRouter(
    prefix="/categories",
    tags=["categories"],
)

@router.get("/", response_model=List[CategoryInDB])
async def get_menu_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    restaurant: Restaurant = Depends(get_current_restaurant)
):
    """
    Get a list of all available menu categories with full details.
    """
    return get_categories(db, restaurant_id=restaurant.id)

@router.post("/", response_model=CategoryInDB, status_code=status.HTTP_201_CREATED)
async def create_menu_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    restaurant: Restaurant = Depends(get_current_restaurant)
):
    """
    Create a new menu category.
    """
    try:
        return create_category(db, category, restaurant_id=restaurant.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{category_id}", response_model=CategoryInDB)
async def get_menu_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    restaurant: Restaurant = Depends(get_current_restaurant)
):
    """
    Get a specific menu category by ID.
    """
    db_category = get_category(db, category_id, restaurant_id=restaurant.id)
    if db_category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return db_category

@router.put("/{category_id}", response_model=CategoryInDB)
async def update_menu_category(
    category_id: int,
    category_update: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    restaurant: Restaurant = Depends(get_current_restaurant)
):
    """
    Update a menu category.
    """
    try:
        db_category = update_category(db, category_id, category_update, restaurant_id=restaurant.id)
        if db_category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        return db_category
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_menu_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    restaurant: Restaurant = Depends(get_current_restaurant)
):
    """
    Delete a menu category.
    """
    try:
        deleted = delete_category(db, category_id, restaurant_id=restaurant.id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
