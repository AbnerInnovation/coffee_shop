from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
import logging

from ..models.menu import MenuItem as MenuItemModel, Category as CategoryModel
from ..schemas.menu import MenuItemCreate, MenuItemUpdate, Category

logger = logging.getLogger(__name__)

def get_menu_items(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    category: Optional[str] = None,
    available: Optional[bool] = None
) -> List[MenuItemModel]:
    """
    Get a list of menu items with optional filtering.
    """
    query = db.query(MenuItemModel)
    
    if category is not None:
        # Look up the category by name
        category_name = category.value.upper() if hasattr(category, 'value') else category.upper()
        category_obj = db.query(CategoryModel).filter(CategoryModel.name == category_name).first()
        if category_obj:
            query = query.filter(MenuItemModel.category_id == category_obj.id)
    
    if available is not None:
        query = query.filter(MenuItemModel.is_available == available)
    
    return query.offset(skip).limit(limit).all()

def get_menu_item(db: Session, item_id: int) -> Optional[MenuItemModel]:
    """
    Get a menu item by ID with its category loaded.
    """
    return db.query(MenuItemModel)\
        .options(joinedload(MenuItemModel.category))\
        .filter(MenuItemModel.id == item_id)\
        .first()

def create_menu_item(
    db: Session, 
    menu_item: MenuItemCreate
) -> MenuItemModel:
    """
    Create a new menu item.
    """
    # Get the data as dict
    item_data = menu_item.dict()
    
    # Look up the category by name
    category_name = item_data.pop('category_name').upper()
    category = db.query(CategoryModel).filter(CategoryModel.name == category_name).first()
    
    if not category:
        # Create the category if it doesn't exist
        category = CategoryModel(name=category_name)
        db.add(category)
        db.commit()
        db.refresh(category)
    
    # Add the category_id to the item data
    item_data['category_id'] = category.id
    
    # Create the menu item
    db_item = MenuItemModel(**item_data)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def update_menu_item(
    db: Session, 
    db_item: MenuItemModel, 
    menu_item: MenuItemUpdate
) -> MenuItemModel:
    """
    Update a menu item.
    """
    update_data = menu_item.dict(exclude_unset=True)
    
    # Handle category update if category_name is provided
    if 'category_name' in update_data:
        category_name = update_data.pop('category_name')
        # Find or create the category
        category = db.query(CategoryModel).filter(
            CategoryModel.name.ilike(category_name)
        ).first()
        
        if not category:
            # Create the category if it doesn't exist
            category = CategoryModel(name=category_name)
            db.add(category)
            db.commit()
            db.refresh(category)
            
        db_item.category_id = category.id
    # Fall back to category_id if provided
    elif 'category_id' in update_data:
        category_id = update_data.pop('category_id')
        # Verify the category exists
        category = db.query(CategoryModel).filter(CategoryModel.id == category_id).first()
        if not category:
            raise ValueError(f"Category with ID {category_id} not found")
        db_item.category_id = category_id
    
    # Update other fields
    for field, value in update_data.items():
        setattr(db_item, field, value)
    
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_menu_item(db: Session, db_item: MenuItemModel) -> None:
    """
    Delete a menu item.
    """
    db.delete(db_item)
    db.commit()

def get_categories(db: Session) -> List[str]:
    """
    Get a list of all available menu categories from the database.
    
    Returns:
        List[str]: List of unique category names
    """
    # Get all categories from the database
    categories = db.query(CategoryModel).all()
    
    # Extract unique category names
    category_names = list({category.name for category in categories})
    
    # If no categories exist, return some defaults
    if not category_names:
        category_names = [
            "COFFEE",
            "TEA",
            "BREAKFAST",
            "LUNCH",
            "DESSERTS",
            "DRINKS"
        ]
        
        # Create the default categories in the database
        for name in category_names:
            if not db.query(CategoryModel).filter_by(name=name).first():
                db.add(CategoryModel(name=name))
        db.commit()
        
    return category_names
