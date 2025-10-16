"""
Example endpoint demonstrating proper exception handling usage.

This file shows how to use custom exceptions in a real FastAPI endpoint.
Copy these patterns to your own endpoints for consistent error handling.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.core.exceptions import (
    ResourceNotFoundError,
    ValidationError,
    UnauthorizedError,
    ForbiddenError,
    ConflictError,
    DatabaseError
)
from app.db.base import get_db
from app.models.order import Order
from app.models.table import Table
from app.schemas.order import OrderCreate, OrderResponse
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()


# Example 1: GET endpoint with ResourceNotFoundError
@router.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific order by ID.
    
    Raises:
        ResourceNotFoundError: If order doesn't exist
        ForbiddenError: If user doesn't have access to this order
    """
    # Query the order
    order = db.query(Order).filter(Order.id == order_id).first()
    
    # Raise 404 if not found
    if not order:
        raise ResourceNotFoundError("Order", order_id)
    
    # Check permissions
    if order.restaurant_id != current_user.restaurant_id and not current_user.is_admin:
        raise ForbiddenError(
            "You don't have permission to view this order",
            required_permission="same_restaurant_or_admin"
        )
    
    return order


# Example 2: POST endpoint with validation and conflict errors
@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new order.
    
    Raises:
        ValidationError: If input data is invalid
        ResourceNotFoundError: If table doesn't exist
        ConflictError: If table already has an open order
        DatabaseError: If database operation fails
    """
    # Validate table exists
    table = db.query(Table).filter(Table.id == order_data.table_id).first()
    if not table:
        raise ResourceNotFoundError("Table", order_data.table_id)
    
    # Validate table is available
    if table.status != "available":
        raise ValidationError(
            f"Table is currently {table.status}",
            field="table_id"
        )
    
    # Check for existing open orders on this table
    existing_order = db.query(Order).filter(
        Order.table_id == order_data.table_id,
        Order.status.in_(["pending", "preparing", "ready"])
    ).first()
    
    if existing_order:
        raise ConflictError(
            f"Table {order_data.table_id} already has an open order (#{existing_order.id})",
            resource="Order"
        )
    
    # Validate order items
    if not order_data.items or len(order_data.items) == 0:
        raise ValidationError("Order must contain at least one item", field="items")
    
    # Calculate total
    total = sum(item.price * item.quantity for item in order_data.items)
    if total <= 0:
        raise ValidationError("Order total must be greater than 0", field="total")
    
    # Create the order
    try:
        new_order = Order(
            table_id=order_data.table_id,
            restaurant_id=current_user.restaurant_id,
            user_id=current_user.id,
            status="pending",
            total=total
        )
        
        db.add(new_order)
        db.commit()
        db.refresh(new_order)
        
        # Update table status
        table.status = "occupied"
        db.commit()
        
        return new_order
        
    except Exception as e:
        db.rollback()
        raise DatabaseError(
            "Failed to create order",
            operation="insert"
        )


# Example 3: PUT endpoint with multiple error types
@router.put("/orders/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    new_status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update order status.
    
    Raises:
        ResourceNotFoundError: If order doesn't exist
        ValidationError: If status transition is invalid
        ForbiddenError: If user lacks permission
    """
    # Valid status transitions
    VALID_STATUSES = ["pending", "preparing", "ready", "completed", "cancelled"]
    STATUS_TRANSITIONS = {
        "pending": ["preparing", "cancelled"],
        "preparing": ["ready", "cancelled"],
        "ready": ["completed", "cancelled"],
        "completed": [],  # Terminal state
        "cancelled": []   # Terminal state
    }
    
    # Validate status value
    if new_status not in VALID_STATUSES:
        raise ValidationError(
            f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}",
            field="status"
        )
    
    # Get the order
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise ResourceNotFoundError("Order", order_id)
    
    # Check permissions
    if order.restaurant_id != current_user.restaurant_id:
        raise ForbiddenError("You can only update orders from your restaurant")
    
    # Validate status transition
    current_status = order.status
    allowed_transitions = STATUS_TRANSITIONS.get(current_status, [])
    
    if new_status not in allowed_transitions:
        raise ValidationError(
            f"Cannot transition from '{current_status}' to '{new_status}'. "
            f"Allowed transitions: {', '.join(allowed_transitions) if allowed_transitions else 'none (terminal state)'}",
            field="status"
        )
    
    # Update the order
    try:
        order.status = new_status
        db.commit()
        db.refresh(order)
        return order
    except Exception as e:
        db.rollback()
        raise DatabaseError(
            "Failed to update order status",
            operation="update"
        )


