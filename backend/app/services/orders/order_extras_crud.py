"""
Order Item Extras CRUD Operations

CRUD operations for order item extras (additional toppings, modifications, etc.)
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone

from ...models.order_item import OrderItem as OrderItemModel
from ...models.order_item_extra import OrderItemExtra
from ...schemas.order import OrderItemExtraCreate, OrderItemExtraUpdate
from .serializers import serialize_order_item_extra


def get_item_extras(
    db: Session,
    order_item_id: int,
    include_deleted: bool = False
) -> List[dict]:
    """
    Get all extras for an order item.
    
    Args:
        db: Database session
        order_item_id: ID of the order item
        include_deleted: Whether to include soft-deleted extras
        
    Returns:
        List of serialized extras
    """
    query = db.query(OrderItemExtra).filter(
        OrderItemExtra.order_item_id == order_item_id
    )
    
    if not include_deleted:
        query = query.filter(OrderItemExtra.deleted_at.is_(None))
    
    extras = query.all()
    return [serialize_order_item_extra(extra) for extra in extras]


def get_extra_by_id(
    db: Session,
    extra_id: int,
    include_deleted: bool = False
) -> Optional[OrderItemExtra]:
    """
    Get a specific extra by ID.
    
    Args:
        db: Database session
        extra_id: ID of the extra
        include_deleted: Whether to include soft-deleted extras
        
    Returns:
        OrderItemExtra model instance or None
    """
    query = db.query(OrderItemExtra).filter(OrderItemExtra.id == extra_id)
    
    if not include_deleted:
        query = query.filter(OrderItemExtra.deleted_at.is_(None))
    
    return query.first()


def add_extra_to_item(
    db: Session,
    order_item_id: int,
    extra: OrderItemExtraCreate
) -> dict:
    """
    Add an extra to an order item.
    
    Args:
        db: Database session
        order_item_id: ID of the order item
        extra: Extra creation data
        
    Returns:
        Serialized created extra
    """
    # Verify order item exists
    order_item = db.query(OrderItemModel).filter(
        OrderItemModel.id == order_item_id,
        OrderItemModel.deleted_at.is_(None)
    ).first()
    
    if not order_item:
        raise ValueError(f"Order item {order_item_id} not found")
    
    # Create extra
    db_extra = OrderItemExtra(
        order_item_id=order_item_id,
        name=extra.name,
        price=extra.price,
        quantity=extra.quantity,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db.add(db_extra)
    
    # Update order total
    from ...models.order import Order as OrderModel
    order = db.query(OrderModel).filter(
        OrderModel.id == order_item.order_id
    ).first()
    
    if order:
        # Recalculate total including all extras
        total = 0.0
        for item in order.items:
            if item.deleted_at is None:
                total += item.quantity * (item.unit_price or 0)
                # Add extras
                for item_extra in item.extras:
                    if item_extra.deleted_at is None:
                        total += item_extra.quantity * (item_extra.price or 0)
        
        order.total_amount = total
        order.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(db_extra)
    
    return serialize_order_item_extra(db_extra)


def update_item_extra(
    db: Session,
    db_extra: OrderItemExtra,
    extra: OrderItemExtraUpdate
) -> dict:
    """
    Update an order item extra.
    
    Args:
        db: Database session
        db_extra: Existing extra
        extra: Update data
        
    Returns:
        Serialized updated extra
    """
    update_data = extra.dict(exclude_unset=True)
    
    # Update extra fields
    for field, value in update_data.items():
        setattr(db_extra, field, value)
    
    db_extra.updated_at = datetime.now(timezone.utc)
    
    # Recalculate order total
    order_item = db.query(OrderItemModel).filter(
        OrderItemModel.id == db_extra.order_item_id
    ).first()
    
    if order_item:
        from ...models.order import Order as OrderModel
        order = db.query(OrderModel).filter(
            OrderModel.id == order_item.order_id
        ).first()
        
        if order:
            # Recalculate total including all extras
            total = 0.0
            for item in order.items:
                if item.deleted_at is None:
                    total += item.quantity * (item.unit_price or 0)
                    # Add extras
                    for item_extra in item.extras:
                        if item_extra.deleted_at is None:
                            total += item_extra.quantity * (item_extra.price or 0)
            
            order.total_amount = total
            order.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(db_extra)
    
    return serialize_order_item_extra(db_extra)


def delete_item_extra(db: Session, db_extra: OrderItemExtra) -> None:
    """
    Soft delete an order item extra.
    
    Args:
        db: Database session
        db_extra: Extra to delete
    """
    db_extra.deleted_at = datetime.now(timezone.utc)
    db.add(db_extra)
    
    # Recalculate order total
    order_item = db.query(OrderItemModel).filter(
        OrderItemModel.id == db_extra.order_item_id
    ).first()
    
    if order_item:
        from ...models.order import Order as OrderModel
        order = db.query(OrderModel).filter(
            OrderModel.id == order_item.order_id
        ).first()
        
        if order:
            # Recalculate total excluding deleted extras
            total = 0.0
            for item in order.items:
                if item.deleted_at is None:
                    total += item.quantity * (item.unit_price or 0)
                    # Add only non-deleted extras
                    for item_extra in item.extras:
                        if item_extra.deleted_at is None and item_extra.id != db_extra.id:
                            total += item_extra.quantity * (item_extra.price or 0)
            
            order.total_amount = total
            order.updated_at = datetime.now(timezone.utc)
    
    db.commit()
