from sqlalchemy import Integer, String, Boolean, Column
from sqlalchemy.orm import relationship
from .base import BaseModel
from ..db.base import Base

class Table(Base, BaseModel):
    __tablename__ = "tables"
    
    number = Column(Integer, unique=True, nullable=False)
    capacity = Column(Integer, nullable=False)
    location = Column(String(50), nullable=False)
    is_occupied = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    orders = relationship("Order", back_populates="table", cascade="all, delete-orphan")
