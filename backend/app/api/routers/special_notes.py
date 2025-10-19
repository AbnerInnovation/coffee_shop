"""
Special Notes API Router

Endpoints for tracking and retrieving frequently used special notes/instructions.
This enables the "Top 3 most requested notes" feature for quick order entry.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging

from app.db.base import get_db
from app.models.user import User, UserRole
from app.models.restaurant import Restaurant
from app.services.user import get_current_active_user
from app.core.dependencies import get_current_restaurant
from app.services.special_notes import SpecialNotesService
from app.schemas.special_notes import TopSpecialNote, TrackNoteRequest, TrackNoteResponse

logger = logging.getLogger(__name__)


def check_admin(user: User):
    """Check if user has admin role."""
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

router = APIRouter(
    prefix="/special-notes",
    tags=["special-notes"]
)


@router.get("/top", response_model=List[TopSpecialNote])
async def get_top_special_notes(
    limit: int = 3,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    restaurant: Restaurant = Depends(get_current_restaurant)
):
    """
    Get the top N most frequently used special notes for quick access.
    Results are cached for 1 hour for optimal performance.
    
    Args:
        limit: Number of top notes to return (default: 3)
        db: Database session
        current_user: Current authenticated user
        restaurant: Current restaurant context
        
    Returns:
        List of top special notes with usage counts
    """
    try:
        top_notes = SpecialNotesService.get_top_notes(restaurant.id, db)
        # Limit the results to the requested number
        return top_notes[:limit]
    except Exception as e:
        logger.error(f"Error fetching top special notes: {str(e)}")
        # Return empty list on error instead of failing
        return []


@router.post("/record", response_model=TrackNoteResponse)
async def record_special_note(
    request: TrackNoteRequest,
    current_user: User = Depends(get_current_active_user),
    restaurant: Restaurant = Depends(get_current_restaurant)
):
    """
    Record usage of a special note for statistics.
    Updates are batched for performance (actual DB write happens in background).
    
    Args:
        request: Request containing the note text to track
        current_user: Current authenticated user
        restaurant: Current restaurant context
        
    Returns:
        Response indicating success or failure
    """
    try:
        # Async tracking - accumulates in memory
        SpecialNotesService.track_note_async(restaurant.id, request.note_text)
        return TrackNoteResponse(success=True)
    except Exception as e:
        logger.error(f"Error recording special note: {str(e)}")
        # Don't fail the request if tracking fails
        return TrackNoteResponse(success=False, message="Failed to record note")


@router.get("/cache-stats")
async def get_cache_stats(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get cache statistics for monitoring (admin only).
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Dictionary with cache statistics
    """
    from ...core.security import check_admin
    check_admin(current_user)
    return SpecialNotesService.get_cache_stats()
