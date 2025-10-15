from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session, joinedload
import logging

from ..models.menu import MenuItem as MenuItemModel, Category as CategoryModel
from ..schemas.menu import MenuItemCreate, MenuItemUpdate, CategoryCreate, CategoryUpdate, Category

logger = logging.getLogger(__name__)


def get_menu_items(
    db: Session,
    restaurant_id: int,
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = None,
    available: Optional[bool] = None,
) -> List[MenuItemModel]:
    """
    Get a list of menu items with optional filtering.
    Includes variants and category in the results.
    """
    from sqlalchemy.orm import joinedload

    # Start building the query with relationships and filter out deleted items
    query = db.query(MenuItemModel).options(
        joinedload(MenuItemModel.category), 
        joinedload(MenuItemModel.variants)
    ).filter(
        MenuItemModel.deleted_at.is_(None),
        MenuItemModel.restaurant_id == restaurant_id
    )

    if category_id is not None:
        # Filter by category_id directly
        query = query.filter(MenuItemModel.category_id == category_id)

    if available is not None:
        query = query.filter(MenuItemModel.is_available == available)

    # Order by category name and then by menu item name
    query = query.join(CategoryModel).order_by(
        CategoryModel.name.asc(),
        MenuItemModel.name.asc()
    )

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


def get_menu_item(db: Session, item_id: int, restaurant_id: int) -> Optional[MenuItemModel]:
    """
    Get a non-deleted menu item by ID with its category and variants loaded.
    """
    return (
        db.query(MenuItemModel)
        .options(joinedload(MenuItemModel.category), joinedload(MenuItemModel.variants))
        .filter(
            MenuItemModel.id == item_id,
            MenuItemModel.restaurant_id == restaurant_id,
            MenuItemModel.deleted_at.is_(None)
        )
        .first()
    )


def create_menu_item(db: Session, menu_item: MenuItemCreate, restaurant_id: int) -> MenuItemModel:
    """
    Create a new menu item with its variants.
    Note: This function expects to be called within an existing transaction context.
    """
    from ..models.menu import MenuItemVariant as MenuItemVariantModel
    
    logger.info(f"Creating menu item with data: {menu_item}")
    logger.info(f"Variants data: {menu_item.variants if hasattr(menu_item, 'variants') else 'No variants'}")

    # Get the data as dict, excluding variants and category
    item_data = menu_item.dict(exclude={"variants", "category"}, exclude_unset=True)
    logger.info(f"Item data (excluding variants and category): {item_data}")

    # Look up the category by name within the same restaurant
    category_name = menu_item.category.upper()
    logger.info(f"Looking up category: {category_name}")
    
    category = db.query(CategoryModel).filter(
        CategoryModel.name == category_name,
        CategoryModel.restaurant_id == restaurant_id,
        CategoryModel.deleted_at.is_(None)
    ).first()

    if not category:
        logger.info(f"Creating new category: {category_name}")
        category = CategoryModel(name=category_name, restaurant_id=restaurant_id)
        db.add(category)
        db.flush()

    # Add the category_id to the item data
    item_data["category_id"] = category.id
    logger.info(f"Using category ID: {category.id}")

    try:
        # Create the menu item
        db_item = MenuItemModel(**item_data, restaurant_id=restaurant_id)
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
    menu_item: MenuItemUpdate,
    restaurant_id: int
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
        .filter(
            MenuItemModel.id == item_id,
            MenuItemModel.restaurant_id == restaurant_id
        )
        .first()
    )
    if db_item is None:
        raise ValueError(f"Menu item with ID {item_id} not found")

    data = menu_item.dict(exclude_unset=True)
    variants_data = data.pop("variants", None)

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
        # Only consider non-deleted variants
        existing_variants = {v.id: v for v in db_item.variants if v.deleted_at is None}
        sent_variant_ids = set()

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
                # Create new variant (only if it doesn't have an id or the id doesn't exist)
                new_variant_data = {k: v for k, v in variant_data.items() if k != "id"}
                new_variant_data["menu_item_id"] = db_item.id
                new_variant = MenuItemVariantModel(**new_variant_data)
                db.add(new_variant)

        # Soft delete variants that were not included
        for variant in db_item.variants:
            if variant.deleted_at is None and variant.id not in sent_variant_ids:
                variant.deleted_at = datetime.now(timezone.utc)
                db.add(variant)

    db.commit()
    db.refresh(db_item)  # Make sure relationships are updated
    return db_item


def delete_menu_item(db: Session, db_item: MenuItemModel) -> None:
    """
    Soft delete a menu item by setting the deleted_at timestamp.
    Note: This function expects to be called within an existing transaction context.
    """
    db_item.deleted_at = datetime.now(timezone.utc)
    db.add(db_item)


