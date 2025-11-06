"""
API endpoints for importing menus from JSON files.
Allows dynamic menu loading in production without code changes.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from pydantic import BaseModel, Field
import logging

from app.db.database import get_db
from app.models.menu import Category, MenuItem
from app.models.restaurant import Restaurant
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.cash_register import CashTransaction
from app.services.user import get_current_active_user
from app.models.user import User, UserRole

router = APIRouter()
logger = logging.getLogger(__name__)


def get_current_superuser(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Verify that current user is a SYSADMIN"""
    if current_user.role != UserRole.SYSADMIN:
        raise HTTPException(
            status_code=403,
            detail="Solo los administradores del sistema pueden importar menús"
        )
    return current_user


# Pydantic schemas for JSON body
class MenuImportRequest(BaseModel):
    """Request schema for importing menu from JSON body"""
    menu_data: Dict[str, Any] = Field(..., description="Menu data with categories and items")
    restaurant_id: int = Field(..., description="ID of the restaurant", ge=1)
    clear_existing: bool = Field(False, description="Whether to clear existing menu")
    force: bool = Field(False, description="Force deletion even with active orders")
    
    class Config:
        json_schema_extra = {
            "example": {
                "restaurant_id": 4,
                "clear_existing": True,
                "force": False,
                "menu_data": {
                    "categories": [
                        {
                            "name": "TACOS",
                            "description": "Tacos tradicionales",
                            "items": [
                                {
                                    "name": "Taco de Pastor",
                                    "description": "Carne al pastor",
                                    "price": 25,
                                    "is_available": True
                                }
                            ]
                        }
                    ]
                }
            }
        }


def validate_menu_data(data: Dict[str, Any]) -> bool:
    """Validate menu JSON structure"""
    if "categories" not in data:
        raise ValueError("El JSON debe contener una clave 'categories'")
    
    if not isinstance(data["categories"], list):
        raise ValueError("'categories' debe ser una lista")
    
    for category in data["categories"]:
        if "name" not in category:
            raise ValueError("Cada categoría debe tener un 'name'")
        if "items" not in category:
            raise ValueError(f"La categoría '{category['name']}' debe tener 'items'")
        if not isinstance(category["items"], list):
            raise ValueError(f"'items' en '{category['name']}' debe ser una lista")
        
        for item in category["items"]:
            if "name" not in item:
                raise ValueError(f"Cada item en '{category['name']}' debe tener 'name'")
            if "price" not in item:
                raise ValueError(f"El item '{item['name']}' debe tener 'price'")
    
    return True


def clear_restaurant_menu(db: Session, restaurant_id: int, force: bool = False):
    """Clear existing menu for a restaurant"""
    
    # Check for active orders
    active_orders = db.query(Order).filter(
        Order.restaurant_id == restaurant_id,
        Order.status.in_(['pending', 'preparing', 'ready'])
    ).count()
    
    if active_orders > 0 and not force:
        raise HTTPException(
            status_code=400,
            detail=f"El restaurante tiene {active_orders} órdenes activas. "
                   f"Use force=true para eliminar de todas formas."
        )
    
    # Get menu item IDs
    menu_item_ids = [item.id for item in db.query(MenuItem.id).filter(
        MenuItem.restaurant_id == restaurant_id
    ).all()]
    
    if menu_item_ids:
        # Delete order items
        db.query(OrderItem).filter(
            OrderItem.menu_item_id.in_(menu_item_ids)
        ).delete(synchronize_session=False)
        
        # Get order IDs
        order_ids = [order.id for order in db.query(Order.id).filter(
            Order.restaurant_id == restaurant_id
        ).all()]
        
        if order_ids:
            # Delete cash transactions
            db.query(CashTransaction).filter(
                CashTransaction.order_id.in_(order_ids)
            ).delete(synchronize_session=False)
        
        # Delete orders
        db.query(Order).filter(
            Order.restaurant_id == restaurant_id
        ).delete(synchronize_session=False)
    
    # Delete menu items
    deleted_items = db.query(MenuItem).filter(
        MenuItem.restaurant_id == restaurant_id
    ).delete(synchronize_session=False)
    
    # Delete categories
    deleted_categories = db.query(Category).filter(
        Category.restaurant_id == restaurant_id
    ).delete(synchronize_session=False)
    
    db.commit()
    
    return {
        "deleted_items": deleted_items,
        "deleted_categories": deleted_categories,
        "deleted_orders": len(order_ids) if menu_item_ids and order_ids else 0
    }


def import_menu_from_data(
    db: Session,
    restaurant_id: int,
    menu_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Import menu from validated data"""
    
    categories_created = 0
    items_created = 0
    category_map = {}
    
    # Create categories and items
    for cat_data in menu_data["categories"]:
        # Create category
        category = Category(
            name=cat_data["name"],
            description=cat_data.get("description"),
            visible_in_kitchen=cat_data.get("visible_in_kitchen", True),
            restaurant_id=restaurant_id
        )
        db.add(category)
        db.flush()  # Get the ID
        
        category_map[cat_data["name"]] = category.id
        categories_created += 1
        
        # Create items for this category
        for item_data in cat_data["items"]:
            item = MenuItem(
                name=item_data["name"],
                description=item_data.get("description"),
                price=item_data["price"],
                discount_price=item_data.get("discount_price"),
                category_id=category.id,
                restaurant_id=restaurant_id,
                is_available=item_data.get("is_available", True),
                image_url=item_data.get("image_url"),
                ingredients=item_data.get("ingredients")
            )
            db.add(item)
            items_created += 1
    
    db.commit()
    
    return {
        "categories_created": categories_created,
        "items_created": items_created,
        "category_map": category_map
    }


@router.post("/import")
async def import_menu_from_body(
    request: MenuImportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    Import menu from JSON body (recommended).
    
    **Request Body:**
    ```json
    {
        "restaurant_id": 4,
        "clear_existing": true,
        "force": false,
        "menu_data": {
            "categories": [
                {
                    "name": "Category Name",
                    "description": "Optional description",
                    "visible_in_kitchen": true,
                    "items": [
                        {
                            "name": "Item Name",
                            "description": "Item description",
                            "price": 100.00,
                            "discount_price": 80.00,
                            "is_available": true,
                            "image_url": "https://...",
                            "ingredients": {"options": [...], "removable": [...]}
                        }
                    ]
                }
            ]
        }
    }
    ```
    
    **Parameters:**
    - **restaurant_id**: ID of the restaurant
    - **clear_existing**: Whether to clear existing menu (default: False)
    - **force**: Force deletion even with active orders (default: False)
    - **menu_data**: Menu structure with categories and items
    """
    
    # Verify restaurant exists
    restaurant = db.query(Restaurant).filter(Restaurant.id == request.restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")
    
    # Validate structure
    try:
        validate_menu_data(request.menu_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Clear existing menu if requested
    deletion_stats = None
    if request.clear_existing:
        try:
            deletion_stats = clear_restaurant_menu(db, request.restaurant_id, request.force)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error clearing menu: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error limpiando menú: {str(e)}")
    
    # Import new menu
    try:
        import_stats = import_menu_from_data(db, request.restaurant_id, request.menu_data)
    except Exception as e:
        db.rollback()
        logger.error(f"Error importing menu: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error importando menú: {str(e)}")
    
    return {
        "success": True,
        "restaurant_id": request.restaurant_id,
        "restaurant_name": restaurant.name,
        "deletion_stats": deletion_stats,
        "import_stats": import_stats
    }