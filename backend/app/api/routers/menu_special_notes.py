"""
Menu Special Notes Router

Handles special notes tracking and statistics for menu items.
Separated from menu.py for better organization and maintainability.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.base import get_db
from app.services.special_notes import SpecialNotesService
from app.schemas.special_notes import TopSpecialNote, TrackNoteRequest, TrackNoteResponse
from app.models.user import User, UserRole
from app.models.restaurant import Restaurant
from app.services.user import get_current_active_user
from app.core.dependencies import get_current_restaurant

# Set up logging
logger = logging.getLogger(__name__)

# Create router
# Note: This will be included in main menu router, so prefix is relative
router = APIRouter(
    prefix="/special-notes",
    tags=["menu-special-notes"]
)


def check_admin(current_user: User) -> None:
    """
    Check if the current user has admin privileges.
    
    Args:
        current_user: The current authenticated user
        
    Raises:
        HTTPException: If user is not admin or sysadmin
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.SYSADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )


@router.get("/top", response_model=List[TopSpecialNote])
async def get_top_special_notes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    restaurant: Restaurant = Depends(get_current_restaurant)
):
    """
    Get the top 3 most frequently used special notes for quick access.
    Results are cached for 1 hour for optimal performance.
    """
    try:
        top_notes = SpecialNotesService.get_top_notes(restaurant.id, db)
        return top_notes
    except Exception as e:
        logger.error(f"Error fetching top special notes: {str(e)}")
        # Return empty list on error instead of failing
        return []


@router.post("/track", response_model=TrackNoteResponse)
async def track_special_note(
    request: TrackNoteRequest,
    current_user: User = Depends(get_current_active_user),
    restaurant: Restaurant = Depends(get_current_restaurant)
):
    """
    Track usage of a special note for statistics.
    Updates are batched for performance (actual DB write happens in background).
    """
    try:
        # Async tracking - accumulates in memory
        SpecialNotesService.track_note_async(restaurant.id, request.note_text)
        return TrackNoteResponse(success=True)
    except Exception as e:
        logger.error(f"Error tracking special note: {str(e)}")
        # Don't fail the request if tracking fails
        return TrackNoteResponse(success=False, message="Failed to track note")


@router.get("/cache-stats")
async def get_cache_stats(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get cache statistics for monitoring (admin only).
    """
    check_admin(current_user)
    return SpecialNotesService.get_cache_stats()
