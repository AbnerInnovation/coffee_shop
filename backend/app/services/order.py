from datetime import datetime, timezone
from sqlalchemy import or_, and_, func as sa_func
from typing import List, Optional, Dict, Any
import logging
from sqlalchemy.orm import Session, joinedload
import sqlalchemy as sa

from ..models.order import Order as OrderModel, OrderStatus
from ..models.order_item import OrderItem as OrderItemModel
from ..models.menu import MenuItem, MenuItemVariant
from ..schemas.order import OrderCreate, OrderUpdate, OrderItemCreate, OrderItemUpdate

# -----------------------------
# Serialization helpers
# -----------------------------

def serialize_menu_item(menu_item: MenuItem) -> dict:
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
    if not variant:
        return None
    return {
        "id": variant.id,
        "name": variant.name,
        "price": float(variant.price) if variant.price is not None else 0.0,
        "discount_price": float(variant.discount_price) if variant.discount_price is not None else None,
        "description": getattr(variant, "description", None),
    }

def serialize_order_item(item: OrderItemModel) -> dict:
    return {
        "id": item.id,
        "order_id": item.order_id,
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
    }

def serialize_order(order: OrderModel) -> dict:
    # Calculate subtotal from items
    items = getattr(order, "items", [])
    subtotal = sum(item.quantity * (item.unit_price or 0) for item in items)
    
    # For now, tax is 0 (can be configured later)
    tax = 0.0
    total = subtotal + tax
    
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
    }

# -----------------------------
# Query helpers
# -----------------------------

def apply_filters(query, filters: Dict[str, Any]):
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
        query = query.filter(or_(OrderModel.notes.ilike(search_term), OrderModel.customer_name.ilike(search_term)))

    return query

# -----------------------------
# Queries
# -----------------------------

