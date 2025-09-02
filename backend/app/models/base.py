from sqlalchemy.orm import declarative_base, declared_attr
from sqlalchemy import Column, Integer, DateTime, inspect
from datetime import datetime
from typing import Any, Dict, Type, TypeVar, Optional

# Global Base used by all models
Base = declarative_base()

T = TypeVar('T', bound='BaseModel')

class BaseModel:
    """
    Mixin for all database models.
    Provides common columns and functionality.
    """
    __abstract__ = True   # <-- important, prevents SQLAlchemy from treating this as a real table
    __name__: str  # Helps with type checking

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    @declared_attr
    def __tablename__(cls) -> str:
        """Generate __tablename__ automatically."""
        return f"{cls.__name__.lower()}s"

    def update_from_dict(self, **kwargs: Any) -> None:
        """Update model attributes from a dictionary."""
        for key, value in kwargs.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)
