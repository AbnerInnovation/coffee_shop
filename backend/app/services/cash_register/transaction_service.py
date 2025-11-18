"""
Transaction Service - Single Responsibility: Cash Transaction Management

Handles all operations related to cash transactions:
- Creating transactions
- Retrieving transactions
- Deleting transactions
- Creating transactions from orders
"""

from datetime import datetime, timezone
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from ...models.cash_register import (
    CashTransaction as CashTransactionModel,
    PaymentMethod,
    TransactionType
)
from ...schemas.cash_register import CashTransactionCreate

logger = logging.getLogger(__name__)


def create_transaction(
    db: Session, 
    transaction_data: CashTransactionCreate, 
    created_by_user_id: int
) -> CashTransactionModel:
    """
    Create a new cash transaction.
    
    Args:
        db: Database session
        transaction_data: Transaction creation data
        created_by_user_id: ID of the user creating the transaction
        
    Returns:
        Created cash transaction
        
    Raises:
        Exception: If transaction creation fails
    """
    try:
        # Only pass valid fields to SQLAlchemy model
        transaction_dict = transaction_data.dict()
        transaction_dict["created_by_user_id"] = created_by_user_id

        db_transaction = CashTransactionModel(**transaction_dict)
        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)
        
        logger.info(f"Created transaction {db_transaction.id} for session {transaction_data.session_id}")
        return db_transaction
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating transaction: {e}")
        raise


def get_transactions_by_session(db: Session, session_id: int) -> List[CashTransactionModel]:
    """
    Get all transactions for a session.
    
    Args:
        db: Database session
        session_id: ID of the session
        
    Returns:
        List of transactions ordered by ID descending
    """
    return db.query(CashTransactionModel).filter(
        CashTransactionModel.session_id == session_id
    ).order_by(CashTransactionModel.id.desc()).all()


def delete_transaction(db: Session, transaction_id: int, user_id: int) -> bool:
    """
    Delete a transaction from a cash register session.
    
    Args:
        db: Database session
        transaction_id: ID of the transaction to delete
        user_id: ID of the user requesting deletion (for authorization)
        
    Returns:
        True if deleted successfully
        
    Raises:
        ValueError: If transaction not found or session is closed
    """
    # Lazy import to avoid circular dependency
    from .session_service import get_session
    
    try:
        transaction = db.query(CashTransactionModel).filter(
            CashTransactionModel.id == transaction_id
        ).first()
        
        if not transaction:
            raise ValueError("Transaction not found")
        
        # Check if the session is still open
        session = get_session(db, transaction.session_id)
        if not session:
            raise ValueError("Session not found")
        if session.status.value != "OPEN":
            raise ValueError("Cannot delete transactions from a closed session")
        
        # Delete the transaction
        db.delete(transaction)
        db.commit()
        
        logger.info(f"Deleted transaction {transaction_id} by user {user_id}")
        return True
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting transaction {transaction_id}: {e}")
        raise


def create_transaction_from_order(
    db: Session,
    order_id: int,
    created_by_user_id: int,
    transaction_type: TransactionType = TransactionType.SALE,
    session_id: Optional[int] = None,
    payment_method: Optional[str] = None
) -> CashTransactionModel:
    """
    Create a cash register transaction from an order payment.
    
    Args:
        db: Database session
        order_id: ID of the order
        created_by_user_id: ID of the user creating the transaction
        transaction_type: Type of transaction (default: SALE)
        session_id: Optional session ID (will find current session if not provided)
        payment_method: Optional payment method
        
    Returns:
        Created cash transaction
        
    Raises:
        ValueError: If order not found, already paid, or no open session
    """
    # Lazy import to avoid circular dependency
    from .session_service import get_current_session
    from ...models.order import Order as OrderModel

    # Get the order
    db_order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not db_order:
        raise ValueError("Order not found")

    if db_order.is_paid:
        raise ValueError("Order is already paid")

    # Get or create cash register session for the user
    if not session_id:
        # Find current open session for the user
        current_session = get_current_session(db, created_by_user_id)
        if not current_session:
            raise ValueError("No open cash register session found. Please open a session first.")
        session_id = current_session.id

    # Check if transaction already exists for this order
    existing_transaction = db.query(CashTransactionModel).filter(
        CashTransactionModel.order_id == order_id,
        CashTransactionModel.session_id == session_id
    ).first()

    if existing_transaction:
        raise ValueError("Transaction already exists for this order in the current session")

    # Map payment method from order to PaymentMethod enum
    payment_method_enum = None
    if payment_method:
        try:
            payment_method_enum = PaymentMethod[payment_method.upper()]
        except (KeyError, AttributeError):
            payment_method_enum = PaymentMethod.CASH  # Default to cash
    elif db_order.payment_method:
        try:
            payment_method_enum = PaymentMethod[db_order.payment_method.upper()]
        except (KeyError, AttributeError):
            payment_method_enum = PaymentMethod.CASH

    # Create the transaction
    transaction = CashTransactionModel(
        session_id=session_id,
        transaction_type=transaction_type,
        amount=db_order.total_amount,
        description=f"Pago de orden #{db_order.order_number}",
        order_id=order_id,
        created_by_user_id=created_by_user_id,
        payment_method=payment_method_enum
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    
    logger.info(f"Created transaction from order #{db_order.order_number}")
    return transaction
