from fastapi import APIRouter, Depends, status, BackgroundTasks, Request
from sqlalchemy.orm import Session, selectinload
from typing import List, Optional

from ...db.base import get_db
from ...models.order import Order as OrderModel, OrderStatus
from ...models.order_item import OrderItem as OrderItemModel
from ...models.table import Table as TableModel
from ...models.menu import MenuItem as MenuItemModel
from ...models.restaurant import Restaurant
from ...models.user import User
from ...schemas.order import Order, OrderCreate, OrderUpdate, OrderItemCreate, OrderItemUpdate, OrderItem
from ...services import order as order_service
from ...services.order import serialize_order_item
from ...services.cash_register import create_transaction_from_order
from ...services.user import get_current_active_user
from ...core.dependencies import get_current_restaurant
from ...core.exceptions import ResourceNotFoundError, ValidationError, ConflictError, DatabaseError

router = APIRouter(
    prefix="/orders",
    tags=["orders"],
    dependencies=[Depends(get_current_active_user)],
    responses={404: {"description": "Not found"},
}
)


@router.get("/", response_model=List[Order])
async def read_orders(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    status: Optional[OrderStatus] = None,
    table_id: Optional[int] = None,
    sort_by: str = 'orders',
    db: Session = Depends(get_db),
    restaurant: Restaurant = Depends(get_current_restaurant),
    current_user: User = Depends(get_current_active_user)
) -> List[Order]:
    """
    Retrieve orders with optional filtering (filtered by restaurant).
    Waiters only see their own orders.
    sort_by: 'orders' (newest first by ID) or 'kitchen' (FIFO by status/created_at)
    """
    try:
        # If user is a waiter, filter to only their orders
        waiter_id = None
        if current_user.role == "staff" and current_user.staff_type == "waiter":
            waiter_id = current_user.id
        
        return order_service.get_orders(
            db,
            restaurant_id=restaurant.id,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            status=status,
            table_id=table_id,
            waiter_id=waiter_id
        )
    except Exception as e:
        raise DatabaseError(f"Error retrieving orders: {str(e)}", operation="select")



@router.post("/", response_model=Order, status_code=status.HTTP_201_CREATED)
async def create_order(
    request: Request,
    order: OrderCreate, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    restaurant: Restaurant = Depends(get_current_restaurant),
    current_user: User = Depends(get_current_active_user)
) -> Order:
    """
    Create a new order.
    """
    # Only validate table exists if table_id is provided (for dine-in orders)
    if order.table_id is not None:
        db_table = db.query(TableModel).filter(TableModel.id == order.table_id).first()
        if not db_table:
            raise ResourceNotFoundError("Table", order.table_id)
    
    for item in order.items:
        db_item = db.query(MenuItemModel).filter(MenuItemModel.id == item.menu_item_id).first()
        if not db_item:
            raise ResourceNotFoundError("MenuItem", item.menu_item_id)
    
    return order_service.create_order_with_items(db=db, order=order, restaurant_id=restaurant.id, user_id=current_user.id)


@router.get("/{order_id}", response_model=Order)
async def read_order(order_id: int, db: Session = Depends(get_db), restaurant: Restaurant = Depends(get_current_restaurant)) -> Order:
    """
    Get a specific order by ID.
    """
    db_order = order_service.get_order(db, order_id=order_id, restaurant_id=restaurant.id)
    if db_order is None:
        raise ResourceNotFoundError("Order", order_id)
    return db_order


