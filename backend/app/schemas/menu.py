from pydantic import BaseModel, Field, validator, ConfigDict
from enum import Enum
from typing import Optional, List, Union, Any
from datetime import datetime
from ..models.menu import Category as CategoryModel

# Category schemas
class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    name: Optional[str] = Field(None, min_length=1, max_length=50)

class CategoryInDB(CategoryBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)

from pydantic import GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema

# Use the same enum from models for consistency
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
            # Convert any case to uppercase and get the enum member
            if isinstance(value, str):
                value = value.upper()
            return cls(value)
        except ValueError:
            raise ValueError(f"'{value}' is not a valid {cls.__name__}")
    
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: Any,
    ) -> core_schema.CoreSchema:
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
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: x.value
            ),
        )
    
    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return {
            'enum': [e.value for e in cls],
            'title': cls.__name__,
        }
    
    def __str__(self):
        return self.value

class MenuItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    is_available: bool = True
    image_url: Optional[str] = None

    model_config = ConfigDict(
        use_enum_values=True,
        json_encoders={
            Category: lambda v: v.value if v else None,
        }
    )

class MenuItemCreate(MenuItemBase):
    category: str = Field(..., min_length=1, max_length=50)
    variants: List['MenuItemVariantCreate'] = []

class MenuItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    category_id: Optional[int] = None
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    is_available: Optional[bool] = None
    image_url: Optional[str] = None
    variants: List['MenuItemVariantCreate'] = []

class MenuItemInDBBase(MenuItemBase):
    id: int
    category_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class MenuItem(MenuItemInDBBase):
    """Menu item with category and variants relationship."""
    category: Optional[CategoryInDB] = None
    variants: List['MenuItemVariant'] = []
    
    model_config = ConfigDict(from_attributes=True)
    
    @classmethod
    def from_orm(cls, obj):
        from sqlalchemy import inspect
        # Convert the SQLAlchemy model to a dictionary
        obj_dict = {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}
        
        # Handle the category relationship if it's loaded
        if hasattr(obj, 'category') and obj.category:
            obj_dict['category'] = CategoryInDB(
                id=obj.category.id,
                name=obj.category.name,
                description=obj.category.description,
                created_at=obj.category.created_at,
                updated_at=obj.category.updated_at
            )
        
        # Handle variants if they're loaded
        if hasattr(obj, 'variants') and obj.variants is not None:
            obj_dict['variants'] = [MenuItemVariant.from_orm(v) for v in obj.variants]
        
        # Create the model instance
        return cls(**obj_dict)

class MenuItemInDB(MenuItemInDBBase):
    pass

# Variant schemas
class MenuItemVariantBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    price: float = Field(..., gt=0)
    is_available: bool = True

class MenuItemVariantCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    price: float = Field(..., gt=0)
    is_available: bool = True

class MenuItemVariantUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    price: Optional[float] = Field(None, gt=0)
    is_available: Optional[bool] = None

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

# Rebuild models to resolve forward references used in type annotations
# This is required by Pydantic v2 when using string-based forward refs
MenuItemVariant.model_rebuild()
MenuItemVariantCreate.model_rebuild()
MenuItemVariantUpdate.model_rebuild()
MenuItemVariantInDB.model_rebuild()
MenuItemVariantInDBBase.model_rebuild()
