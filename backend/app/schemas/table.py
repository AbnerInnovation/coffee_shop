from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class TableBase(BaseModel):
    number: int = Field(..., gt=0)
    capacity: int = Field(..., gt=0)
    location: str = Field(..., min_length=1, max_length=50)
    is_occupied: bool = False

class TableCreate(TableBase):
    pass

class TableUpdate(BaseModel):
    number: Optional[int] = Field(None, gt=0)
    capacity: Optional[int] = Field(None, gt=0)
    location: Optional[str] = Field(None, min_length=1, max_length=50)
    is_occupied: Optional[bool] = None

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
