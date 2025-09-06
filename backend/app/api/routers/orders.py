from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session, selectinload
from typing import List

from ...db.base import get_db
from ...models.order import Order as OrderModel, OrderStatus
from ...models.order_item import OrderItem as OrderItemModel
from ...models.table import Table as TableModel
from ...models.menu import MenuItem as MenuItemModel
from ...schemas.order import Order, OrderCreate, OrderUpdate, OrderItemCreate, OrderItemUpdate, OrderItem
from ...services import order as order_service
from ...services.user import get_current_active_user

router = APIRouter(
    prefix="/orders",
    tags=["orders"],
    dependencies=[Depends(get_current_active_user)],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=List[Order])
async def read_orders(
    skip: int = 0, 
    limit: int = 100,
    status: OrderStatus = None,
    table_id: int = None,
    db: Session = Depends(get_db)
) -> List[Order]:
    """
    Retrieve orders with optional filtering.
    """
    try:
        return order_service.get_orders(
            db, 
            skip=skip, 
            limit=limit, 
            status=status,
            table_id=table_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving orders: {str(e)}")


@router.post("/", response_model=Order, status_code=status.HTTP_201_CREATED)
async def create_order(
    order: OrderCreate, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> Order:
    """
    Create a new order.
    """
    db_table = db.query(TableModel).filter(TableModel.id == order.table_id).first()
    if not db_table:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")
    
    for item in order.items:
        db_item = db.query(MenuItemModel).filter(MenuItemModel.id == item.menu_item_id).first()
        if not db_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Menu item with ID {item.menu_item_id} not found"
            )
    
    return order_service.create_order_with_items(db=db, order=order)


@router.get("/{order_id}", response_model=Order)
async def read_order(order_id: int, db: Session = Depends(get_db)) -> Order:
    """
    Get a specific order by ID.
    """
    db_order = order_service.get_order(db, order_id=order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order


@router.put("/{order_id}", response_model=Order)
async def update_order(order_id: int, order: OrderUpdate, db: Session = Depends(get_db)) -> Order:
    """
    Update an order.
    """
    # First get the database order object
    db_order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    # Update the order in the database
    updated_order = order_service.update_order(db=db, db_order=db_order, order=order)
    
    # Return the updated order
    return updated_order




@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(order_id: int, db: Session = Depends(get_db)) -> None:
    """
    Delete an order.
    """
    db_order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    order_service.delete_order(db, db_order=db_order)


@router.post("/{order_id}/items", response_model=OrderItem, status_code=status.HTTP_201_CREATED)
async def add_order_item(order_id: int, item: OrderItemCreate, db: Session = Depends(get_db)) -> OrderItem:
    """
    Add an item to an existing order.
    """
    db_order = order_service.get_order(db, order_id=order_id)
    if not db_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    db_menu_item = db.query(MenuItemModel).filter(MenuItemModel.id == item.menu_item_id).first()
    if not db_menu_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Menu item with ID {item.menu_item_id} not found"
        )
    
    return order_service.add_order_item(db=db, db_order=db_order, item=item, unit_price=db_menu_item.price)


@router.put("/{order_id}/items/{item_id}", response_model=OrderItem)
async def update_order_item(order_id: int, item_id: int, item: OrderItemUpdate, db: Session = Depends(get_db)) -> OrderItem:
    """
    Update an order item.
    """
    db_order_item = order_service.get_order_item(db, item_id=item_id)
    if not db_order_item or db_order_item.order_id != order_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order item not found")
    
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
    db_order_item = order_service.get_order_item(db, item_id=item_id)
    if not db_order_item or db_order_item.order_id != order_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order item not found")
    
    # Update the status
    db_order_item.status = status
    db.commit()
    db.refresh(db_order_item)
    
    return db_order_item


@router.delete("/{order_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order_item(order_id: int, item_id: int, db: Session = Depends(get_db)) -> None:
    """
    Remove an item from an order.
    """
    db_order_item = order_service.get_order_item(db, item_id=item_id)
    if not db_order_item or db_order_item.order_id != order_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order item not found")
    
    order_service.delete_order_item(db=db, db_item=db_order_item)