# Example 4: DELETE endpoint
@router.delete("/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an order (admin only).
    
    Raises:
        ResourceNotFoundError: If order doesn't exist
        ForbiddenError: If user is not an admin
        ConflictError: If order cannot be deleted in current state
    """
    # Check admin permission
    if not current_user.is_admin:
        raise ForbiddenError(
            "Only administrators can delete orders",
            required_permission="admin"
        )
    
    # Get the order
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise ResourceNotFoundError("Order", order_id)
    
    # Check if order can be deleted
    if order.status == "completed":
        raise ConflictError(
            "Cannot delete completed orders. Please cancel first.",
            resource="Order"
        )
    
    # Delete the order
    try:
        db.delete(order)
        db.commit()
    except Exception as e:
        db.rollback()
        raise DatabaseError(
            "Failed to delete order",
            operation="delete"
        )


# Example 5: Batch operation with multiple error types
@router.post("/orders/batch-cancel")
def batch_cancel_orders(
    order_ids: List[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cancel multiple orders at once.
    
    Raises:
        ValidationError: If input is invalid
        ForbiddenError: If user lacks permission
    """
    # Validate input
    if not order_ids or len(order_ids) == 0:
        raise ValidationError("Must provide at least one order ID", field="order_ids")
    
    if len(order_ids) > 50:
        raise ValidationError("Cannot cancel more than 50 orders at once", field="order_ids")
    
    # Check admin permission
    if not current_user.is_admin:
        raise ForbiddenError(
            "Only administrators can batch cancel orders",
            required_permission="admin"
        )
    
    # Get all orders
    orders = db.query(Order).filter(Order.id.in_(order_ids)).all()
    
    # Track results
    cancelled = []
    failed = []
    
    for order in orders:
        if order.status in ["pending", "preparing", "ready"]:
            order.status = "cancelled"
            cancelled.append(order.id)
        else:
            failed.append({
                "order_id": order.id,
                "reason": f"Cannot cancel order in '{order.status}' status"
            })
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise DatabaseError(
            "Failed to cancel orders",
            operation="batch_update"
        )
    
    return {
        "success": True,
        "cancelled": cancelled,
        "failed": failed,
        "total_requested": len(order_ids),
        "total_cancelled": len(cancelled)
    }


# Example 6: Complex validation with multiple checks
@router.post("/orders/{order_id}/items")
def add_order_item(
    order_id: int,
    item_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add an item to an existing order.
    
    Demonstrates complex validation with multiple error types.
    """
    # Get the order
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise ResourceNotFoundError("Order", order_id)
    
    # Check order status
    if order.status not in ["pending", "preparing"]:
        raise ConflictError(
            f"Cannot add items to order in '{order.status}' status",
            resource="Order"
        )
    
    # Validate item data
    if "menu_item_id" not in item_data:
        raise ValidationError("menu_item_id is required", field="menu_item_id")
    
    if "quantity" not in item_data:
        raise ValidationError("quantity is required", field="quantity")
    
    quantity = item_data.get("quantity", 0)
    if not isinstance(quantity, int) or quantity <= 0:
        raise ValidationError("quantity must be a positive integer", field="quantity")
    
    if quantity > 100:
        raise ValidationError("quantity cannot exceed 100", field="quantity")
    
    # Continue with adding the item...
    return {"message": "Item added successfully"}


"""
Key Takeaways:

1. Always use specific exception classes (ResourceNotFoundError, ValidationError, etc.)
2. Provide clear, actionable error messages
3. Include field names in ValidationError for client-side form handling
4. Check permissions early and raise ForbiddenError when appropriate
5. Validate state transitions and raise ConflictError for invalid states
6. Let exceptions propagate - don't catch and re-raise unnecessarily
7. Use try-except only for database operations that need rollback
8. Include context in error details (resource type, operation, etc.)

These patterns ensure:
- Consistent error responses across all endpoints
- Better debugging with structured error information
- Improved client-side error handling
- Clear API documentation through exception docstrings
"""
