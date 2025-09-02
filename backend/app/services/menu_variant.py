from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from ..models.menu import MenuItemVariant, MenuItem
from ..schemas.menu import MenuItemVariantCreate, MenuItemVariantUpdate

logger = logging.getLogger(__name__)

def get_variants(
    db: Session,
    menu_item_id: int,
    skip: int = 0,
    limit: int = 100,
    available: Optional[bool] = None
) -> List[MenuItemVariant]:
    """
    Get all variants for a menu item with optional filtering.
    """
    query = db.query(MenuItemVariant).filter(
        MenuItemVariant.menu_item_id == menu_item_id
    )
    
    if available is not None:
        query = query.filter(MenuItemVariant.is_available == available)
    
    return query.offset(skip).limit(limit).all()

def get_variant(
    db: Session,
    variant_id: int,
    menu_item_id: Optional[int] = None
) -> Optional[MenuItemVariant]:
    """
    Get a specific variant by ID, optionally filtered by menu item ID.
    """
    query = db.query(MenuItemVariant).filter(
        MenuItemVariant.id == variant_id
    )
    
    if menu_item_id is not None:
        query = query.filter(MenuItemVariant.menu_item_id == menu_item_id)
    
    return query.first()

def create_variant(
    db: Session,
    variant: MenuItemVariantCreate,
    menu_item_id: int
) -> MenuItemVariant:
    """
    Create a new variant for a menu item.
    Note: This function expects to be called within an existing transaction context.
    """
    # Verify the menu item exists
    menu_item = db.query(MenuItem).filter(MenuItem.id == menu_item_id).first()
    if not menu_item:
        raise ValueError(f"Menu item with ID {menu_item_id} not found")
    
    db_variant = MenuItemVariant(
        **variant.dict(),
        menu_item_id=menu_item_id
    )
    db.add(db_variant)
    db.flush()  # Flush to get the ID without committing
    db.refresh(db_variant)
    return db_variant

def update_variant(
    db: Session,
    db_variant: MenuItemVariant,
    variant: MenuItemVariantUpdate
) -> MenuItemVariant:
    """
    Update an existing variant.
    Note: This function expects to be called within an existing transaction context.
    """
    update_data = variant.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_variant, field, value)
        
    db.add(db_variant)
    db.flush()  # Flush changes without committing
    db.refresh(db_variant)
    return db_variant

def delete_variant(
    db: Session,
    db_variant: MenuItemVariant
) -> bool:
    """
    Delete a variant.
    Note: This function expects to be called within an existing transaction context.
    """
    db.delete(db_variant)
    db.flush()  # Flush the deletion without committing
    return True
