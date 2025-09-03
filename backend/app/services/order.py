from datetime import datetime
from sqlalchemy import or_
from typing import List, Optional
import logging
from sqlalchemy.orm import Session, selectinload, joinedload

from ..models.order import Order as OrderModel, OrderStatus
from ..models.order_item import OrderItem as OrderItemModel
from ..models.menu import MenuItem, MenuItemVariant
from ..schemas.order import OrderCreate, OrderUpdate, OrderItemCreate, OrderItemUpdate


# -----------------------------
# Serialization helpers
# -----------------------------

def serialize_menu_item(menu_item: Optional[MenuItem]) -> Optional[dict]:
    if not menu_item:
        return None
    return {
        "id": menu_item.id,
        "name": menu_item.name,
        "price": float(menu_item.price) if menu_item.price is not None else 0.0,
        "description": menu_item.description,
        "category": getattr(menu_item.category, "name", menu_item.category) if menu_item.category else None,
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
    return {
        "id": order.id,
        "table_id": order.table_id,
        "status": order.status,
        "notes": order.notes or None,
        "total_amount": float(order.total_amount) if order.total_amount is not None else 0.0,
        "created_at": order.created_at,
        "updated_at": order.updated_at,
        "table_number": order.table.number if order.table else None,
        "customer_name": getattr(order, "customer_name", None),
        "user_id": getattr(order, "user_id", None),
        "items": [serialize_order_item(item) for item in getattr(order, "items", [])],
    }


# -----------------------------
# Queries
# -----------------------------

def get_orders(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[OrderStatus] = None,
    table_id: Optional[int] = None,
    include_deleted: bool = False,
) -> List[dict]:
    try:
        query = db.query(OrderModel).options(
            joinedload(OrderModel.items).joinedload(OrderItemModel.menu_item),
            joinedload(OrderModel.items).joinedload(OrderItemModel.variant),
            joinedload(OrderModel.table),
            joinedload(OrderModel.user),
        )
        
        # Filter out deleted orders unless explicitly requested
        if not include_deleted:
            query = query.filter(OrderModel.deleted_at.is_(None))
        
        if status is not None:
            query = query.filter(OrderModel.status == status)
        if table_id is not None:
            query = query.filter(OrderModel.table_id == table_id)

        orders = query.order_by(OrderModel.created_at.desc()).offset(skip).limit(limit).all()
        return [serialize_order(order) for order in orders]

    except Exception as e:
        logging.error(f"Error in get_orders: {str(e)}", exc_info=True)
        raise


def get_order(db: Session, order_id: int, include_deleted: bool = False) -> Optional[dict]:
    try:
        query = db.query(OrderModel).options(
            joinedload(OrderModel.items).joinedload(OrderItemModel.menu_item),
            joinedload(OrderModel.items).joinedload(OrderItemModel.variant),
            joinedload(OrderModel.table),
            joinedload(OrderModel.user),
        ).filter(OrderModel.id == order_id)
        
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

def create_order_with_items(db: Session, order: OrderCreate) -> dict:
    db_order = OrderModel(
        table_id=order.table_id,
        notes=order.notes,
        status=OrderStatus.PENDING,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(db_order)
    db.flush()  # get order ID

    total_amount = 0.0

    for item in order.items:
        menu_item = db.query(MenuItem).filter(MenuItem.id == item.menu_item_id).first()
        if not menu_item:
            raise ValueError(f"Menu item {item.menu_item_id} not found")

        variant = None
        unit_price = menu_item.price
        if item.variant_id:
            variant = (
                db.query(MenuItemVariant)
                .filter(
                    MenuItemVariant.id == item.variant_id,
                    MenuItemVariant.menu_item_id == item.menu_item_id,
                )
                .first()
            )
            if not variant:
                raise ValueError(f"Variant {item.variant_id} not found for menu item {item.menu_item_id}")
            unit_price = variant.price

        db_item = OrderItemModel(
            order_id=db_order.id,
            menu_item_id=item.menu_item_id,
            variant_id=item.variant_id,
            quantity=item.quantity,
            unit_price=unit_price,
            special_instructions=item.special_instructions,
            status=OrderStatus.PENDING,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(db_item)
        total_amount += unit_price * item.quantity

    db_order.total_amount = total_amount
    db_order.updated_at = datetime.utcnow()
    db.commit()
    return get_order(db, db_order.id)


def update_order(db: Session, db_order: OrderModel, order: OrderUpdate) -> dict:
    update_data = order.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_order, field, value)

    db_order.updated_at = datetime.utcnow()
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    # Return the serialized order
    return serialize_order(db_order)


def delete_order(db: Session, db_order: OrderModel) -> None:
    # Soft delete the order
    db_order.deleted_at = datetime.utcnow()
    db.add(db_order)
    
    # Also soft delete all order items
    for item in db_order.items:
        item.deleted_at = datetime.utcnow()
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
    unit_price = menu_item.price
    if item.variant_id:
        variant = (
            db.query(MenuItemVariant)
            .filter(
                MenuItemVariant.id == item.variant_id,
                MenuItemVariant.menu_item_id == item.menu_item_id,
            )
            .first()
        )
        if not variant:
            raise ValueError(f"Variant {item.variant_id} not found for menu item {item.menu_item_id}")
        unit_price = variant.price

    db_item = OrderItemModel(
        order_id=db_order.id,
        menu_item_id=item.menu_item_id,
        variant_id=item.variant_id,
        quantity=item.quantity,
        unit_price=unit_price,
        special_instructions=item.special_instructions,
        status=OrderStatus.PENDING,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(db_item)

    db_order.total_amount = (db_order.total_amount or 0) + (unit_price * item.quantity)
    db_order.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(db_item)

    return serialize_order_item(db_item)


def update_order_item(db: Session, db_item: OrderItemModel, item: OrderItemUpdate) -> dict:
    update_data = item.dict(exclude_unset=True)

    if "variant_id" in update_data and update_data["variant_id"] != db_item.variant_id:
        if update_data["variant_id"]:
            variant = (
                db.query(MenuItemVariant)
                .filter(
                    MenuItemVariant.id == update_data["variant_id"],
                    MenuItemVariant.menu_item_id == db_item.menu_item_id,
                )
                .first()
            )
            if not variant:
                raise ValueError(f"Variant {update_data['variant_id']} not found")
            update_data["unit_price"] = variant.price
        else:
            menu_item = db.query(MenuItem).filter(MenuItem.id == db_item.menu_item_id).first()
            if menu_item:
                update_data["unit_price"] = menu_item.price

    for field, value in update_data.items():
        setattr(db_item, field, value)

    db_item.updated_at = datetime.utcnow()

    order = db.query(OrderModel).filter(OrderModel.id == db_item.order_id).first()
    if order:
        order.total_amount = sum(i.quantity * (i.unit_price or 0) for i in order.items)
        order.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(db_item)

    return serialize_order_item(db_item)


def delete_order_item(db: Session, db_item: OrderItemModel) -> None:
    # Soft delete the order item
    db_item.deleted_at = datetime.utcnow()
    db.add(db_item)
    
    # Update the order total
    order = db.query(OrderModel).filter(OrderModel.id == db_item.order_id).first()
    if order:
        # Recalculate the total based on non-deleted items
        order.total_amount = sum(
            item.quantity * item.unit_price 
            for item in order.items 
            if item.deleted_at is None and item.id != db_item.id
        )
        order.updated_at = datetime.utcnow()
        db.add(order)
    
    db.commit()
