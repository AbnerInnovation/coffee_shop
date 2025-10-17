from .base import PhoenixBaseModel as BaseModel
from pydantic import Field, ConfigDict, validator
from enum import Enum
from typing import Optional, List, Union, Any
from datetime import datetime
from ..models.menu import Category as CategoryModel
from pydantic_core import core_schema
from pydantic import GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from ..core.validators import sanitize_text, validate_url, validate_discount_price

# ----------------------------
# Category Schemas
# ----------------------------
class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    
    @validator('name')
    def sanitize_name(cls, v):
        """Remove potentially dangerous characters from category name."""
        return sanitize_text(v)
    
    @validator('description')
    def sanitize_description(cls, v):
        """Remove potentially dangerous characters from description."""
        return sanitize_text(v)

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    name: Optional[str] = Field(None, min_length=1, max_length=50)

class CategoryInDB(CategoryBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# ----------------------------
# Category Enum
# ----------------------------
class Category(str, Enum):
    COFFEE = "COFFEE"
    TEA = "TEA"
    PASTRY = "PASTRY"
    SANDWICH = "SANDWICH"
    DESSERT = "DESSERT"
    OTHER = "OTHER"

    @classmethod
    def _missing_(cls, value):
        if not isinstance(value, str):
            return None
        value = value.upper()
        for member in cls:
            if member.value.upper() == value:
                return member
        return None

    @classmethod
    def _validate(cls, value):
        if isinstance(value, cls):
            return value
        try:
            if isinstance(value, str):
                value = value.upper()
            return cls(value)
        except ValueError:
            raise ValueError(f"'{value}' is not a valid {cls.__name__}")

    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type: Any, _handler: Any) -> core_schema.CoreSchema:
        def validate(value: Union[str, 'Category']) -> 'Category':
            return cls._validate(value)
        from_str_schema = core_schema.chain_schema([
            core_schema.str_schema(),
            core_schema.no_info_plain_validator_function(validate)
        ])
        return core_schema.json_or_python_schema(
            json_schema=core_schema.union_schema([
                core_schema.literal_schema([x.value for x in cls]),
                from_str_schema
            ]),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(cls),
                from_str_schema
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(lambda x: x.value)
        )

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler) -> JsonSchemaValue:
        return {
            'enum': [e.value for e in cls],
            'title': cls.__name__,
        }

    def __str__(self):
        return self.value

# ----------------------------
# MenuItem Variant Schemas
# ----------------------------
class MenuItemVariantBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    price: float = Field(..., le=999999.99, description="Price must be positive and less than 1 million")
    discount_price: Optional[float] = Field(None, ge=0, le=999999.99, description="Discount price must be non-negative")
    is_available: bool = True
    
    @validator('name')
    def sanitize_name(cls, v):
        """Remove potentially dangerous characters from variant name."""
        return sanitize_text(v)
    
    @validator('discount_price')
    def validate_discount_price_field(cls, v, values):
        """Ensure discount price is less than regular price."""
        if 'price' in values:
            return validate_discount_price(v, values['price'])
        return v

class MenuItemVariantCreate(MenuItemVariantBase):
    pass

class MenuItemVariantUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    price: Optional[float] = Field(None, le=999999.99)
    discount_price: Optional[float] = Field(None, ge=0, le=999999.99)
    is_available: Optional[bool] = None
    
    @validator('name')
    def sanitize_name(cls, v):
        """Remove potentially dangerous characters from variant name."""
        return sanitize_text(v)

class MenuItemVariantInDBBase(MenuItemVariantBase):
    id: int
    menu_item_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class MenuItemVariant(MenuItemVariantInDBBase):
    pass

class MenuItemVariantInDB(MenuItemVariantInDBBase):
    pass

# ----------------------------
# MenuItem Schemas
# ----------------------------
class MenuItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    price: float = Field(..., le=999999.99, description="Price must be positive and less than 1 million")
    discount_price: Optional[float] = Field(None, ge=0, le=999999.99, description="Discount price must be non-negative")
    is_available: bool = True
    image_url: Optional[str] = Field(None, max_length=500)

    model_config = ConfigDict(
        use_enum_values=True,
        json_encoders={Category: lambda v: v.value if v else None}
    )
    
    @validator('name')
    def sanitize_name(cls, v):
        """Remove potentially dangerous characters from menu item name."""
        return sanitize_text(v)
    
    @validator('description')
    def sanitize_description(cls, v):
        """Remove potentially dangerous characters from description."""
        return sanitize_text(v)
    
    @validator('image_url')
    def validate_image_url(cls, v):
        """Validate image URL format."""
        return validate_url(v, 'Image URL')
    
    @validator('discount_price')
    def validate_discount_price_field(cls, v, values):
        """Ensure discount price is less than regular price."""
        if 'price' in values:
            return validate_discount_price(v, values['price'])
        return v

class MenuItemCreate(MenuItemBase):
    category: str = Field(..., min_length=1, max_length=50)
    variants: List['MenuItemVariantCreate'] = []

class MenuItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    price: Optional[float] = Field(None, le=999999.99)
    discount_price: Optional[float] = Field(None, ge=0, le=999999.99)
    category_id: Optional[int] = Field(None, ge=1)
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    is_available: Optional[bool] = None
    image_url: Optional[str] = Field(None, max_length=500)
    variants: List['MenuItemVariantCreate'] = []
    
    @validator('name')
    def sanitize_name(cls, v):
        """Remove potentially dangerous characters from menu item name."""
        return sanitize_text(v)
    
    @validator('description')
    def sanitize_description(cls, v):
        """Remove potentially dangerous characters from description."""
        return sanitize_text(v)
    
    @validator('image_url')
    def validate_image_url(cls, v):
        """Validate image URL format."""
        return validate_url(v, 'Image URL')

class MenuItemInDBBase(MenuItemBase):
    id: int
    category_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class MenuItem(MenuItemInDBBase):
    category: Optional[CategoryInDB] = None
    variants: List['MenuItemVariant'] = []

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm(cls, obj):
        from sqlalchemy import inspect
        obj_dict = {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}
        if hasattr(obj, 'category') and obj.category:
            obj_dict['category'] = CategoryInDB(
                id=obj.category.id,
                name=obj.category.name,
                description=obj.category.description,
                created_at=getattr(obj.category, 'created_at', None),
                updated_at=getattr(obj.category, 'updated_at', None)
            )
        if hasattr(obj, 'variants') and obj.variants is not None:
            obj_dict['variants'] = [MenuItemVariant.from_orm(v) for v in obj.variants]
        return cls(**obj_dict)

class MenuItemInDB(MenuItemInDBBase):
    pass

# ----------------------------
# Rebuild models to resolve forward references
# ----------------------------
MenuItemVariant.model_rebuild()
MenuItemVariantCreate.model_rebuild()
MenuItemVariantUpdate.model_rebuild()
MenuItemVariantInDB.model_rebuild()
MenuItemVariantInDBBase.model_rebuild()
MenuItemCreate.model_rebuild()
MenuItemUpdate.model_rebuild()
MenuItem.model_rebuild()
