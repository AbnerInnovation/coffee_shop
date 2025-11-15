"""
Order Items CRUD Operations

CRUD operations for order items, including:
- Getting order items
- Adding items to orders
- Updating order items
- Deleting order items
- Updating order item status
"""

from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timezone

from ...models.order import Order as OrderModel, OrderStatus
from ...models.order_item import OrderItem as OrderItemModel
from ...models.menu import MenuItem, MenuItemVariant
from ...schemas.order import OrderItemCreate, OrderItemUpdate
from .serializers import serialize_order_item


def get_order_item(
    db: Session,
    item_id: int,
    include_deleted: bool = False
) -> Optional[OrderItemModel]:
    """
    Get an order item by ID.
    
    Args:
        db: Database session
        item_id: ID of the order item
        include_deleted: Whether to include soft-deleted items
        
    Returns:
        OrderItem model instance or None
    """
    query = db.query(OrderItemModel).filter(OrderItemModel.id == item_id)
    if not include_deleted:
        query = query.filter(OrderItemModel.deleted_at.is_(None))
    return query.first()


def add_order_item(
    db: Session,
    db_order: OrderModel,
    item: OrderItemCreate,
    unit_price: Optional[float] = None
) -> dict:
    """
    Add an item to an existing order.
    
    Args:
        db: Database session
        db_order: Order to add item to
        item: Item creation data
        unit_price: Optional unit price (if not provided, will be calculated from menu item)
        
    Returns:
        Serialized order item
    """
    menu_item = db.query(MenuItem).filter(MenuItem.id == item.menu_item_id).first()
    if not menu_item:
        raise ValueError(f"Menu item {item.menu_item_id} not found")

    # Calculate unit price if not provided
    if unit_price is None:
        unit_price = menu_item.get_effective_price()  # Use discount price if available
        
        if item.variant_id:
            variant = db.query(MenuItemVariant).filter(
                MenuItemVariant.id == item.variant_id,
                MenuItemVariant.menu_item_id == item.menu_item_id,
            ).first()
            if not variant:
                raise ValueError(
                    f"Variant {item.variant_id} not found for menu item {item.menu_item_id}"
                )
            unit_price = variant.get_effective_price()

    db_item = OrderItemModel(
        order_id=db_order.id,
        menu_item_id=item.menu_item_id,
        variant_id=item.variant_id,
        quantity=item.quantity,
        unit_price=unit_price,
        special_instructions=item.special_instructions,
        status=OrderStatus.PENDING,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(db_item)
    
    # Update order total
    db_order.total_amount = (db_order.total_amount or 0) + (unit_price * item.quantity)
    db_order.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(db_item)
    
    return serialize_order_item(db_item)


def update_order_item(
    db: Session,
    db_item: OrderItemModel,
    item: OrderItemUpdate
) -> dict:
    """
    Update an order item.
    
    Args:
        db: Database session
        db_item: Existing order item
        item: Update data
        
    Returns:
        Serialized updated order item
    """
    update_data = item.dict(exclude_unset=True)
    
    # Handle variant change
    if "variant_id" in update_data and update_data["variant_id"] != db_item.variant_id:
        if update_data["variant_id"]:
            variant = db.query(MenuItemVariant).filter(
                MenuItemVariant.id == update_data["variant_id"],
                MenuItemVariant.menu_item_id == db_item.menu_item_id,
            ).first()
            if not variant:
                raise ValueError(f"Variant {update_data['variant_id']} not found")
            update_data["unit_price"] = variant.get_effective_price()
        else:
            # Removing variant, use base menu item price
            menu_item = db.query(MenuItem).filter(MenuItem.id == db_item.menu_item_id).first()
            if menu_item:
                update_data["unit_price"] = menu_item.get_effective_price()

    # Validate and convert status if provided
    if 'status' in update_data:
        try:
            update_data['status'] = OrderStatus(update_data['status'])
        except ValueError:
            raise ValueError(
                f"Invalid status. Must be one of: {', '.join([s.value for s in OrderStatus])}"
            )

    # Update item fields
    for field, value in update_data.items():
        setattr(db_item, field, value)

    db_item.updated_at = datetime.now(timezone.utc)
    
    # Recalculate order total
    order = db.query(OrderModel).filter(OrderModel.id == db_item.order_id).first()
    if order:
        order.total_amount = sum(i.quantity * (i.unit_price or 0) for i in order.items)
        order.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(db_item)
    
    return serialize_order_item(db_item)


def update_order_item_status(
    db: Session,
    db_item: OrderItemModel,
    status: str
) -> dict:
    """
    Update only the status of an order item.
    
    Args:
        db: Database session
        db_item: Order item to update
        status: New status
        
    Returns:
        Serialized updated order item
    """
    try:
        db_item.status = OrderStatus(status)
    except ValueError:
        raise ValueError(
            f"Invalid status '{status}'. Must be one of: {', '.join([s.value for s in OrderStatus])}"
        )
    
    db_item.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(db_item)
    
    return serialize_order_item(db_item)


def delete_order_item(db: Session, db_item: OrderItemModel) -> None:
    """
    Soft delete an order item.
    
    Args:
        db: Database session
        db_item: Order item to delete
    """
    db_item.deleted_at = datetime.now(timezone.utc)
    db.add(db_item)
    
    # Recalculate order total
    order = db.query(OrderModel).filter(OrderModel.id == db_item.order_id).first()
    if order:
        order.total_amount = sum(
            item.quantity * item.unit_price 
            for item in order.items 
            if item.deleted_at is None and item.id != db_item.id
        )
        order.updated_at = datetime.now(timezone.utc)
        db.add(order)
    
    db.commit()
