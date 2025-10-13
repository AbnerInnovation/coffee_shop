from sqlalchemy.orm import declared_attr
from sqlalchemy import Column, Integer, DateTime, inspect
from datetime import datetime, timezone
from typing import Any, Dict, Type, TypeVar, Optional
from ..db.base import Base  # Import the Base from db.base

T = TypeVar('T', bound='BaseModel')

class BaseModel(Base):
    """
    Mixin for all database models.
    Provides common columns and functionality.
    """
    __abstract__ = True   # Prevents SQLAlchemy from treating this as a real table
    __name__: str  # Helps with type checking
    
    # Ensure these columns are properly typed for SQLAlchemy 2.0
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Columns are now defined in the class body above

    @declared_attr
    def __tablename__(cls) -> str:
        """Generate __tablename__ automatically."""
        return f"{cls.__name__.lower()}s"

    def update_from_dict(self, **kwargs: Any) -> None:
        """Update model attributes from a dictionary."""
        for key, value in kwargs.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)
