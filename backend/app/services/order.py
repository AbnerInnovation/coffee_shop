from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..models.order import Order as OrderModel, OrderStatus
from ..models.order_item import OrderItem as OrderItemModel
from ..models.menu import MenuItem, MenuItemVariant
from ..schemas.order import OrderCreate, OrderUpdate, OrderItemCreate, OrderItemUpdate

def get_orders(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    status: Optional[OrderStatus] = None,
    table_id: Optional[int] = None
) -> List[OrderModel]:
    """
    Retrieve orders with optional filtering.
    """
    query = db.query(OrderModel)
    
    if status is not None:
        query = query.filter(OrderModel.status == status)
    if table_id is not None:
        query = query.filter(OrderModel.table_id == table_id)
        
    return query.offset(skip).limit(limit).all()

def get_order(db: Session, order_id: int) -> Optional[OrderModel]:
    """
    Get a single order by ID.
    """
    return db.query(OrderModel).filter(OrderModel.id == order_id).first()

def create_order_with_items(db: Session, order: OrderCreate) -> OrderModel:
    """
    Create a new order with order items, handling menu item variants.
    """
    db_order = OrderModel(
        table_id=order.table_id,
        notes=order.notes,
        status=OrderStatus.PENDING,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(db_order)
    db.flush()  # Flush to get the order ID
    
    total_amount = 0.0
    
    for item in order.items:
        # Get the menu item
        menu_item = db.query(MenuItem).filter(MenuItem.id == item.menu_item_id).first()
        if not menu_item:
            raise ValueError(f"Menu item with ID {item.menu_item_id} not found")
        
        # Get the variant if specified
        variant = None
        if item.variant_id:
            variant = db.query(MenuItemVariant).filter(
                MenuItemVariant.id == item.variant_id,
                MenuItemVariant.menu_item_id == item.menu_item_id
            ).first()
            if not variant:
                raise ValueError(f"Variant with ID {item.variant_id} not found for menu item {item.menu_item_id}")
            unit_price = variant.price
            variant_name = variant.name
        else:
            unit_price = menu_item.price
            variant_name = None
        
        # Create order item
        db_item = OrderItemModel(
            order_id=db_order.id,
            menu_item_id=item.menu_item_id,
            variant_id=item.variant_id,
            quantity=item.quantity,
            unit_price=unit_price,
            special_instructions=item.special_instructions,
            status=OrderStatus.PENDING,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(db_item)
        total_amount += unit_price * item.quantity
    
    # Update order total
    db_order.total_amount = total_amount
    db_order.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_order)
    return db_order

def update_order(
    db: Session, 
    db_order: OrderModel, 
    order: OrderUpdate
) -> OrderModel:
    """
    Update an existing order.
    """
    update_data = order.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_order, field, value)
    
    db_order.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_order)
    return db_order

def delete_order(db: Session, db_order: OrderModel) -> None:
    """
    Delete an order.
    """
    db.delete(db_order)
    db.commit()

def get_order_item(db: Session, item_id: int) -> Optional[OrderItemModel]:
    """
    Get a single order item by ID.
    """
    return db.query(OrderItemModel).filter(OrderItemModel.id == item_id).first()

def add_order_item(
    db: Session,
    db_order: OrderModel,
    item: OrderItemCreate,
    unit_price: float
) -> OrderItemModel:
    """
    Add an item to an existing order, handling menu item variants.
    """
    # Get the menu item and variant
    menu_item = db.query(MenuItem).filter(MenuItem.id == item.menu_item_id).first()
    if not menu_item:
        raise ValueError(f"Menu item with ID {item.menu_item_id} not found")
    
    # Get the variant if specified
    variant = None
    if item.variant_id:
        variant = db.query(MenuItemVariant).filter(
            MenuItemVariant.id == item.variant_id,
            MenuItemVariant.menu_item_id == item.menu_item_id
        ).first()
        if not variant:
            raise ValueError(f"Variant with ID {item.variant_id} not found for menu item {item.menu_item_id}")
        unit_price = variant.price
        variant_name = variant.name
    else:
        unit_price = menu_item.price
        variant_name = None
    
    # Create order item
    db_item = OrderItemModel(
        order_id=db_order.id,
        menu_item_id=item.menu_item_id,
        variant_id=item.variant_id,
        quantity=item.quantity,
        unit_price=unit_price,
        special_instructions=item.special_instructions,
        status=OrderStatus.PENDING,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(db_item)
    
    # Update order total
    db_order.total_amount = (db_order.total_amount or 0) + (unit_price * item.quantity)
    db_order.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_item)
    return db_item

def update_order_item(
    db: Session,
    db_item: OrderItemModel,
    item: OrderItemUpdate
) -> OrderItemModel:
    """
    Update an existing order item, handling menu item variants if changed.
    """
    update_data = item.dict(exclude_unset=True)
    
    # Handle variant changes
    if 'variant_id' in update_data and update_data['variant_id'] != db_item.variant_id:
        variant = None
        if update_data['variant_id']:
            variant = db.query(MenuItemVariant).filter(
                MenuItemVariant.id == update_data['variant_id'],
                MenuItemVariant.menu_item_id == db_item.menu_item_id
            ).first()
            if not variant:
                raise ValueError(f"Variant with ID {update_data['variant_id']} not found for menu item {db_item.menu_item_id}")
            update_data['unit_price'] = variant.price
        else:
            menu_item = db.query(MenuItem).filter(MenuItem.id == db_item.menu_item_id).first()
            if menu_item:
                update_data['unit_price'] = menu_item.price
    
    # Update the item
    for field, value in update_data.items():
        setattr(db_item, field, value)
    
    db_item.updated_at = datetime.utcnow()
    
    # Recalculate order total if quantity or price changed
    if 'quantity' in update_data or 'unit_price' in update_data:
        order = db.query(OrderModel).filter(OrderModel.id == db_item.order_id).first()
        if order:
            order.total_amount = sum(
                item.quantity * item.unit_price 
                for item in order.items
            )
            order.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_order_item(db: Session, db_item: OrderItemModel) -> None:
    """
    Remove an item from an order.
    """
    order = db.query(OrderModel).filter(OrderModel.id == db_item.order_id).first()
    if order:
        # Update order total
        order.total_amount = max(0, (order.total_amount or 0) - (db_item.quantity * db_item.unit_price))
        order.updated_at = datetime.utcnow()
    
    db.delete(db_item)
    db.commit()
