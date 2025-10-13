from .base import PhoenixBaseModel as BaseModel
from pydantic import Field, validator
from typing import Optional
from datetime import datetime
import re


class RestaurantBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    subdomain: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    logo_url: Optional[str] = None
    timezone: str = Field(default="America/Phoenix")
    currency: str = Field(default="USD", max_length=3)
    tax_rate: Optional[float] = Field(default=0.0, ge=0, le=1)
    is_active: bool = True
    
    @validator('subdomain')
    def validate_subdomain(cls, v):
        """Validate subdomain format (alphanumeric and hyphens only)"""
        if not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError('Subdomain must contain only lowercase letters, numbers, and hyphens')
        if v.startswith('-') or v.endswith('-'):
            raise ValueError('Subdomain cannot start or end with a hyphen')
        return v
    
    @validator('email')
    def validate_email(cls, v):
        """Basic email validation"""
        if v and '@' not in v:
            raise ValueError('Invalid email format')
        return v


class RestaurantCreate(RestaurantBase):
    """Schema for creating a new restaurant"""
    pass


class RestaurantUpdate(BaseModel):
    """Schema for updating a restaurant (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    logo_url: Optional[str] = None
    timezone: Optional[str] = None
    currency: Optional[str] = Field(None, max_length=3)
    tax_rate: Optional[float] = Field(None, ge=0, le=1)
    is_active: Optional[bool] = None


class Restaurant(RestaurantBase):
    """Schema for restaurant response"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class RestaurantPublic(BaseModel):
    """Public restaurant info (no sensitive data)"""
    id: int
    name: str
    subdomain: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    timezone: str
    currency: str
    
    class Config:
        from_attributes = True
