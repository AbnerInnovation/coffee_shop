"""
Denomination Service - Single Responsibility: Expense and Denomination Management

Handles operations related to:
- Adding expenses to sessions
- Cash denomination counting
- Expense categorization
"""

from sqlalchemy.orm import Session
from typing import Optional
import logging

from ...models.cash_register import (
    CashTransaction as CashTransactionModel,
    SessionStatus,
    TransactionType
)
from .session_service import get_session

logger = logging.getLogger(__name__)


def add_expense_to_session(
    db: Session,
    session_id: int,
    amount: float,
    description: str,
    created_by_user_id: int,
    category: Optional[str] = None
) -> CashTransactionModel:
    """
    Add an expense transaction to a cash register session.
    
    Args:
        db: Database session
        session_id: ID of the cash register session
        amount: Expense amount (positive value)
        description: Description of the expense
        created_by_user_id: ID of the user creating the expense
        category: Optional category for the expense
        
    Returns:
        The created expense transaction
        
    Raises:
        ValueError: If session not found or not open
    """
    try:
        # Verify session exists and is open
        db_session = get_session(db, session_id)
        if not db_session:
            raise ValueError("Session not found")
        if db_session.status != SessionStatus.OPEN:
            raise ValueError("Cannot add expenses to a closed session")
        
        # Create expense description with category if provided
        full_description = f"{description}"
        if category:
            full_description = f"[{category}] {description}"
        
        # Create the expense transaction (negative amount to reduce cash)
        transaction = CashTransactionModel(
            session_id=session_id,
            transaction_type=TransactionType.EXPENSE,
            amount=-abs(amount),  # Ensure negative value for expense
            description=full_description,
            created_by_user_id=created_by_user_id
        )
        
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        
        logger.info(f"Added expense transaction {transaction.id} to session {session_id}")
        return transaction
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding expense to session {session_id}: {e}")
        raise
