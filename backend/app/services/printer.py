"""
Service layer for Printer operations
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.printer import Printer, PrinterType
from app.models.menu import Category
from app.schemas.printer import PrinterCreate, PrinterUpdate
from app.core.exceptions import ResourceNotFoundError, ValidationError, ConflictError


def get_printer_by_id(db: Session, printer_id: int, restaurant_id: int) -> Optional[Printer]:
    """Get a printer by ID for a specific restaurant"""
    from sqlalchemy.orm import joinedload
    return db.query(Printer).options(
        joinedload(Printer.categories)
    ).filter(
        Printer.id == printer_id,
        Printer.restaurant_id == restaurant_id,
        Printer.deleted_at.is_(None)
    ).first()


def get_printers_by_restaurant(
    db: Session,
    restaurant_id: int,
    printer_type: Optional[PrinterType] = None,
    is_active: Optional[bool] = None
) -> List[Printer]:
    """Get all printers for a restaurant with optional filters"""
    from sqlalchemy.orm import joinedload
    query = db.query(Printer).options(
        joinedload(Printer.categories)
    ).filter(
        Printer.restaurant_id == restaurant_id,
        Printer.deleted_at.is_(None)
    )
    
    if printer_type:
        query = query.filter(Printer.printer_type == printer_type)
    
    if is_active is not None:
        query = query.filter(Printer.is_active == is_active)
    
    return query.order_by(Printer.printer_type, Printer.name).all()


def get_printers_by_category(db: Session, category_id: int, restaurant_id: int) -> List[Printer]:
    """Get all printers assigned to a specific category"""
    return db.query(Printer).join(
        Printer.categories
    ).filter(
        Category.id == category_id,
        Printer.restaurant_id == restaurant_id,
        Printer.deleted_at.is_(None),
        Printer.is_active == True
    ).all()


def create_printer(db: Session, printer_data: PrinterCreate, restaurant_id: int) -> Printer:
    """Create a new printer"""
    # If this printer is set as default, unset other defaults of the same type
    if printer_data.is_default:
        db.query(Printer).filter(
            Printer.restaurant_id == restaurant_id,
            Printer.printer_type == printer_data.printer_type,
            Printer.is_default == True,
            Printer.deleted_at.is_(None)
        ).update({"is_default": False})
    
    # Create printer
    printer_dict = printer_data.dict(exclude={'category_ids'})
    printer = Printer(
        restaurant_id=restaurant_id,
        **printer_dict
    )
    
    # Assign categories if provided
    if printer_data.category_ids:
        categories = db.query(Category).filter(
            Category.id.in_(printer_data.category_ids),
            Category.restaurant_id == restaurant_id,
            Category.deleted_at.is_(None)
        ).all()
        
        if len(categories) != len(printer_data.category_ids):
            raise ValidationError(
                "One or more category IDs are invalid",
                field="category_ids"
            )
        
        printer.categories = categories
    
    db.add(printer)
    db.commit()
    db.refresh(printer)
    
    return printer


def update_printer(
    db: Session,
    printer_id: int,
    restaurant_id: int,
    printer_data: PrinterUpdate
) -> Printer:
    """Update a printer"""
    printer = get_printer_by_id(db, printer_id, restaurant_id)
    
    if not printer:
        raise ResourceNotFoundError("Printer", printer_id)
    
    # If setting as default, unset other defaults of the same type
    if printer_data.is_default and not printer.is_default:
        printer_type = printer_data.printer_type or printer.printer_type
        db.query(Printer).filter(
            Printer.restaurant_id == restaurant_id,
            Printer.printer_type == printer_type,
            Printer.is_default == True,
            Printer.id != printer_id,
            Printer.deleted_at.is_(None)
        ).update({"is_default": False})
    
    # Update printer fields
    update_data = printer_data.dict(exclude_unset=True, exclude={'category_ids'})
    for field, value in update_data.items():
        setattr(printer, field, value)
    
    # Update categories if provided
    if printer_data.category_ids is not None:
        categories = db.query(Category).filter(
            Category.id.in_(printer_data.category_ids),
            Category.restaurant_id == restaurant_id,
            Category.deleted_at.is_(None)
        ).all()
        
        if len(categories) != len(printer_data.category_ids):
            raise ValidationError(
                "One or more category IDs are invalid",
                field="category_ids"
            )
        
        printer.categories = categories
    
    db.commit()
    db.refresh(printer)
    
    return printer


def delete_printer(db: Session, printer_id: int, restaurant_id: int) -> bool:
    """Soft delete a printer"""
    printer = get_printer_by_id(db, printer_id, restaurant_id)
    
    if not printer:
        raise ResourceNotFoundError("Printer", printer_id)
    
    from datetime import datetime, timezone
    printer.deleted_at = datetime.now(timezone.utc)
    
    db.commit()
    
    return True


def assign_categories_to_printer(
    db: Session,
    printer_id: int,
    restaurant_id: int,
    category_ids: List[int]
) -> Printer:
    """Assign categories to a printer"""
    printer = get_printer_by_id(db, printer_id, restaurant_id)
    
    if not printer:
        raise ResourceNotFoundError("Printer", printer_id)
    
    # Validate all categories exist and belong to the restaurant
    categories = db.query(Category).filter(
        Category.id.in_(category_ids),
        Category.restaurant_id == restaurant_id,
        Category.deleted_at.is_(None)
    ).all()
    
    if len(categories) != len(category_ids):
        raise ValidationError(
            "One or more category IDs are invalid",
            field="category_ids"
        )
    
    printer.categories = categories
    db.commit()
    db.refresh(printer)
    
    return printer


def get_default_printer_by_type(
    db: Session,
    restaurant_id: int,
    printer_type: PrinterType
) -> Optional[Printer]:
    """Get the default printer for a specific type"""
    return db.query(Printer).filter(
        Printer.restaurant_id == restaurant_id,
        Printer.printer_type == printer_type,
        Printer.is_default == True,
        Printer.is_active == True,
        Printer.deleted_at.is_(None)
    ).first()
