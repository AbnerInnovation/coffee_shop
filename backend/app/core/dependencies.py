from fastapi import Request, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from ..models.restaurant import Restaurant
from ..middleware.restaurant import get_restaurant_from_request


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
