"""
Payment Service

Handles all payment-related operations for orders, including:
- Processing order payments
- Creating cash register transactions
- Validating payment methods
- Managing order status transitions
"""

from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timezone

from ...models.order import Order as OrderModel, OrderStatus
from ...schemas.order import PaymentMethod
from ...core.exceptions import ValidationError, ResourceNotFoundError


def validate_payment_method(payment_method: str) -> PaymentMethod:
    """
    Validate and convert payment method string to enum.
    
    Args:
        payment_method: Payment method string
        
    Returns:
        PaymentMethod enum
        
    Raises:
        ValidationError: If payment method is invalid
    """
    try:
        return PaymentMethod(payment_method)
    except ValueError:
        valid_methods = [method.value for method in PaymentMethod]
        raise ValidationError(
            f"Invalid payment method '{payment_method}'. "
            f"Valid methods are: {', '.join(valid_methods)}",
            field="payment_method"
        )


def can_cancel_order(order: OrderModel, user_role: str) -> tuple[bool, Optional[str]]:
    """
    Check if an order can be cancelled by the given user.
    
    Args:
        order: Order to check
        user_role: Role of the user attempting to cancel
        
    Returns:
        Tuple of (can_cancel, error_message)
    """
    # Only admin and sysadmin can cancel orders
    if user_role not in ['admin', 'sysadmin']:
        return False, "Solo los administradores pueden cancelar pedidos"
    
    # Cannot cancel paid orders
    if order.is_paid:
        return False, "No se puede cancelar un pedido que ya está pagado"
    
    return True, None


def process_order_payment(
    db: Session,
    order_id: int,
    payment_method: str,
    user_id: int,
    restaurant_id: int,
    status: Optional[str] = None
) -> OrderModel:
    """
    Process payment for an order.
    
    This function handles the complete payment workflow:
    1. Validates the order exists and isn't already paid
    2. Validates the payment method
    3. Marks the order as paid
    4. Updates order status to COMPLETED (or provided status)
    5. Creates a cash register transaction
    6. Releases the table if it's a dine-in order
    
    Args:
        db: Database session
        order_id: ID of the order to pay
        payment_method: Payment method (cash, card, transfer, etc.)
        user_id: ID of the user processing the payment
        restaurant_id: ID of the restaurant
        status: Optional status to set (defaults to COMPLETED)
        
    Returns:
        Updated order object
        
    Raises:
        ResourceNotFoundError: If order doesn't exist
        ValidationError: If order is already paid or payment method is invalid
    """
    # Get the order
    order = db.query(OrderModel).filter(
        OrderModel.id == order_id,
        OrderModel.restaurant_id == restaurant_id,
        OrderModel.deleted_at.is_(None)
    ).first()
    
    if not order:
        raise ResourceNotFoundError("Order", order_id)
    
    # Check if already paid
    if order.is_paid:
        raise ValidationError(
            f"Order {order_id} is already paid",
            field="is_paid"
        )
    
    # Validate payment method
    payment_method_enum = validate_payment_method(payment_method)
    
    # Mark order as paid
    order.is_paid = True
    order.payment_method = payment_method_enum
    order.paid_at = datetime.now(timezone.utc)
    
    # Update status
    if status:
        try:
            order.status = OrderStatus(status)
        except ValueError:
            raise ValidationError(f"Invalid status: {status}", field="status")
    else:
        order.status = OrderStatus.COMPLETED
    
    order.updated_at = datetime.now(timezone.utc)
    
    # Create cash register transaction
    try:
        from ..cash_register import create_transaction_from_order
        create_transaction_from_order(
            db=db,
            order_id=order_id,
            created_by_user_id=user_id
        )
    except ValueError as e:
        raise ValidationError(str(e))
    
    # Release table if dine-in order
    if order.table_id:
        from .table_manager import mark_table_available_if_no_orders
        mark_table_available_if_no_orders(db, order.table_id, order_id)
    
    # Commit changes
    db.add(order)
    db.commit()
    db.refresh(order)
    
    return order


def mark_order_as_paid_simple(
    db: Session,
    order: OrderModel,
    payment_method: PaymentMethod
) -> OrderModel:
    """
    Simple version: just mark order as paid without side effects.
    
    Use this when you want to handle table management and transactions separately.
    
    Args:
        db: Database session
        order: Order to mark as paid
        payment_method: Payment method enum
        
    Returns:
        Updated order
    """
    order.is_paid = True
    order.payment_method = payment_method
    order.paid_at = datetime.now(timezone.utc)
    order.status = OrderStatus.COMPLETED
    order.updated_at = datetime.now(timezone.utc)
    
    db.add(order)
    db.flush()  # Don't commit, let caller handle transaction
    
    return order


def refund_order_payment(
    db: Session,
    order_id: int,
    user_id: int,
    restaurant_id: int,
    reason: Optional[str] = None
) -> OrderModel:
    """
    Refund a paid order.
    
    Args:
        db: Database session
        order_id: ID of the order to refund
        user_id: ID of the user processing the refund
        restaurant_id: ID of the restaurant
        reason: Optional reason for refund
        
    Returns:
        Updated order
        
    Raises:
        ResourceNotFoundError: If order doesn't exist
        ValidationError: If order is not paid
    """
    # Get the order
    order = db.query(OrderModel).filter(
        OrderModel.id == order_id,
        OrderModel.restaurant_id == restaurant_id,
        OrderModel.deleted_at.is_(None)
    ).first()
    
    if not order:
        raise ResourceNotFoundError("Order", order_id)
    
    # Check if paid
    if not order.is_paid:
        raise ValidationError(
            f"Order {order_id} is not paid, cannot refund",
            field="is_paid"
        )
    
    # Mark as refunded
    order.is_paid = False
    order.status = OrderStatus.CANCELLED
    order.updated_at = datetime.now(timezone.utc)
    
    # TODO: Create refund transaction in cash register
    # This would require a new transaction type in cash_register service
    
    db.add(order)
    db.commit()
    db.refresh(order)
    
    return order
