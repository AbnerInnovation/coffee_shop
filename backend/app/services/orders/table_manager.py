"""
Table Manager Service

Handles table occupancy management for orders, including:
- Marking tables as occupied/available
- Handling table changes when order type changes
- Checking if tables have active orders
"""

from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timezone

from ...models.table import Table as TableModel
from ...models.order import Order as OrderModel, OrderStatus
from ...core.exceptions import ResourceNotFoundError


def mark_table_occupied(db: Session, table_id: int) -> TableModel:
    """
    Mark a table as occupied.
    
    Args:
        db: Database session
        table_id: ID of the table to mark as occupied
        
    Returns:
        Updated table
        
    Raises:
        ResourceNotFoundError: If table doesn't exist
    """
    table = db.query(TableModel).filter(
        TableModel.id == table_id,
        TableModel.deleted_at.is_(None)
    ).first()
    
    if not table:
        raise ResourceNotFoundError("Table", table_id)
    
    table.is_occupied = True
    table.updated_at = datetime.now(timezone.utc)
    
    db.add(table)
    db.flush()  # Don't commit, let caller handle transaction
    
    return table


def mark_table_available_if_no_orders(
    db: Session,
    table_id: int,
    exclude_order_id: Optional[int] = None
) -> Optional[TableModel]:
    """
    Mark a table as available if it has no active orders.
    
    This function checks if the table has any unpaid orders (excluding the specified order).
    If no unpaid orders exist, the table is marked as available.
    
    Args:
        db: Database session
        table_id: ID of the table to check
        exclude_order_id: Order ID to exclude from the check (e.g., the order being paid)
        
    Returns:
        Updated table if it was marked available, None otherwise
    """
    # Get the table
    table = db.query(TableModel).filter(
        TableModel.id == table_id,
        TableModel.deleted_at.is_(None)
    ).first()
    
    if not table:
        return None
    
    # Check for other unpaid orders on this table
    query = db.query(OrderModel).filter(
        OrderModel.table_id == table_id,
        OrderModel.is_paid == False,
        OrderModel.status != OrderStatus.CANCELLED,
        OrderModel.deleted_at.is_(None)
    )
    
    if exclude_order_id:
        query = query.filter(OrderModel.id != exclude_order_id)
    
    other_orders = query.count()
    
    # If no other unpaid orders, mark table as available
    if other_orders == 0:
        table.is_occupied = False
        table.updated_at = datetime.now(timezone.utc)
        db.add(table)
        db.flush()
        return table
    
    return None


def handle_table_change(
    db: Session,
    old_table_id: Optional[int],
    new_table_id: Optional[int],
    new_order_type: str,
    order_id: int
) -> dict:
    """
    Handle table changes when an order is updated.
    
    This function manages the following scenarios:
    1. dine-in → takeaway/delivery: Release old table
    2. takeaway/delivery → dine-in: Occupy new table
    3. dine-in → dine-in (different table): Release old, occupy new
    4. No change: Do nothing
    
    Args:
        db: Database session
        old_table_id: Current table ID (None if takeaway/delivery)
        new_table_id: New table ID (None if changing to takeaway/delivery)
        new_order_type: New order type ('dine_in', 'takeaway', 'delivery')
        order_id: ID of the order being updated
        
    Returns:
        Dictionary with changes made:
        {
            'old_table_released': bool,
            'new_table_occupied': bool,
            'old_table_id': int or None,
            'new_table_id': int or None
        }
    """
    result = {
        'old_table_released': False,
        'new_table_occupied': False,
        'old_table_id': old_table_id,
        'new_table_id': new_table_id
    }
    
    # Scenario 1: Removing table (dine-in → takeaway/delivery)
    is_removing_table = (
        old_table_id and 
        (new_table_id is None or new_order_type in ['takeaway', 'delivery'])
    )
    
    if is_removing_table:
        released = mark_table_available_if_no_orders(db, old_table_id, order_id)
        result['old_table_released'] = released is not None
    
    # Scenario 2: Adding table (takeaway/delivery → dine-in)
    is_adding_table = (
        not old_table_id and 
        new_table_id and 
        new_order_type == 'dine_in'
    )
    
    if is_adding_table:
        mark_table_occupied(db, new_table_id)
        result['new_table_occupied'] = True
    
    # Scenario 3: Changing table (dine-in → dine-in, different table)
    is_changing_table = (
        old_table_id and 
        new_table_id and 
        old_table_id != new_table_id and
        new_order_type == 'dine_in'
    )
    
    if is_changing_table:
        # Release old table
        released = mark_table_available_if_no_orders(db, old_table_id, order_id)
        result['old_table_released'] = released is not None
        
        # Occupy new table
        mark_table_occupied(db, new_table_id)
        result['new_table_occupied'] = True
    
    return result


def get_table_active_orders(
    db: Session,
    table_id: int,
    exclude_order_id: Optional[int] = None
) -> list[OrderModel]:
    """
    Get all active (unpaid, not cancelled) orders for a table.
    
    Args:
        db: Database session
        table_id: ID of the table
        exclude_order_id: Optional order ID to exclude
        
    Returns:
        List of active orders
    """
    query = db.query(OrderModel).filter(
        OrderModel.table_id == table_id,
        OrderModel.is_paid == False,
        OrderModel.status != OrderStatus.CANCELLED,
        OrderModel.deleted_at.is_(None)
    )
    
    if exclude_order_id:
        query = query.filter(OrderModel.id != exclude_order_id)
    
    return query.all()


def is_table_available(db: Session, table_id: int) -> bool:
    """
    Check if a table is available (not occupied or has no active orders).
    
    Args:
        db: Database session
        table_id: ID of the table to check
        
    Returns:
        True if table is available, False otherwise
    """
    table = db.query(TableModel).filter(
        TableModel.id == table_id,
        TableModel.deleted_at.is_(None)
    ).first()
    
    if not table:
        return False
    
    # Check table's occupied flag
    if not table.is_occupied:
        return True
    
    # Double-check by counting active orders
    active_orders = get_table_active_orders(db, table_id)
    return len(active_orders) == 0
