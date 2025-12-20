"""
Order CRUD Operations

Basic CRUD operations for orders, including:
- Querying orders with filters and sorting
- Creating orders with items
- Updating orders
- Deleting orders (soft delete)
"""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, case
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
import logging
import sqlalchemy as sa

from ...models.order import Order as OrderModel, OrderStatus
from ...models.order_item import OrderItem as OrderItemModel
from ...models.order_person import OrderPerson as OrderPersonModel
from ...models.menu import MenuItem, MenuItemVariant
from ...models.table import Table as TableModel
from ...schemas.order import OrderCreate, OrderUpdate, OrderItemCreate
from .serializers import serialize_order
from .ticket_generator import generate_ticket_number
from ...services.subscription import get_restaurant_subscription
from ...core.operation_modes import validate_order_for_mode, get_default_order_type, get_mode_config


def apply_filters(query, filters: Dict[str, Any]):
    """
    Apply filters to an order query.
    
    Args:
        query: SQLAlchemy query object
        filters: Dictionary of filters to apply
        
    Returns:
        Filtered query
    """
    if not filters:
        return query

    # Filter by restaurant_id (required for multi-tenant)
    if filters.get("restaurant_id") is not None:
        query = query.filter(OrderModel.restaurant_id == filters["restaurant_id"])

    if filters.get("status") is not None:
        query = query.filter(OrderModel.status == filters["status"])

    if filters.get("table_id") is not None:
        query = query.filter(OrderModel.table_id == filters["table_id"])
    
    if filters.get("waiter_id") is not None:
        query = query.filter(OrderModel.user_id == filters["waiter_id"])

    if not filters.get("include_deleted", False):
        query = query.filter(OrderModel.deleted_at.is_(None))

    if filters.get("start_date"):
        query = query.filter(OrderModel.created_at >= filters["start_date"])

    if filters.get("end_date"):
        query = query.filter(OrderModel.created_at <= filters["end_date"])

    if filters.get("search"):
        search_term = f"%{filters['search']}%"
        query = query.filter(
            or_(
                OrderModel.notes.ilike(search_term),
                OrderModel.customer_name.ilike(search_term)
            )
        )

    # Filter by hours (e.g., last 24 hours)
    if filters.get("hours") is not None:
        hours_ago = datetime.now(timezone.utc) - timedelta(hours=filters["hours"])
        query = query.filter(OrderModel.created_at >= hours_ago)

    return query


def get_orders(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    sort_by: str = 'kitchen',
    **filters,
) -> List[dict]:
    """
    Get orders with optional filtering and sorting.
    
    Args:
        db: Database session
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        sort_by: Sorting method ('kitchen' for FIFO, 'orders' for newest first)
        **filters: Additional filters (restaurant_id, status, table_id, waiter_id, etc.)
        
    Returns:
        List of serialized orders
    """
    try:
        query = db.query(OrderModel).options(
            joinedload(OrderModel.items).joinedload(OrderItemModel.menu_item),
            joinedload(OrderModel.items).joinedload(OrderItemModel.variant),
            joinedload(OrderModel.persons).joinedload(OrderPersonModel.items).joinedload(OrderItemModel.menu_item),
            joinedload(OrderModel.persons).joinedload(OrderPersonModel.items).joinedload(OrderItemModel.variant),
            joinedload(OrderModel.table),
            joinedload(OrderModel.user),
        )

        query = apply_filters(query, filters or {})
        
        # Apply sorting based on context
        if sort_by == 'kitchen':
            # Kitchen view: FIFO (oldest first)
            # Order by:
            # 1. Status (pending before preparing)
            # 2. Sort ASC (1 = items added to existing order, 2 = new order)
            # 3. Created_at ASC (oldest first - FIFO)
            status_order = case(
                (OrderModel.status == OrderStatus.PENDING, 0),
                (OrderModel.status == OrderStatus.PREPARING, 1),
                else_=2
            )
            orders = query.order_by(
                status_order,
                OrderModel.sort.asc(),
                OrderModel.created_at.asc()
            ).offset(skip).limit(limit).all()
        else:
            # Orders view: Newest first (by ID desc)
            orders = query.order_by(
                OrderModel.id.desc()
            ).offset(skip).limit(limit).all()

        return [serialize_order(order) for order in orders]
    except Exception as e:
        logging.error(f"Error in get_orders: {str(e)}", exc_info=True)
        raise


