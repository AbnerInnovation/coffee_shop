"""
Serializers for Orders

Functions to convert database models to dictionaries for API responses.
"""

from typing import Optional

from ...models.order import Order as OrderModel
from ...models.order_item import OrderItem as OrderItemModel
from ...models.order_person import OrderPerson as OrderPersonModel
from ...models.menu import MenuItem, MenuItemVariant


def serialize_menu_item(menu_item: MenuItem) -> dict:
    """
    Serialize a menu item to dictionary.
    
    Args:
        menu_item: MenuItem model instance
        
    Returns:
        Dictionary with menu item data
    """
    # Get category visible_in_kitchen flag
    category_visible = True  # Default to visible
    if menu_item.category:
        category_visible = getattr(menu_item.category, "visible_in_kitchen", True)
    
    return {
        "id": menu_item.id,
        "name": menu_item.name,
        "price": float(menu_item.price) if menu_item.price is not None else 0.0,
        "discount_price": float(menu_item.discount_price) if menu_item.discount_price is not None else None,
        "description": menu_item.description,
        "category": getattr(menu_item.category, "name", menu_item.category) if menu_item.category else None,
        "category_visible_in_kitchen": category_visible,
        "image_url": menu_item.image_url,
        "is_available": menu_item.is_available,
    }


def serialize_variant(variant: Optional[MenuItemVariant]) -> Optional[dict]:
    """
    Serialize a menu item variant to dictionary.
    
    Args:
        variant: MenuItemVariant model instance or None
        
    Returns:
        Dictionary with variant data or None
    """
    if not variant:
        return None
    return {
        "id": variant.id,
        "name": variant.name,
        "price": float(variant.price) if variant.price is not None else 0.0,
        "discount_price": float(variant.discount_price) if variant.discount_price is not None else None,
        "description": getattr(variant, "description", None),
    }


def serialize_order_item_extra(extra) -> dict:
    """
    Serialize an order item extra to dictionary.
    
    Args:
        extra: OrderItemExtra model instance
        
    Returns:
        Dictionary with extra data
    """
    return {
        "id": extra.id,
        "order_item_id": extra.order_item_id,
        "name": extra.name,
        "price": float(extra.price) if extra.price is not None else 0.0,
        "quantity": extra.quantity,
        "created_at": extra.created_at,
        "updated_at": extra.updated_at,
    }


def serialize_order_item(item: OrderItemModel) -> dict:
    """
    Serialize an order item to dictionary.
    
    Args:
        item: OrderItem model instance
        
    Returns:
        Dictionary with order item data
    """
    # Serialize extras if they exist
    extras = []
    if hasattr(item, 'extras') and item.extras:
        extras = [serialize_order_item_extra(extra) for extra in item.extras]
    
    return {
        "id": item.id,
        "order_id": item.order_id,
        "person_id": item.person_id,
        "menu_item_id": item.menu_item_id,
        "quantity": item.quantity,
        "special_instructions": item.special_instructions,
        "status": item.status,
        "variant_id": item.variant_id,
        "variant": serialize_variant(item.variant),
        "unit_price": float(item.unit_price) if item.unit_price is not None else None,
        "created_at": item.created_at,
        "updated_at": item.updated_at,
        "menu_item": serialize_menu_item(item.menu_item),
        "extras": extras,
    }


def serialize_order_person(person: OrderPersonModel) -> dict:
    """
    Serialize an order person with their items to dictionary.
    
    Args:
        person: OrderPerson model instance
        
    Returns:
        Dictionary with person data
    """
    return {
        "id": person.id,
        "order_id": person.order_id,
        "name": person.name,
        "position": person.position,
        "created_at": person.created_at,
        "updated_at": person.updated_at,
        "items": [serialize_order_item(item) for item in person.items] if hasattr(person, 'items') else [],
    }


def serialize_order(order: OrderModel) -> dict:
    """
    Serialize an order to dictionary.
    
    Args:
        order: Order model instance
        
    Returns:
        Dictionary with complete order data
    """
    # Calculate subtotal from items including extras
    items = getattr(order, "items", [])
    subtotal = 0.0
    for item in items:
        # Add item price
        subtotal += item.quantity * (item.unit_price or 0)
        # Add extras price
        if hasattr(item, 'extras') and item.extras:
            for extra in item.extras:
                subtotal += extra.quantity * (extra.price or 0)
    
    # For now, tax is 0 (can be configured later)
    tax = 0.0
    total = subtotal + tax
    
    # Serialize persons if they exist
    persons = []
    if hasattr(order, 'persons') and order.persons:
        persons = [serialize_order_person(person) for person in order.persons]
    
    return {
        "id": order.id,
        "order_number": order.order_number,
        "table_id": order.table_id,
        "status": order.status,
        "notes": order.notes or None,
        "total_amount": float(order.total_amount) if order.total_amount is not None else total,
        "subtotal": subtotal,
        "tax": tax,
        "taxRate": 0.0,
        "total": total,
        "created_at": order.created_at,
        "updated_at": order.updated_at,
        "table_number": order.table.number if order.table else None,
        "customer_name": order.customer_name,
        "user_id": order.user_id,
        "order_type": order.order_type,
        "is_paid": order.is_paid,
        "payment_method": order.payment_method,
        "sort": order.sort if hasattr(order, 'sort') else 50,
        "deleted_at": order.deleted_at,
        "items": [serialize_order_item(item) for item in items],
        "persons": persons,
    }
