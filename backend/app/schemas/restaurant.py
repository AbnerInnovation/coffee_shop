from .base import PhoenixBaseModel as BaseModel
from pydantic import Field, validator
from typing import Optional, Dict
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
    """Base schema for restaurant with common fields"""
    name: str = Field(..., min_length=1, max_length=100)
    subdomain: str = Field(..., min_length=3, max_length=50, pattern="^[a-z0-9-]+$")
    business_type: str = Field(default="restaurant", max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    address: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    logo_url: Optional[str] = Field(None, max_length=500)
    timezone: str = Field(default="America/Los_Angeles", max_length=50)
    currency: str = Field(default="MXN", max_length=3)
    tax_rate: Optional[float] = Field(default=0.0, ge=0, le=1)
    kitchen_print_enabled: bool = Field(default=False)
    kitchen_print_paper_width: int = Field(default=80, ge=58, le=80)
    customer_print_enabled: bool = Field(default=False)
    customer_print_paper_width: int = Field(default=80, ge=58, le=80)
    allow_dine_in_without_table: bool = Field(default=False)
    advanced_printing_enabled: bool = Field(default=False)
    payment_methods_config: Dict[str, bool] = Field(
        default={"cash": True, "card": False, "digital": True, "other": False},
        description="Payment methods configuration. Cash is always enabled."
    )
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
    
    @validator('payment_methods_config')
    def validate_payment_methods(cls, v):
        """Ensure cash is always enabled."""
        if v is not None and isinstance(v, dict):
            v['cash'] = True  # Cash is always enabled
        return v


class RestaurantCreate(RestaurantBase):
    """Schema for creating a new restaurant"""
    trial_days: Optional[int] = Field(default=14, ge=1, le=365, description="Number of trial days (1-365)")
    admin_email: Optional[str] = Field(None, max_length=100)
    plan_id: Optional[int] = Field(None, description="Subscription plan ID (if not provided, creates trial)")
    
    @validator('admin_email')
    def validate_admin_email_field(cls, v):
        """Validate admin email if provided"""
        if v:
            return validate_email(v)
        return v
    
    @validator('business_type')
    def validate_business_type(cls, v):
        """Validate business type"""
        allowed_types = ['restaurant', 'cafe', 'food_truck', 'churreria', 'bakery', 'bar', 'fast_food', 'other']
        if v not in allowed_types:
            raise ValueError(f'Business type must be one of: {", ".join(allowed_types)}')
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
    advanced_printing_enabled: Optional[bool] = None
    kitchen_print_enabled: Optional[bool] = None
    kitchen_print_paper_width: Optional[int] = Field(None, ge=58, le=80)
    customer_print_enabled: Optional[bool] = None
    customer_print_paper_width: Optional[int] = Field(None, ge=58, le=80)
    allow_dine_in_without_table: Optional[bool] = None
    payment_methods_config: Optional[Dict[str, bool]] = None
    
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
    
    @validator('payment_methods_config')
    def validate_payment_methods_update(cls, v):
        """Ensure cash is always enabled."""
        if v is not None and isinstance(v, dict):
            v['cash'] = True  # Cash is always enabled
        return v


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
    advanced_printing_enabled: bool = False
    kitchen_print_enabled: bool = True
    kitchen_print_paper_width: int = 80
    customer_print_enabled: bool = True
    customer_print_paper_width: int = 80
    allow_dine_in_without_table: bool = False
    payment_methods_config: Dict[str, bool] = {"cash": True, "card": False, "digital": True, "other": False}
    
    class Config:
        from_attributes = True


class RestaurantCreationResponse(BaseModel):
    """Response schema for restaurant creation with welcome message"""
    restaurant: Restaurant
    admin_email: str
    admin_password: str
    restaurant_url: str
    trial_days: Optional[int] = None
    trial_expires: Optional[datetime] = None
    subscription_plan: Optional[str] = None
    welcome_message: str
    shareable_message: str