def get_order(
    db: Session,
    order_id: int,
    restaurant_id: int,
    include_deleted: bool = False
) -> Optional[dict]:
    """
    Get a single order by ID.
    
    Args:
        db: Database session
        order_id: ID of the order
        restaurant_id: Restaurant ID for multi-tenant filtering
        include_deleted: Whether to include soft-deleted orders
        
    Returns:
        Serialized order or None if not found
    """
    try:
        from ...models.order_item_extra import OrderItemExtra
        
        query = db.query(OrderModel).options(
            joinedload(OrderModel.items).joinedload(OrderItemModel.menu_item),
            joinedload(OrderModel.items).joinedload(OrderItemModel.variant),
            joinedload(OrderModel.items).joinedload(OrderItemModel.extras),
            joinedload(OrderModel.persons).joinedload(OrderPersonModel.items).joinedload(OrderItemModel.menu_item),
            joinedload(OrderModel.persons).joinedload(OrderPersonModel.items).joinedload(OrderItemModel.variant),
            joinedload(OrderModel.persons).joinedload(OrderPersonModel.items).joinedload(OrderItemModel.extras),
            joinedload(OrderModel.table),
            joinedload(OrderModel.user),
        ).filter(
            OrderModel.id == order_id,
            OrderModel.restaurant_id == restaurant_id
        )

        if not include_deleted:
            query = query.filter(OrderModel.deleted_at.is_(None))

        db_order = query.first()
        return serialize_order(db_order) if db_order else None
    except Exception as e:
        logging.error(f"Error in get_order: {str(e)}", exc_info=True)
        raise