@router.put("/{order_id}", response_model=Order)
async def update_order(order_id: int, order: OrderUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_active_user)) -> Order:
    """
    Update an order.
    """
    # First get the database order object
    db_order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if db_order is None:
        raise ResourceNotFoundError("Order", order_id)

    # Check if order is being marked as paid
    if order.is_paid and not db_order.is_paid:
        # Validate payment method if provided
        if order.payment_method is not None:
            from ...schemas.order import PaymentMethod
            try:
                payment_method_enum = PaymentMethod(order.payment_method.value)
            except (ValueError, AttributeError):
                raise ValidationError("Invalid payment method", field="payment_method")
            db_order.payment_method = payment_method_enum
        # If no payment method provided, default to CASH
        else:
            from ...schemas.order import PaymentMethod
            db_order.payment_method = PaymentMethod.CASH

        # Mark order as paid and completed
        db_order.is_paid = True
        db_order.status = OrderStatus.COMPLETED

        # Mark table as available if this is a dine-in order
        if db_order.table_id:
            from ...models.table import Table as TableModel
            table = db.query(TableModel).filter(TableModel.id == db_order.table_id).first()
            if table:
                # Check if there are other active orders for this table
                from datetime import datetime, timezone
                other_active_orders = db.query(OrderModel).filter(
                    OrderModel.table_id == db_order.table_id,
                    OrderModel.id != order_id,
                    OrderModel.status.in_([OrderStatus.PENDING, OrderStatus.PREPARING, OrderStatus.READY]),
                    OrderModel.is_paid == False
                ).count()
                
                # Only mark as available if no other active orders
                if other_active_orders == 0:
                    table.is_occupied = False
                    table.updated_at = datetime.now(timezone.utc)

        # Create cash register transaction
        try:
            create_transaction_from_order(
                db=db,
                order_id=order_id,
                created_by_user_id=current_user.id
            )
        except ValueError as e:
            raise ValidationError(str(e))

        # Commit the payment changes first
        db.commit()
        db.refresh(db_order)

    # Update any other fields from the request
    if order.dict(exclude_unset=True):
        updated_order = order_service.update_order(db=db, db_order=db_order, order=order)
        return updated_order
    else:
        # If no other updates, just return the current order
        return order_service.get_order(db, order_id, db_order.restaurant_id)




@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(order_id: int, db: Session = Depends(get_db)) -> None:
    """
    Delete an order.
    """
    db_order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if db_order is None:
        raise ResourceNotFoundError("Order", order_id)
    
    order_service.delete_order(db, db_order=db_order)


@router.post("/{order_id}/items", response_model=OrderItem, status_code=status.HTTP_201_CREATED)
async def add_order_item(order_id: int, item: OrderItemCreate, db: Session = Depends(get_db)) -> OrderItem:
    """
    Add an item to an existing order.
    """
    # Fetch the ORM model, not the serialized dict
    db_order = db.query(OrderModel).filter(OrderModel.id == order_id, OrderModel.deleted_at.is_(None)).first()
    if not db_order:
        raise ResourceNotFoundError("Order", order_id)
    
    db_menu_item = db.query(MenuItemModel).filter(MenuItemModel.id == item.menu_item_id).first()
    if not db_menu_item:
        raise ResourceNotFoundError("MenuItem", item.menu_item_id)
    
    # If order was preparing or ready, change it back to pending since there's a new item
    if db_order.status in [OrderStatus.PREPARING, OrderStatus.READY]:
        db_order.status = OrderStatus.PENDING
    
    # Set sort to 1 to give priority (items added to existing order)
    db_order.sort = 1
    
    # Always update updated_at when adding items to track latest activity
    from datetime import datetime, timezone
    db_order.updated_at = datetime.now(timezone.utc)
    db.commit()
    
    # Add the item (will be created with status=PENDING)
    result = order_service.add_order_item(db=db, db_order=db_order, item=item, unit_price=db_menu_item.price)
    
    return result


@router.post("/{order_id}/items/bulk", response_model=Order, status_code=status.HTTP_201_CREATED)
async def add_multiple_items_to_order(
    order_id: int, 
    items: List[OrderItemCreate], 
    db: Session = Depends(get_db),
    restaurant: Restaurant = Depends(get_current_restaurant)
) -> Order:
    """
    Add multiple items to an existing order at once.
    This is useful when customers order additional items after their initial order.
    """
    # Validate order exists and is not deleted
    db_order = db.query(OrderModel).filter(
        OrderModel.id == order_id, 
        OrderModel.deleted_at.is_(None),
        OrderModel.restaurant_id == restaurant.id
    ).first()
    if not db_order:
        raise ResourceNotFoundError("Order", order_id)
    
    # Validate order is still open (not completed or cancelled)
    if db_order.status in [OrderStatus.COMPLETED, OrderStatus.CANCELLED]:
        raise ConflictError(
            f"Cannot add items to a {db_order.status.value} order",
            resource="Order"
        )
    
    # Validate all menu items exist
    for item in items:
        db_menu_item = db.query(MenuItemModel).filter(MenuItemModel.id == item.menu_item_id).first()
        if not db_menu_item:
            raise ResourceNotFoundError("MenuItem", item.menu_item_id)
    
    # Add all items (they will be created with status=PENDING)
    for item in items:
        db_menu_item = db.query(MenuItemModel).filter(MenuItemModel.id == item.menu_item_id).first()
        order_service.add_order_item(db=db, db_order=db_order, item=item, unit_price=db_menu_item.price)
    
    # If order was preparing or ready, change it back to pending since there are new items
    if db_order.status in [OrderStatus.PREPARING, OrderStatus.READY]:
        db_order.status = OrderStatus.PENDING
    
    # Set sort to 1 to give priority (items added to existing order)
    db_order.sort = 1
    
    # Always update updated_at when adding items to track latest activity
    from datetime import datetime, timezone
    db_order.updated_at = datetime.now(timezone.utc)
    db.commit()
    
    # Return updated order with all items
    return order_service.get_order(db, order_id=order_id, restaurant_id=restaurant.id)


