"""
Calculation Service - Single Responsibility: Financial Calculations

Handles all financial calculations and aggregations:
- Expected balance calculations
- Session totals (sales, refunds, tips, expenses)
- Payment breakdowns
- Net cash flow calculations
"""

from sqlalchemy.orm import Session
from typing import Dict, Tuple
import logging

from ...models.cash_register import (
    CashTransaction as CashTransactionModel,
    TransactionType
)
from .transaction_service import get_transactions_by_session

logger = logging.getLogger(__name__)


def calculate_expected_balance(
    db: Session, 
    session_id: int, 
    initial_balance: float
) -> float:
    """
    Calculate the expected balance for a session based on transactions.
    
    Args:
        db: Database session
        session_id: ID of the cash register session
        initial_balance: Initial balance when session opened
        
    Returns:
        Expected balance (initial + sum of all transactions)
    """
    transactions = get_transactions_by_session(db, session_id)
    transaction_sum = sum(float(t.amount) for t in transactions)
    return float(initial_balance) + transaction_sum


def calculate_session_totals(
    db: Session, 
    session_id: int
) -> Tuple[float, float, float, float, float]:
    """
    Calculate all financial totals for a session.
    
    Args:
        db: Database session
        session_id: ID of the cash register session
        
    Returns:
        Tuple of (total_sales, total_refunds, total_tips, total_expenses, net_cash_flow)
    """
    transactions = get_transactions_by_session(db, session_id)
    
    # Calculate totals by transaction type
    total_sales = sum(
        t.amount for t in transactions 
        if t.transaction_type == TransactionType.SALE
    )
    
    total_refunds = sum(
        abs(t.amount) for t in transactions 
        if t.transaction_type in [TransactionType.REFUND, TransactionType.CANCELLATION]
    )
    
    total_tips = sum(
        t.amount for t in transactions 
        if t.transaction_type == TransactionType.TIP
    )
    
    total_expenses = sum(
        abs(t.amount) for t in transactions 
        if t.transaction_type == TransactionType.EXPENSE
    )
    
    # Calculate net cash flow
    # Refunds and expenses reduce cash, so they're subtracted
    # Note: total_refunds and total_expenses are already positive (abs values)
    net_cash_flow = total_sales - total_refunds + total_tips - total_expenses
    
    return (
        float(total_sales),
        float(total_refunds),
        float(total_tips),
        float(total_expenses),
        float(net_cash_flow)
    )


def calculate_payment_breakdown(
    db: Session, 
    session_id: int
) -> Dict[str, float]:
    """
    Calculate payment method breakdown for a session.
    
    Args:
        db: Database session
        session_id: ID of the cash register session
        
    Returns:
        Dictionary with payment method totals
    """
    transactions = get_transactions_by_session(db, session_id)
    
    payment_breakdown = {
        "cash": 0.0,
        "card": 0.0,
        "digital": 0.0,
        "other": 0.0
    }
    
    for transaction in transactions:
        if transaction.payment_method and transaction.amount > 0:
            method_key = transaction.payment_method.value.lower()
            if method_key in payment_breakdown:
                payment_breakdown[method_key] += float(transaction.amount)
    
    return payment_breakdown


def calculate_cash_difference(
    expected_balance: float, 
    actual_balance: float
) -> float:
    """
    Calculate the difference between expected and actual balance.
    
    Args:
        expected_balance: Expected balance from transactions
        actual_balance: Actual balance counted physically
        
    Returns:
        Difference (positive = surplus, negative = shortage)
    """
    return actual_balance - expected_balance


def aggregate_session_totals(
    sessions: list
) -> Tuple[float, float, float, float, int, Dict[str, float]]:
    """
    Aggregate totals from multiple sessions (for weekly/monthly reports).
    
    Args:
        sessions: List of session data dictionaries
        
    Returns:
        Tuple of (total_sales, total_refunds, total_tips, total_expenses, 
                  total_transactions, payment_breakdown)
    """
    total_sales = 0.0
    total_refunds = 0.0
    total_tips = 0.0
    total_expenses = 0.0
    total_transactions = 0
    payment_breakdown = {"cash": 0.0, "card": 0.0, "digital": 0.0, "other": 0.0}
    
    for session_data in sessions:
        total_sales += session_data.get('total_sales', 0.0)
        total_refunds += session_data.get('total_refunds', 0.0)
        total_tips += session_data.get('total_tips', 0.0)
        total_expenses += session_data.get('total_expenses', 0.0)
        total_transactions += session_data.get('total_transactions', 0)
        
        # Aggregate payment methods
        session_breakdown = session_data.get('payment_breakdown', {})
        for method, amount in session_breakdown.items():
            if method in payment_breakdown:
                payment_breakdown[method] += amount
    
    return (
        total_sales,
        total_refunds,
        total_tips,
        total_expenses,
        total_transactions,
        payment_breakdown
    )
