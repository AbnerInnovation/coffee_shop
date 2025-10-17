from sqlalchemy import String, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import TYPE_CHECKING
from datetime import datetime, timezone
from .base import BaseModel

if TYPE_CHECKING:
    from .restaurant import Restaurant

class SpecialNoteStats(BaseModel):
    """
    Tracks usage statistics for special notes/instructions to provide
    intelligent suggestions to users based on most frequently used notes.
    
    This enables the "Top 3 most requested notes" feature for quick access.
    """
    __tablename__ = "special_note_stats"
    
    # Foreign key to restaurant for multi-tenant support
    restaurant_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("restaurants.id"), 
        nullable=False, 
        index=True
    )
    
    # The actual note text (e.g., "Sin Cebolla", "Extra salsa", "Tortilla Maíz")
    note_text: Mapped[str] = mapped_column(String(200), nullable=False)
    
    # Number of times this note has been used
    usage_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    # Last time this note was used (for cleanup of old/unused notes)
    last_used_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    
    # Relationships
    restaurant: Mapped["Restaurant"] = relationship("Restaurant")
    
    # Ensure unique combination of restaurant_id and note_text
    __table_args__ = (
        UniqueConstraint('restaurant_id', 'note_text', name='uq_restaurant_note'),
    )
    
    def __repr__(self) -> str:
        return f"<SpecialNoteStats(id={self.id}, restaurant_id={self.restaurant_id}, note='{self.note_text}', count={self.usage_count})>"