def get_orders(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    sort_by: str = 'kitchen',
    **filters,
) -> List[dict]:
    try:
        query = db.query(OrderModel).options(
            joinedload(OrderModel.items).joinedload(OrderItemModel.menu_item),
            joinedload(OrderModel.items).joinedload(OrderItemModel.variant),
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
            from sqlalchemy import case
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

def get_order(db: Session, order_id: int, restaurant_id: int, include_deleted: bool = False) -> Optional[dict]:
    try:
        query = db.query(OrderModel).options(
            joinedload(OrderModel.items).joinedload(OrderItemModel.menu_item),
            joinedload(OrderModel.items).joinedload(OrderItemModel.variant),
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

# -----------------------------
# CRUD
# -----------------------------

def create_order_with_items(db: Session, order: OrderCreate, restaurant_id: int, user_id: int = None) -> dict:
    # Set order_type based on whether table_id is provided
    order_type = "dine_in" if order.table_id is not None else "delivery"

    # Get the next order number for this restaurant
    max_order_number = db.query(sa.func.max(OrderModel.order_number)).filter(
        OrderModel.restaurant_id == restaurant_id
    ).scalar()
    next_order_number = (max_order_number or 0) + 1

    db_order = OrderModel(
        order_number=next_order_number,
        table_id=order.table_id,
        customer_name=getattr(order, 'customer_name', None),  # Add customer_name if provided
        order_type=order_type,
        notes=order.notes,
        status=OrderStatus.PENDING,
        restaurant_id=restaurant_id,
        user_id=user_id,  # Set the user who created the order
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(db_order)
    db.flush()

    total_amount = 0.0

    for item in order.items:
        menu_item = db.query(MenuItem).filter(MenuItem.id == item.menu_item_id).first()
        if not menu_item:
            raise ValueError(f"Menu item {item.menu_item_id} not found")

        variant = None
        unit_price = menu_item.get_effective_price()  # Use discount price if available
        if item.variant_id:
            variant = db.query(MenuItemVariant).filter(
                MenuItemVariant.id == item.variant_id,
                MenuItemVariant.menu_item_id == item.menu_item_id,
            ).first()
            if not variant:
                raise ValueError(f"Variant {item.variant_id} not found for menu item {item.menu_item_id}")
            unit_price = variant.get_effective_price()  # Use discount price if available

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
        total_amount += unit_price * item.quantity

    db_order.total_amount = total_amount
    db_order.updated_at = datetime.now(timezone.utc)
    
    # Mark table as occupied if this is a dine-in order AND order is not already paid
    # If order enters already paid, table management is manual
    if order.table_id and not getattr(order, 'is_paid', False):
        from ..models.table import Table as TableModel
        table = db.query(TableModel).filter(TableModel.id == order.table_id).first()
        if table and not table.is_occupied:
            table.is_occupied = True
            table.updated_at = datetime.now(timezone.utc)
    
    db.commit()

    return get_order(db, db_order.id, restaurant_id)

def update_order(db: Session, db_order: OrderModel, order: OrderUpdate) -> dict:
    update_data = order.dict(exclude_unset=True)
    # Remove fields that should not be updated directly
    update_data.pop('is_paid', None)  # Handled separately in the router
    update_data.pop('payment_method', None)  # Handled separately in the router

    # Validate and convert status if provided
    if 'status' in update_data:
        try:
            from ..models.order import OrderStatus
            update_data['status'] = OrderStatus(update_data['status'])
            
            # Mark table as available if order is being cancelled
            if update_data['status'] == OrderStatus.CANCELLED and db_order.table_id:
                from ..models.table import Table as TableModel
                table = db.query(TableModel).filter(TableModel.id == db_order.table_id).first()
                if table:
                    # Check if there are other active orders for this table
                    other_active_orders = db.query(OrderModel).filter(
                        OrderModel.table_id == db_order.table_id,
                        OrderModel.id != db_order.id,
                        OrderModel.status.in_([OrderStatus.PENDING, OrderStatus.PREPARING, OrderStatus.READY]),
                        OrderModel.is_paid == False
                    ).count()
                    
                    # Only mark as available if no other active orders
                    if other_active_orders == 0:
                        table.is_occupied = False
                        table.updated_at = datetime.now(timezone.utc)
        except ValueError:
            raise ValueError(f"Invalid status. Must be one of: {', '.join([s.value for s in OrderStatus])}")

    for field, value in update_data.items():
        setattr(db_order, field, value)

    db_order.updated_at = datetime.now(timezone.utc)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return serialize_order(db_order)

def delete_order(db: Session, db_order: OrderModel) -> None:
    db_order.deleted_at = datetime.now(timezone.utc)
    db.add(db_order)
    for item in db_order.items:
        item.deleted_at = datetime.now(timezone.utc)
        db.add(item)
    db.commit()

# -----------------------------
# Order items
# -----------------------------

def get_order_item(db: Session, item_id: int, include_deleted: bool = False) -> Optional[OrderItemModel]:
    query = db.query(OrderItemModel).filter(OrderItemModel.id == item_id)
    if not include_deleted:
        query = query.filter(OrderItemModel.deleted_at.is_(None))
    return query.first()

def add_order_item(db: Session, db_order: OrderModel, item: OrderItemCreate, unit_price: float) -> dict:
    menu_item = db.query(MenuItem).filter(MenuItem.id == item.menu_item_id).first()
    if not menu_item:
        raise ValueError(f"Menu item {item.menu_item_id} not found")

    variant = None
    unit_price = menu_item.get_effective_price()  # Use discount price if available
    if item.variant_id:
        variant = db.query(MenuItemVariant).filter(
            MenuItemVariant.id == item.variant_id,
            MenuItemVariant.menu_item_id == item.menu_item_id,
        ).first()
        if not variant:
            raise ValueError(f"Variant {item.variant_id} not found for menu item {item.menu_item_id}")
        unit_price = variant.get_effective_price()  # Use discount price if available

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
    db_order.total_amount = (db_order.total_amount or 0) + (unit_price * item.quantity)
    db_order.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_item)
    return serialize_order_item(db_item)

def update_order_item(db: Session, db_item: OrderItemModel, item: OrderItemUpdate) -> dict:
    update_data = item.dict(exclude_unset=True)
    if "variant_id" in update_data and update_data["variant_id"] != db_item.variant_id:
        if update_data["variant_id"]:
            variant = db.query(MenuItemVariant).filter(
                MenuItemVariant.id == update_data["variant_id"],
                MenuItemVariant.menu_item_id == db_item.menu_item_id,
            ).first()
            if not variant:
                raise ValueError(f"Variant {update_data['variant_id']} not found")
            update_data["unit_price"] = variant.get_effective_price()  # Use discount price if available
        else:
            menu_item = db.query(MenuItem).filter(MenuItem.id == db_item.menu_item_id).first()
            if menu_item:
                update_data["unit_price"] = menu_item.get_effective_price()  # Use discount price if available

    # Validate and convert status if provided
    if 'status' in update_data:
        try:
            from ..models.order import OrderStatus
            update_data['status'] = OrderStatus(update_data['status'])
        except ValueError:
            raise ValueError(f"Invalid status. Must be one of: {', '.join([s.value for s in OrderStatus])}")

    for field, value in update_data.items():
        setattr(db_item, field, value)

    db_item.updated_at = datetime.now(timezone.utc)
    order = db.query(OrderModel).filter(OrderModel.id == db_item.order_id).first()
    if order:
        order.total_amount = sum(i.quantity * (i.unit_price or 0) for i in order.items)
        order.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(db_item)
    return serialize_order_item(db_item)

def delete_order_item(db: Session, db_item: OrderItemModel) -> None:
    db_item.deleted_at = datetime.now(timezone.utc)
    db.add(db_item)
    order = db.query(OrderModel).filter(OrderModel.id == db_item.order_id).first()
    if order:
        order.total_amount = sum(
            item.quantity * item.unit_price for item in order.items if item.deleted_at is None and item.id != db_item.id
        )
        order.updated_at = datetime.now(timezone.utc)
        db.add(order)
    db.commit()
