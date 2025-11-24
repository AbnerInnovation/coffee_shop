from .base import PhoenixBaseModel as BaseModel
from pydantic import Field, validator
from typing import Optional
from datetime import datetime
from ..core.validators import (
    sanitize_text,
    validate_subdomain,
    validate_phone,
    validate_email,
    validate_url,
    validate_currency_code
)


class RestaurantBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    subdomain: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=1000)
    address: Optional[str] = Field(None, max_length=500)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    logo_url: Optional[str] = Field(None, max_length=500)
    timezone: str = Field(default="America/Phoenix", max_length=100)
    currency: str = Field(default="USD", max_length=3)
    tax_rate: Optional[float] = Field(default=0.0, ge=0, le=1)
    is_active: bool = True
    
    @validator('name')
    def sanitize_name(cls, v):
        """Remove potentially dangerous characters from restaurant name."""
        return sanitize_text(v)
    
    @validator('subdomain')
    def validate_subdomain_field(cls, v):
        """Validate subdomain format (alphanumeric and hyphens only)"""
        return validate_subdomain(v)
    
    @validator('description')
    def sanitize_description(cls, v):
        """Remove potentially dangerous characters from description."""
        return sanitize_text(v)
    
    @validator('address')
    def sanitize_address(cls, v):
        """Remove potentially dangerous characters from address."""
        return sanitize_text(v)
    
    @validator('phone')
    def validate_phone_field(cls, v):
        """Validate phone number format."""
        return validate_phone(v)
    
    @validator('email')
    def validate_email_field(cls, v):
        """Enhanced email validation"""
        return validate_email(v)
    
    @validator('logo_url')
    def validate_logo_url(cls, v):
        """Validate logo URL format."""
        return validate_url(v, 'Logo URL')
    
    @validator('currency')
    def validate_currency_field(cls, v):
        """Validate currency code format."""
        return validate_currency_code(v)


class RestaurantCreate(RestaurantBase):
    """Schema for creating a new restaurant"""
    trial_days: Optional[int] = Field(default=14, ge=1, le=365, description="Number of trial days (1-365)")
    admin_email: Optional[str] = Field(None, max_length=100)
    
    @validator('admin_email')
    def validate_admin_email_field(cls, v):
        """Validate admin email if provided"""
        if v:
            return validate_email(v)
        return v


class RestaurantUpdate(BaseModel):
    """Schema for updating a restaurant (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    address: Optional[str] = Field(None, max_length=500)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    logo_url: Optional[str] = Field(None, max_length=500)
    timezone: Optional[str] = Field(None, max_length=100)
    currency: Optional[str] = Field(None, max_length=3)
    tax_rate: Optional[float] = Field(None, ge=0, le=1)
    is_active: Optional[bool] = None
    
    @validator('name')
    def sanitize_name(cls, v):
        """Remove potentially dangerous characters from restaurant name."""
        return sanitize_text(v)
    
    @validator('description')
    def sanitize_description(cls, v):
        """Remove potentially dangerous characters from description."""
        return sanitize_text(v)
    
    @validator('address')
    def sanitize_address(cls, v):
        """Remove potentially dangerous characters from address."""
        return sanitize_text(v)
    
    @validator('phone')
    def validate_phone_field(cls, v):
        """Validate phone number format."""
        return validate_phone(v)
    
    @validator('email')
    def validate_email_field(cls, v):
        """Enhanced email validation"""
        return validate_email(v)
    
    @validator('logo_url')
    def validate_logo_url(cls, v):
        """Validate logo URL format."""
        return validate_url(v, 'Logo URL')
    
    @validator('currency')
    def validate_currency_field(cls, v):
        """Validate currency code format."""
        return validate_currency_code(v)


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
    kitchen_print_enabled: bool = True
    kitchen_print_paper_width: int = 80
    
    class Config:
        from_attributes = True


class RestaurantCreationResponse(BaseModel):
    """Response schema for restaurant creation with welcome message"""
    restaurant: Restaurant
    admin_email: str
    admin_password: str
    restaurant_url: str
    trial_days: int
    trial_expires: datetime
    welcome_message: str
    shareable_message: str
