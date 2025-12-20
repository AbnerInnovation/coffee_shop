"""
API endpoints for Printer management
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.base import get_db
from app.core.dependencies import get_current_user_with_restaurant
from app.models.user import User
from app.models.printer import PrinterType
from app.schemas.printer import (
    PrinterCreate,
    PrinterUpdate,
    PrinterResponse,
    PrinterListResponse,
    PrinterCategoryAssignment
)
from app.services import printer as printer_service
from app.core.exceptions import ResourceNotFoundError

router = APIRouter(prefix="/printers", tags=["printers"])


@router.get("/", response_model=PrinterListResponse)
def get_printers(
    printer_type: Optional[PrinterType] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(get_current_user_with_restaurant),
    db: Session = Depends(get_db)
):
    """
    Get all printers for the current restaurant
    
    Optional filters:
    - printer_type: Filter by printer type (kitchen, bar, cashier)
    - is_active: Filter by active status
    """
    printers = printer_service.get_printers_by_restaurant(
        db=db,
        restaurant_id=current_user.restaurant_id,
        printer_type=printer_type,
        is_active=is_active
    )
    
    return {
        "printers": [PrinterResponse.from_printer(p) for p in printers],
        "total": len(printers)
    }


@router.get("/{printer_id}", response_model=PrinterResponse)
def get_printer(
    printer_id: int,
    current_user: User = Depends(get_current_user_with_restaurant),
    db: Session = Depends(get_db)
):
    """Get a specific printer by ID"""
    printer = printer_service.get_printer_by_id(
        db=db,
        printer_id=printer_id,
        restaurant_id=current_user.restaurant_id
    )
    
    if not printer:
        raise ResourceNotFoundError("Printer", printer_id)
    
    return PrinterResponse.from_printer(printer)


@router.get("/category/{category_id}", response_model=List[PrinterResponse])
def get_printers_by_category(
    category_id: int,
    current_user: User = Depends(get_current_user_with_restaurant),
    db: Session = Depends(get_db)
):
    """Get all printers assigned to a specific category"""
    printers = printer_service.get_printers_by_category(
        db=db,
        category_id=category_id,
        restaurant_id=current_user.restaurant_id
    )
    
    return [PrinterResponse.from_printer(p) for p in printers]


@router.get("/type/{printer_type}/default", response_model=PrinterResponse)
def get_default_printer(
    printer_type: PrinterType,
    current_user: User = Depends(get_current_user_with_restaurant),
    db: Session = Depends(get_db)
):
    """Get the default printer for a specific type"""
    printer = printer_service.get_default_printer_by_type(
        db=db,
        restaurant_id=current_user.restaurant_id,
        printer_type=printer_type
    )
    
    if not printer:
        raise ResourceNotFoundError(
            f"Default {printer_type} printer",
            f"for restaurant {current_user.restaurant_id}"
        )
    
    return PrinterResponse.from_printer(printer)


@router.post("/", response_model=PrinterResponse, status_code=status.HTTP_201_CREATED)
def create_printer(
    printer_data: PrinterCreate,
    current_user: User = Depends(get_current_user_with_restaurant),
    db: Session = Depends(get_db)
):
    """Create a new printer"""
    printer = printer_service.create_printer(
        db=db,
        printer_data=printer_data,
        restaurant_id=current_user.restaurant_id
    )
    
    return PrinterResponse.from_printer(printer)


@router.put("/{printer_id}", response_model=PrinterResponse)
def update_printer(
    printer_id: int,
    printer_data: PrinterUpdate,
    current_user: User = Depends(get_current_user_with_restaurant),
    db: Session = Depends(get_db)
):
    """Update a printer"""
    printer = printer_service.update_printer(
        db=db,
        printer_id=printer_id,
        restaurant_id=current_user.restaurant_id,
        printer_data=printer_data
    )
    
    return PrinterResponse.from_printer(printer)


@router.delete("/{printer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_printer(
    printer_id: int,
    current_user: User = Depends(get_current_user_with_restaurant),
    db: Session = Depends(get_db)
):
    """Delete a printer (soft delete)"""
    printer_service.delete_printer(
        db=db,
        printer_id=printer_id,
        restaurant_id=current_user.restaurant_id
    )
    
    return None


@router.post("/{printer_id}/categories", response_model=PrinterResponse)
def assign_categories(
    printer_id: int,
    assignment: PrinterCategoryAssignment,
    current_user: User = Depends(get_current_user_with_restaurant),
    db: Session = Depends(get_db)
):
    """Assign categories to a printer"""
    printer = printer_service.assign_categories_to_printer(
        db=db,
        printer_id=printer_id,
        restaurant_id=current_user.restaurant_id,
        category_ids=assignment.category_ids
    )
    
    return PrinterResponse.from_printer(printer)