@router.put("/{order_id}/items/{item_id}", response_model=OrderItem)
async def update_order_item(order_id: int, item_id: int, item: OrderItemUpdate, db: Session = Depends(get_db)) -> OrderItem:
    """
    Update an order item.
    """
    db_order_item = order_service.get_order_item(db, item_id=item_id)
    if not db_order_item or db_order_item.order_id != order_id:
        raise ResourceNotFoundError("OrderItem", item_id)
    
    return order_service.update_order_item(db=db, db_item=db_order_item, item=item)


@router.patch("/{order_id}/items/{item_id}/status", response_model=OrderItem)
async def update_order_item_status(
    order_id: int, 
    item_id: int, 
    status: str, 
    db: Session = Depends(get_db)
) -> OrderItem:
    """
    Update the status of an order item.
    """
    # Validate status parameter
    from ...models.order import OrderStatus
    try:
        status_enum = OrderStatus(status.lower())
    except ValueError:
        raise ValidationError(
            f"Invalid status. Must be one of: {', '.join([s.value for s in OrderStatus])}",
            field="status"
        )
    
    db_order_item = order_service.get_order_item(db, item_id=item_id)
    if not db_order_item or db_order_item.order_id != order_id:
        raise ResourceNotFoundError("OrderItem", item_id)
    
    # Update the status
    db_order_item.status = status_enum
    db.commit()
    db.refresh(db_order_item)
    
    return order_service.serialize_order_item(db_order_item)


@router.delete("/{order_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order_item(order_id: int, item_id: int, db: Session = Depends(get_db)) -> None:
    """
    Remove an item from an order.
    """
    db_order_item = order_service.get_order_item(db, item_id=item_id)
    if not db_order_item or db_order_item.order_id != order_id:
        raise ResourceNotFoundError("OrderItem", item_id)
    
    order_service.delete_order_item(db=db, db_item=db_order_item)


@router.patch("/{order_id}/pay", response_model=Order)
async def mark_order_as_paid(
    order_id: int,
    payment_method: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
) -> Order:
    """
    Mark an order as paid and create a cash register transaction.
    """
    # Get the order
    db_order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not db_order:
        raise ResourceNotFoundError("Order", order_id)

    if db_order.is_paid:
        raise ConflictError("Order is already paid", resource="Order")

    # Validate payment method
    from ...schemas.order import PaymentMethod
    try:
        payment_method_enum = PaymentMethod(payment_method.lower())
    except ValueError:
        raise ValidationError(
            f"Invalid payment method. Must be one of: {', '.join([pm.value for pm in PaymentMethod])}",
            field="payment_method"
        )

    try:
        # Create cash register transaction with payment method
        create_transaction_from_order(
            db=db,
            order_id=order_id,
            created_by_user_id=current_user.id,
            payment_method=payment_method
        )

        # Mark order as paid
        db_order.is_paid = True
        db_order.payment_method = payment_method_enum
        db_order.status = OrderStatus.COMPLETED

        # Mark table as available if this is a dine-in order
        if db_order.table_id:
            from ...models.table import Table as TableModel
            from datetime import datetime, timezone
            table = db.query(TableModel).filter(TableModel.id == db_order.table_id).first()
            if table:
                # Check if there are other active orders for this table
                other_active_orders = db.query(OrderModel).filter(
                    OrderModel.table_id == db_order.table_id,
                    OrderModel.id != order_id,
                    OrderModel.status.in_([OrderStatus.PENDING, OrderStatus.PREPARING, OrderStatus.READY]),
                    OrderModel.is_paid == False
                ).count()
                
                # Only mark as available if no other active orders
                if other_active_orders == 0:
                    table.is_occupied = False
                    table.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(db_order)

        return order_service.get_order(db, order_id, db_order.restaurant_id)

    except ValueError as e:
        raise ValidationError(str(e))
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Error processing payment: {str(e)}", operation="update")