def get_categories(db: Session, restaurant_id: int) -> List[CategoryModel]:
    """
    Get a list of all available menu categories from the database.

    Returns:
        List[CategoryModel]: List of category objects (excluding soft deleted ones)
    """
    # Get all categories from the database (excluding soft deleted ones)
    categories = db.query(CategoryModel).filter(
        CategoryModel.deleted_at.is_(None),
        CategoryModel.restaurant_id == restaurant_id
    ).all()

    # If no categories exist, return some defaults
    if not categories:
        category_names = ["COFFEE", "TEA", "BREAKFAST", "LUNCH", "DESSERTS", "DRINKS"]

        # Create the default categories in the database
        for name in category_names:
            if not db.query(CategoryModel).filter_by(name=name, restaurant_id=restaurant_id, deleted_at=None).first():
                db.add(CategoryModel(name=name, restaurant_id=restaurant_id))
        db.commit()

        # Fetch the newly created categories
        categories = db.query(CategoryModel).filter(
            CategoryModel.deleted_at.is_(None),
            CategoryModel.restaurant_id == restaurant_id
        ).all()

    return categories


def get_category(db: Session, category_id: int, restaurant_id: int) -> Optional[CategoryModel]:
    """
    Get a specific category by ID.

    Args:
        db: Database session
        category_id: Category ID

    Returns:
        CategoryModel or None if not found
    """
    return db.query(CategoryModel).filter(
        CategoryModel.id == category_id,
        CategoryModel.restaurant_id == restaurant_id,
        CategoryModel.deleted_at.is_(None)
    ).first()


def create_category(db: Session, category_data: CategoryCreate, restaurant_id: int) -> CategoryModel:
    """
    Create a new category.

    Args:
        db: Database session
        category_data: Category creation data

    Returns:
        CategoryModel: The created category
    """
    # Check if category with this name already exists
    existing_category = db.query(CategoryModel).filter(
        CategoryModel.name == category_data.name.upper(),
        CategoryModel.restaurant_id == restaurant_id,
        CategoryModel.deleted_at.is_(None)
    ).first()

    if existing_category:
        raise ValueError(f"Category with name '{category_data.name}' already exists")

    # Create new category
    db_category = CategoryModel(
        name=category_data.name.upper(),
        description=category_data.description,
        restaurant_id=restaurant_id
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)

    return db_category


def update_category(
    db: Session,
    category_id: int,
    category_data: CategoryUpdate,
    restaurant_id: int
) -> Optional[CategoryModel]:
    """
    Update a category.

    Args:
        db: Database session
        category_id: Category ID
        category_data: Category update data

    Returns:
        CategoryModel or None if not found
    """
    db_category = db.query(CategoryModel).filter(
        CategoryModel.id == category_id,
        CategoryModel.restaurant_id == restaurant_id,
        CategoryModel.deleted_at.is_(None)
    ).first()

    if not db_category:
        return None

    # Check if new name conflicts with existing category (if name is being updated)
    if category_data.name and category_data.name != db_category.name:
        existing_category = db.query(CategoryModel).filter(
            CategoryModel.name == category_data.name.upper(),
            CategoryModel.id != category_id,
            CategoryModel.restaurant_id == restaurant_id,
            CategoryModel.deleted_at.is_(None)
        ).first()

        if existing_category:
            raise ValueError(f"Category with name '{category_data.name}' already exists")

        db_category.name = category_data.name.upper()

    if category_data.description is not None:
        db_category.description = category_data.description

    db.commit()
    db.refresh(db_category)

    return db_category


def delete_category(db: Session, category_id: int, restaurant_id: int) -> bool:
    """
    Delete a category. Only allow deletion if no menu items are using it.

    Args:
        db: Database session
        category_id: Category ID

    Returns:
        bool: True if deleted, False if not found or has dependencies
    """
    db_category = db.query(CategoryModel).filter(
        CategoryModel.id == category_id,
        CategoryModel.deleted_at.is_(None)
    ).first()

    if not db_category:
        return False

    # Check if any menu items are using this category
    menu_items_count = db.query(MenuItemModel).filter(
        MenuItemModel.category_id == category_id,
        MenuItemModel.deleted_at.is_(None)
    ).count()

    if menu_items_count > 0:
        raise ValueError(f"Cannot delete category '{db_category.name}' because it has {menu_items_count} menu items")

    # Soft delete by setting deleted_at timestamp
    db_category.deleted_at = datetime.now(timezone.utc)
    db.add(db_category)
    db.commit()

    return True