def create_order_with_items(
    db: Session,
    order: OrderCreate,
    restaurant_id: int,
    user_id: Optional[int] = None
) -> dict:
    """
    Create a new order with items.
    
    This function handles:
    - Creating the order
    - Creating order items (with variants and extras)
    - Creating persons (multi-diner support)
    - Calculating total amount
    - Marking table as occupied for dine-in orders
    - Generating ticket numbers for POS mode
    
    Args:
        db: Database session
        order: Order creation data
        restaurant_id: Restaurant ID
        user_id: ID of the user creating the order (waiter)
        
    Returns:
        Serialized created order
    """
    # Get restaurant subscription and operation mode
    subscription = get_restaurant_subscription(db, restaurant_id)
    operation_mode = subscription.plan.operation_mode if subscription and subscription.plan else None
    
    # Get restaurant to check allow_dine_in_without_table setting
    from ...models.restaurant import Restaurant as RestaurantModel
    restaurant = db.query(RestaurantModel).filter(RestaurantModel.id == restaurant_id).first()
    allow_dine_in_without_table = restaurant.allow_dine_in_without_table if restaurant else False
    
    # Determine order_type: use provided, or get default from mode, or infer from table_id
    if order.order_type:
        order_type = order.order_type
    elif operation_mode:
        order_type = get_default_order_type(operation_mode).value
    else:
        order_type = "dine_in" if order.table_id is not None else "delivery"
    
    # Validate order against operation mode
    if operation_mode:
        is_valid, error_msg = validate_order_for_mode(
            operation_mode,
            {
                'table_id': order.table_id,
                'order_type': order_type
            },
            allow_dine_in_without_table
        )
        if not is_valid:
            raise ValueError(error_msg)

    # Get the next order number for this restaurant
    max_order_number = db.query(sa.func.max(OrderModel.order_number)).filter(
        OrderModel.restaurant_id == restaurant_id
    ).scalar()
    next_order_number = (max_order_number or 0) + 1
    
    # Generate ticket number if in POS mode
    ticket_number = None
    if operation_mode:
        ticket_number = generate_ticket_number(db, restaurant_id, operation_mode)
    
    # Determine initial status: POS orders (no kitchen) are completed immediately, others are pending
    mode_config = get_mode_config(operation_mode) if operation_mode else None
    allows_kitchen = mode_config.get('allows_kitchen_orders', True) if mode_config else True
    initial_status = OrderStatus.COMPLETED if (operation_mode and not allows_kitchen) else OrderStatus.PENDING

    db_order = OrderModel(
        order_number=next_order_number,
        table_id=order.table_id,
        customer_name=getattr(order, 'customer_name', None),
        order_type=order_type,
        ticket_number=ticket_number,
        notes=order.notes,
        status=initial_status,
        is_paid=getattr(order, 'is_paid', False),
        restaurant_id=restaurant_id,
        user_id=user_id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(db_order)
    db.flush()

    total_amount = 0.0

    # Helper function to create order items
    def create_order_item(item_data: OrderItemCreate, person_id: Optional[int] = None):
        nonlocal total_amount
        
        menu_item = db.query(MenuItem).filter(MenuItem.id == item_data.menu_item_id).first()
        if not menu_item:
            raise ValueError(f"Menu item {item_data.menu_item_id} not found")

        variant = None
        unit_price = menu_item.get_effective_price()  # Use discount price if available
        if item_data.variant_id:
            variant = db.query(MenuItemVariant).filter(
                MenuItemVariant.id == item_data.variant_id,
                MenuItemVariant.menu_item_id == item_data.menu_item_id,
            ).first()
            if not variant:
                raise ValueError(
                    f"Variant {item_data.variant_id} not found for menu item {item_data.menu_item_id}"
                )
            unit_price = variant.get_effective_price()

        db_item = OrderItemModel(
            order_id=db_order.id,
            person_id=person_id,
            menu_item_id=item_data.menu_item_id,
            variant_id=item_data.variant_id,
            quantity=item_data.quantity,
            unit_price=unit_price,
            special_instructions=item_data.special_instructions,
            status=OrderStatus.PENDING,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(db_item)
        db.flush()  # Flush to get the item ID for extras
        
        # Add item price to total
        total_amount += unit_price * item_data.quantity
        
        # Add extras if provided
        if hasattr(item_data, 'extras') and item_data.extras:
            from ...models.order_item_extra import OrderItemExtra
            for extra_data in item_data.extras:
                db_extra = OrderItemExtra(
                    order_item_id=db_item.id,
                    name=extra_data.name,
                    price=extra_data.price,
                    quantity=extra_data.quantity,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc)
                )
                db.add(db_extra)
                # Add extra price to total
                total_amount += extra_data.price * extra_data.quantity

    # Process persons with their items (new multi-diner approach)
    has_persons = hasattr(order, 'persons') and order.persons
    if has_persons:
        for person_data in order.persons:
            # Create person
            db_person = OrderPersonModel(
                order_id=db_order.id,
                name=person_data.name,
                position=person_data.position,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            db.add(db_person)
            db.flush()  # Flush to get person ID
            
            # Create items for this person
            for item_data in person_data.items:
                create_order_item(item_data, person_id=db_person.id)
    
    # Process direct items ONLY if there are no persons (legacy support)
    # This prevents duplicate items when using multi-diner mode
    if not has_persons and hasattr(order, 'items') and order.items:
        for item_data in order.items:
            create_order_item(item_data, person_id=None)

    db_order.total_amount = total_amount
    db_order.updated_at = datetime.now(timezone.utc)
    
    # Mark table as occupied if this is a dine-in order AND order is not already paid
    if order.table_id and not getattr(order, 'is_paid', False):
        table = db.query(TableModel).filter(TableModel.id == order.table_id).first()
        if table and not table.is_occupied:
            table.is_occupied = True
            table.updated_at = datetime.now(timezone.utc)
    
    db.commit()

    return get_order(db, db_order.id, restaurant_id)


def update_order(db: Session, db_order: OrderModel, order: OrderUpdate) -> dict:
    """
    Update an existing order.
    
    Args:
        db: Database session
        db_order: Existing order model instance
        order: Update data
        
    Returns:
        Serialized updated order
    """
    update_data = order.dict(exclude_unset=True)
    
    # Remove fields that should not be updated directly
    update_data.pop('is_paid', None)  # Handled separately in payment_service
    update_data.pop('payment_method', None)  # Handled separately in payment_service

    # Validate and convert status if provided
    if 'status' in update_data:
        try:
            update_data['status'] = OrderStatus(update_data['status'])
            
            # Mark table as available if order is being cancelled
            if update_data['status'] == OrderStatus.CANCELLED and db_order.table_id:
                from .table_manager import mark_table_available_if_no_orders
                mark_table_available_if_no_orders(db, db_order.table_id, db_order.id)
                
        except ValueError:
            raise ValueError(f"Invalid status: {update_data['status']}")

    # Update order fields
    for field, value in update_data.items():
        setattr(db_order, field, value)
    
    db_order.updated_at = datetime.now(timezone.utc)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    return serialize_order(db_order)


def delete_order(db: Session, db_order: OrderModel) -> None:
    """
    Soft delete an order and its items.
    
    Args:
        db: Database session
        db_order: Order to delete
    """
    db_order.deleted_at = datetime.now(timezone.utc)
    db.add(db_order)
    
    # Soft delete all items
    for item in db_order.items:
        item.deleted_at = datetime.now(timezone.utc)
        db.add(item)
    
    db.commit()
