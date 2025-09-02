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
    available: Optional[bool] = None,
) -> List[MenuItemModel]:
    """
    Get a list of menu items with optional filtering.
    Includes variants and category in the results.
    """
    from sqlalchemy.orm import joinedload

    # Start building the query with relationships
    query = db.query(MenuItemModel).options(
        joinedload(MenuItemModel.category), joinedload(MenuItemModel.variants)
    )

    if category is not None:
        # Look up the category by name
        category_name = (
            category.value.upper() if hasattr(category, "value") else category.upper()
        )
        category_obj = (
            db.query(CategoryModel).filter(CategoryModel.name == category_name).first()
        )
        if category_obj:
            query = query.filter(MenuItemModel.category_id == category_obj.id)

    if available is not None:
        query = query.filter(MenuItemModel.is_available == available)

    # Execute the query and get results
    items = query.offset(skip).limit(limit).all()

    # Ensure we have unique items (joinedload can cause duplicates)
    seen = set()
    unique_items = []
    for item in items:
        if item.id not in seen:
            seen.add(item.id)
            unique_items.append(item)

    return unique_items


def get_menu_item(db: Session, item_id: int) -> Optional[MenuItemModel]:
    """
    Get a menu item by ID with its category and variants loaded.
    """
    from sqlalchemy.orm import joinedload

    return (
        db.query(MenuItemModel)
        .options(joinedload(MenuItemModel.category), joinedload(MenuItemModel.variants))
        .filter(MenuItemModel.id == item_id)
        .first()
    )


def create_menu_item(db: Session, menu_item: MenuItemCreate) -> MenuItemModel:
    """
    Create a new menu item with its variants.
    Note: This function expects to be called within an existing transaction context.
    """
    from ..models.menu import MenuItemVariant as MenuItemVariantModel
    
    logger.info(f"Creating menu item with data: {menu_item}")
    logger.info(f"Variants data: {menu_item.variants if hasattr(menu_item, 'variants') else 'No variants'}")

    # Get the data as dict
    item_data = menu_item.dict(exclude={"variants"}, exclude_unset=True)
    logger.info(f"Item data (excluding variants): {item_data}")

    # Look up the category by name
    category_name = menu_item.category.upper()
    logger.info(f"Looking up category: {category_name}")
    
    category = db.query(CategoryModel).filter(CategoryModel.name == category_name).first()

    if not category:
        logger.info(f"Creating new category: {category_name}")
        category = CategoryModel(name=category_name)
        db.add(category)
        db.flush()

    # Add the category_id to the item data
    item_data["category_id"] = category.id
    logger.info(f"Using category ID: {category.id}")

    try:
        # Create the menu item
        db_item = MenuItemModel(**item_data)
        db.add(db_item)
        db.flush()
        logger.info(f"Created menu item with ID: {db_item.id}")

        # Process variants if any
        if hasattr(menu_item, 'variants') and menu_item.variants:
            logger.info(f"Processing {len(menu_item.variants)} variants")
            for i, variant_data in enumerate(menu_item.variants, 1):
                variant_dict = variant_data.dict()
                variant_dict["menu_item_id"] = db_item.id
                logger.info(f"Creating variant {i}: {variant_dict}")
                
                # Create the variant
                variant = MenuItemVariantModel(**variant_dict)
                db.add(variant)
                db.flush()
                logger.info(f"Created variant with ID: {variant.id}")
        else:
            logger.info("No variants to process")

        # Refresh the item to get the relationships
        db.refresh(db_item)
        db.refresh(db_item, ['variants'])  # Ensure variants are loaded
        
        if hasattr(db_item, 'variants'):
            logger.info(f"Successfully created menu item with {len(db_item.variants)} variants")
        else:
            logger.warning("Menu item created but variants not loaded")
            
        return db_item

    except Exception as e:
        logger.error(f"Error creating menu item: {str(e)}", exc_info=True)
        raise


def update_menu_item(
    db: Session,
    item_id: int,
    menu_item: MenuItemUpdate
) -> MenuItemModel:
    """
    Update a menu item and its variants.
    This function should be called within an existing transaction/session.
    """
    from ..models.menu import MenuItemVariant as MenuItemVariantModel
    from sqlalchemy.orm import joinedload

    # Load the menu item with its category and variants
    db_item = (
        db.query(MenuItemModel)
        .options(joinedload(MenuItemModel.category), joinedload(MenuItemModel.variants))
        .filter(MenuItemModel.id == item_id)
        .first()
    )
    if db_item is None:
        raise ValueError(f"Menu item with ID {item_id} not found")

    data = menu_item.dict(exclude_unset=True)
    print('Data-------------------------->', data)
    variants_data = data.pop("variants", None)
    print('Variants data-------------------------->', variants_data)

    # --- Handle category update ---
    if "category" in data:
        category_name = data.pop("category")
        category = db.query(CategoryModel).filter(CategoryModel.name.ilike(category_name)).first()
        if not category:
            category = CategoryModel(name=category_name.upper())
            db.add(category)
            db.commit()  # Commit so category ID is available
            db.refresh(category)
        db_item.category_id = category.id
    elif "category_id" in data:
        category_id = data.pop("category_id")
        category = db.query(CategoryModel).filter(CategoryModel.id == category_id).first()
        if not category:
            raise ValueError(f"Category with ID {category_id} not found")
        db_item.category_id = category_id

    # --- Update menu item fields ---
    for field, value in data.items():
        setattr(db_item, field, value)

    db.add(db_item)

    # --- Handle variants ---
    if variants_data is not None:
        existing_variants = {v.id: v for v in db_item.variants}
        sent_variant_ids = set()

        print('Variants data-------------------------->', variants_data)
        for variant_data in variants_data:
            variant_id = variant_data.get("id")
            if variant_id and variant_id in existing_variants:
                # Update existing variant
                variant = existing_variants[variant_id]
                for field, value in variant_data.items():
                    if field != "id" and hasattr(variant, field):
                        setattr(variant, field, value)
                db.add(variant)
                sent_variant_ids.add(variant_id)
            else:
                # Create new variant
                variant_data["menu_item_id"] = db_item.id
                new_variant = MenuItemVariantModel(**variant_data)
                db.add(new_variant)

        # Delete variants that were not included
        for variant in db_item.variants:
            if variant.id not in sent_variant_ids:
                db.delete(variant)

    db.commit()
    db.refresh(db_item)  # Make sure relationships are updated
    return db_item


def delete_menu_item(db: Session, db_item: MenuItemModel) -> None:
    """
    Delete a menu item.
    Note: This function expects to be called within an existing transaction context.
    """
    db.delete(db_item)


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
        category_names = ["COFFEE", "TEA", "BREAKFAST", "LUNCH", "DESSERTS", "DRINKS"]

        # Create the default categories in the database
        for name in category_names:
            if not db.query(CategoryModel).filter_by(name=name).first():
                db.add(CategoryModel(name=name))
        db.commit()

    return category_names
