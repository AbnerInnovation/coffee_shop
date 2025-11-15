"""
Validators for Orders

Reusable validation functions to avoid code duplication in routers and services.
"""

from sqlalchemy.orm import Session
from typing import Optional

from ...models.order import Order as OrderModel
from ...models.order_item import OrderItem as OrderItemModel
from ...models.menu import MenuItem as MenuItemModel
from ...models.table import Table as TableModel
from ...models.user import User
from ...core.exceptions import ResourceNotFoundError, ForbiddenError, ValidationError


def validate_menu_item_exists(db: Session, item_id: int) -> MenuItemModel:
    """
    Validate that a menu item exists.
    
    Args:
        db: Database session
        item_id: ID of the menu item
        
    Returns:
        Menu item if found
        
    Raises:
        ResourceNotFoundError: If menu item doesn't exist
    """
    menu_item = db.query(MenuItemModel).filter(
        MenuItemModel.id == item_id,
        MenuItemModel.deleted_at.is_(None)
    ).first()
    
    if not menu_item:
        raise ResourceNotFoundError("MenuItem", item_id)
    
    return menu_item


def validate_table_exists(db: Session, table_id: int) -> TableModel:
    """
    Validate that a table exists.
    
    Args:
        db: Database session
        table_id: ID of the table
        
    Returns:
        Table if found
        
    Raises:
        ResourceNotFoundError: If table doesn't exist
    """
    table = db.query(TableModel).filter(
        TableModel.id == table_id,
        TableModel.deleted_at.is_(None)
    ).first()
    
    if not table:
        raise ResourceNotFoundError("Table", table_id)
    
    return table


def validate_order_exists(
    db: Session,
    order_id: int,
    restaurant_id: Optional[int] = None
) -> OrderModel:
    """
    Validate that an order exists.
    
    Args:
        db: Database session
        order_id: ID of the order
        restaurant_id: Optional restaurant ID to filter by
        
    Returns:
        Order if found
        
    Raises:
        ResourceNotFoundError: If order doesn't exist
    """
    query = db.query(OrderModel).filter(
        OrderModel.id == order_id,
        OrderModel.deleted_at.is_(None)
    )
    
    if restaurant_id:
        query = query.filter(OrderModel.restaurant_id == restaurant_id)
    
    order = query.first()
    
    if not order:
        raise ResourceNotFoundError("Order", order_id)
    
    return order


def validate_order_item_exists(
    db: Session,
    order_id: int,
    item_id: int,
    restaurant_id: Optional[int] = None
) -> OrderItemModel:
    """
    Validate that an order item exists and belongs to the specified order.
    
    Args:
        db: Database session
        order_id: ID of the order
        item_id: ID of the order item
        restaurant_id: Optional restaurant ID to filter by
        
    Returns:
        Order item if found
        
    Raises:
        ResourceNotFoundError: If order item doesn't exist or doesn't belong to order
    """
    # First validate order exists
    order = validate_order_exists(db, order_id, restaurant_id)
    
    # Then get the item
    item = db.query(OrderItemModel).filter(
        OrderItemModel.id == item_id,
        OrderItemModel.order_id == order_id,
        OrderItemModel.deleted_at.is_(None)
    ).first()
    
    if not item:
        raise ResourceNotFoundError("OrderItem", item_id)
    
    return item


def validate_can_modify_order(order: OrderModel, user: User) -> None:
    """
    Validate that a user can modify an order.
    
    Rules:
    - Waiters can only modify their own orders
    - Admins and sysadmins can modify any order
    - Cannot modify paid orders (except admins for cancellation)
    
    Args:
        order: Order to check
        user: User attempting to modify
        
    Raises:
        ForbiddenError: If user cannot modify the order
        ValidationError: If order is paid
    """
    # Check if user is admin/sysadmin
    is_admin = user.role in ['admin', 'sysadmin']
    
    # Waiters can only modify their own orders
    if user.role == 'staff' and user.staff_type == 'waiter':
        if order.waiter_id != user.id:
            raise ForbiddenError("Los meseros solo pueden modificar sus propias órdenes")
    
    # Cannot modify paid orders (unless admin cancelling)
    if order.is_paid and not is_admin:
        raise ValidationError("No se puede modificar una orden que ya está pagada")


def validate_can_cancel_order(order: OrderModel, user: User) -> None:
    """
    Validate that a user can cancel an order.
    
    Rules:
    - Only admins and sysadmins can cancel orders
    - Cannot cancel paid orders
    
    Args:
        order: Order to check
        user: User attempting to cancel
        
    Raises:
        ForbiddenError: If user cannot cancel the order
        ValidationError: If order is paid
    """
    # Only admin and sysadmin can cancel orders
    if user.role not in ['admin', 'sysadmin']:
        raise ForbiddenError("Solo los administradores pueden cancelar pedidos")
    
    # Cannot cancel paid orders
    if order.is_paid:
        raise ValidationError("No se puede cancelar un pedido que ya está pagado")


def validate_can_view_order(order: OrderModel, user: User) -> None:
    """
    Validate that a user can view an order.
    
    Rules:
    - Waiters can only view their own orders
    - Other roles can view all orders
    
    Args:
        order: Order to check
        user: User attempting to view
        
    Raises:
        ForbiddenError: If user cannot view the order
    """
    # Waiters can only view their own orders
    if user.role == 'staff' and user.staff_type == 'waiter':
        if order.waiter_id != user.id:
            raise ForbiddenError("Los meseros solo pueden ver sus propias órdenes")


def validate_order_items(db: Session, items: list) -> None:
    """
    Validate that all menu items in a list exist.
    
    Args:
        db: Database session
        items: List of items with menu_item_id attribute
        
    Raises:
        ResourceNotFoundError: If any menu item doesn't exist
    """
    for item in items:
        validate_menu_item_exists(db, item.menu_item_id)


def validate_order_not_paid(order: OrderModel) -> None:
    """
    Validate that an order is not paid.
    
    Args:
        order: Order to check
        
    Raises:
        ValidationError: If order is already paid
    """
    if order.is_paid:
        raise ValidationError(
            f"Order {order.id} is already paid",
            field="is_paid"
        )
