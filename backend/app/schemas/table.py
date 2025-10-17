from .base import PhoenixBaseModel as BaseModel
from pydantic import Field, validator
from datetime import datetime
from typing import Optional, List
from ..core.validators import validate_alphanumeric_with_spaces

class TableBase(BaseModel):
    number: int = Field(..., gt=0, le=9999, description="Table number must be between 1 and 9999")
    capacity: int = Field(..., gt=0, le=100, description="Capacity must be between 1 and 100")
    location: str = Field(..., min_length=1, max_length=50)
    is_occupied: bool = False
    
    @validator('location')
    def sanitize_location(cls, v):
        """Remove potentially dangerous characters from location."""
        return validate_alphanumeric_with_spaces(v, 'Location', allow_hyphen=True, allow_period=True)

class TableCreate(TableBase):
    pass

class TableUpdate(BaseModel):
    number: Optional[int] = Field(None, gt=0, le=9999)
    capacity: Optional[int] = Field(None, gt=0, le=100)
    location: Optional[str] = Field(None, min_length=1, max_length=50)
    is_occupied: Optional[bool] = None
    
    @validator('location')
    def sanitize_location(cls, v):
        """Remove potentially dangerous characters from location."""
        return validate_alphanumeric_with_spaces(v, 'Location', allow_hyphen=True, allow_period=True)

class TableInDBBase(TableBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class Table(TableInDBBase):
    pass

class TableInDB(TableInDBBase):
    pass
