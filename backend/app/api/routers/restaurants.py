from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List

from ...db.base import get_db
from ...models.restaurant import Restaurant as RestaurantModel
from ...models.user import User, UserRole
from ...schemas.restaurant import Restaurant, RestaurantCreate, RestaurantUpdate, RestaurantPublic
from ...services.user import get_current_active_user
from ...middleware.restaurant import get_restaurant_from_request

router = APIRouter(
    prefix="/restaurants",
    tags=["restaurants"]
)


def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """Dependency to ensure user is an admin"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can perform this action"
        )
    return current_user


@router.get("/current", response_model=RestaurantPublic)
async def get_current_restaurant(request: Request):
    """
    Get the current restaurant based on subdomain.
    This endpoint is public and doesn't require authentication.
    """
    restaurant = await get_restaurant_from_request(request)
    
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No restaurant found for this subdomain"
        )
    
    return restaurant


@router.get("/", response_model=List[Restaurant])
async def list_restaurants(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    List all restaurants (admin only).
    """
    restaurants = db.query(RestaurantModel).offset(skip).limit(limit).all()
    return restaurants


@router.get("/{restaurant_id}", response_model=Restaurant)
async def get_restaurant(
    restaurant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get a specific restaurant by ID (admin only).
    """
    restaurant = db.query(RestaurantModel).filter(RestaurantModel.id == restaurant_id).first()
    
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )
    
    return restaurant


@router.post("/", response_model=Restaurant, status_code=status.HTTP_201_CREATED)
async def create_restaurant(
    restaurant: RestaurantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Create a new restaurant (admin only).
    """
    # Check if subdomain already exists
    existing = db.query(RestaurantModel).filter(
        RestaurantModel.subdomain == restaurant.subdomain
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Restaurant with subdomain '{restaurant.subdomain}' already exists"
        )
    
    # Create new restaurant
    db_restaurant = RestaurantModel(**restaurant.dict())
    db.add(db_restaurant)
    db.commit()
    db.refresh(db_restaurant)
    
    return db_restaurant


@router.put("/{restaurant_id}", response_model=Restaurant)
async def update_restaurant(
    restaurant_id: int,
    restaurant: RestaurantUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Update a restaurant (admin only).
    """
    db_restaurant = db.query(RestaurantModel).filter(RestaurantModel.id == restaurant_id).first()
    
    if not db_restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )
    
    # Update fields
    update_data = restaurant.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_restaurant, field, value)
    
    db.commit()
    db.refresh(db_restaurant)
    
    return db_restaurant


@router.delete("/{restaurant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_restaurant(
    restaurant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Delete a restaurant (admin only).
    Warning: This will cascade delete all related data!
    """
    db_restaurant = db.query(RestaurantModel).filter(RestaurantModel.id == restaurant_id).first()
    
    if not db_restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )
    
    db.delete(db_restaurant)
    db.commit()
