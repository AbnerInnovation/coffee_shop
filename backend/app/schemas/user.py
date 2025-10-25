from .base import PhoenixBaseModel as BaseModel
from pydantic import EmailStr, Field, validator
from datetime import datetime
from typing import Optional
from enum import Enum
from ..core.validators import validate_name, validate_password_strength

class UserRole(str, Enum):
    SYSADMIN = "sysadmin"
    ADMIN = "admin"
    STAFF = "staff"
    CUSTOMER = "customer"

class StaffType(str, Enum):
    WAITER = "waiter"      # Mesero: Crear/editar pedidos, gestionar mesas
    CASHIER = "cashier"    # Cajero: Procesar pagos, acceder a caja registradora
    KITCHEN = "kitchen"    # Cocina: Ver pedidos de cocina, marcar items preparados
    GENERAL = "general"    # General: Solo lectura

class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)
    role: UserRole = UserRole.STAFF
    staff_type: Optional[StaffType] = None
    is_active: bool = True
    restaurant_id: Optional[int] = None
    
    @validator('full_name')
    def validate_full_name(cls, v):
        """Validate and sanitize full name."""
        return validate_name(v, 'Full name')

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength."""
        if v:
            return validate_password_strength(v)
        return v

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    role: Optional[UserRole] = None
    staff_type: Optional[StaffType] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=8, max_length=100)
    
    @validator('full_name')
    def validate_full_name(cls, v):
        """Validate and sanitize full name."""
        return validate_name(v, 'Full name')
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength."""
        if v:
            return validate_password_strength(v)
        return v

class UserInDBBase(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    hashed_password: str

class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @validator('new_password')
    def validate_new_password(cls, v):
        """Validate new password strength."""
        return validate_password_strength(v)
