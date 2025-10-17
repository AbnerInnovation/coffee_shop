from .base import PhoenixBaseModel as BaseModel
from pydantic import Field, ConfigDict
from datetime import datetime
from typing import Optional

# ----------------------------
# Special Note Stats Schemas
# ----------------------------
class TopSpecialNote(BaseModel):
    """Schema for returning top special notes to the frontend."""
    note_text: str = Field(..., description="The special note text")
    usage_count: int = Field(..., description="Number of times this note has been used")
    
    model_config = ConfigDict(from_attributes=True)

class SpecialNoteStatsInDB(BaseModel):
    """Complete schema for special note stats including all fields."""
    id: int
    restaurant_id: int
    note_text: str
    usage_count: int
    last_used_at: datetime
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class TrackNoteRequest(BaseModel):
    """Request schema for tracking a special note usage."""
    note_text: str = Field(..., min_length=1, max_length=200, description="The special note to track")

class TrackNoteResponse(BaseModel):
    """Response schema for note tracking."""
    success: bool
    message: str = "Note tracked successfully"
