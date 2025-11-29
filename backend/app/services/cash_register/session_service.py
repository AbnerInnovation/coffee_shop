"""
Session Service - Single Responsibility: Cash Register Session Management

Handles all operations related to cash register sessions:
- Creating new sessions
- Retrieving sessions (current, by ID, filtered list)
- Closing sessions
- Session validation
"""

from datetime import datetime, timezone
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import logging

from ...core.exceptions import ConflictError, ValidationError
from ...models.cash_register import (
    CashRegisterSession as CashRegisterSessionModel,
    SessionStatus
)
from ...schemas.cash_register import (
    CashRegisterSessionCreate,
    CashRegisterSessionUpdate,
    DenominationCount
)
from .calculation_service import calculate_expected_balance

logger = logging.getLogger(__name__)


def create_session(
    db: Session, 
    session_data: CashRegisterSessionCreate, 
    restaurant_id: int
) -> CashRegisterSessionModel:
    """
    Create a new cash register session with automatic session number calculation.
    
    Args:
        db: Database session
        session_data: Session creation data
        restaurant_id: ID of the restaurant
        
    Returns:
        Created cash register session
        
    Raises:
        ConflictError: If there's already an open session for this restaurant
        Exception: If session creation fails
    """
    try:
        # Check if there's already an open session for this restaurant
        existing_open_session = db.query(CashRegisterSessionModel)\
            .filter(
                CashRegisterSessionModel.restaurant_id == restaurant_id,
                CashRegisterSessionModel.status == SessionStatus.OPEN
            )\
            .first()
        
        if existing_open_session:
            raise ConflictError(
                f"Cannot open a new session. There is already an open session "
                f"(Session #{existing_open_session.session_number}) for this restaurant. "
                f"Please close the existing session before opening a new one.",
                resource="CashRegisterSession"
            )
        
        # Calculate the next session number for this restaurant
        last_session = db.query(CashRegisterSessionModel)\
            .filter(CashRegisterSessionModel.restaurant_id == restaurant_id)\
            .order_by(CashRegisterSessionModel.session_number.desc())\
            .first()
        
        next_session_number = (last_session.session_number + 1) if last_session else 1
        
        db_session = CashRegisterSessionModel(
            restaurant_id=restaurant_id,
            session_number=next_session_number,
            opened_by_user_id=session_data.opened_by_user_id,
            cashier_id=session_data.cashier_id,
            initial_balance=session_data.initial_balance,
            opened_at=datetime.now(timezone.utc),
            status=SessionStatus.OPEN
        )
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        
        logger.info(f"Created cash register session #{next_session_number} for restaurant {restaurant_id}")
        return db_session
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating session: {e}")
        raise


def get_session(db: Session, session_id: int) -> Optional[CashRegisterSessionModel]:
    """
    Get a cash register session by ID with all related data.
    
    Args:
        db: Database session
        session_id: ID of the session to retrieve
        
    Returns:
        Cash register session or None if not found
    """
    return db.query(CashRegisterSessionModel)\
        .options(joinedload(CashRegisterSessionModel.transactions))\
        .options(joinedload(CashRegisterSessionModel.reports))\
        .options(joinedload(CashRegisterSessionModel.opened_by_user))\
        .filter(CashRegisterSessionModel.id == session_id)\
        .first()


def get_current_session(db: Session, user_id: int) -> Optional[CashRegisterSessionModel]:
    """
    Get the current open session for a user.
    
    Args:
        db: Database session
        user_id: ID of the user
        
    Returns:
        Current open session or None if no open session exists
    """
    return db.query(CashRegisterSessionModel)\
        .options(joinedload(CashRegisterSessionModel.transactions))\
        .options(joinedload(CashRegisterSessionModel.reports))\
        .options(joinedload(CashRegisterSessionModel.opened_by_user))\
        .filter(
            CashRegisterSessionModel.opened_by_user_id == user_id,
            CashRegisterSessionModel.status == SessionStatus.OPEN
        )\
        .order_by(CashRegisterSessionModel.opened_at.desc())\
        .first()


def get_sessions(
    db: Session,
    restaurant_id: Optional[int] = None,
    status: Optional[SessionStatus] = None,
    cashier_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
) -> List[CashRegisterSessionModel]:
    """
    Get cash register sessions with optional filtering.
    
    Args:
        db: Database session
        restaurant_id: Filter by restaurant ID
        status: Filter by session status
        cashier_id: Filter by cashier ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of cash register sessions
    """
    query = db.query(CashRegisterSessionModel)\
        .options(joinedload(CashRegisterSessionModel.transactions))\
        .options(joinedload(CashRegisterSessionModel.reports))\
        .options(joinedload(CashRegisterSessionModel.opened_by_user))
    
    if restaurant_id is not None:
        query = query.filter(CashRegisterSessionModel.restaurant_id == restaurant_id)
    if status is not None:
        query = query.filter(CashRegisterSessionModel.status == status)
    if cashier_id is not None:
        query = query.filter(CashRegisterSessionModel.cashier_id == cashier_id)
    
    return query.order_by(CashRegisterSessionModel.session_number.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()


def close_session(
    db: Session,
    session_id: int,
    session_update: CashRegisterSessionUpdate
) -> CashRegisterSessionModel:
    """
    Close a cash register session.
    
    Args:
        db: Database session
        session_id: ID of the session to close
        session_update: Update data including final_balance and notes
        
    Returns:
        The closed session
        
    Raises:
        ValidationError: If session not found or not open
    """
    try:
        db_session = get_session(db, session_id)
        if not db_session:
            raise ValidationError("Session not found")
        if db_session.status != SessionStatus.OPEN:
            raise ValidationError("Session is not open")

        # Calculate expected balance from transactions
        expected_balance = calculate_expected_balance(db, session_id, db_session.initial_balance)

        # The user provides the final balance they counted physically
        actual_balance = session_update.final_balance

        # Set all the required fields for closing
        db_session.closed_at = datetime.now(timezone.utc)
        db_session.final_balance = actual_balance
        db_session.actual_balance = actual_balance
        db_session.expected_balance = expected_balance
        db_session.status = SessionStatus.CLOSED
        db_session.notes = session_update.notes

        db.commit()
        db.refresh(db_session)
        
        logger.info(f"Closed cash register session {session_id}")
        return db_session
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error closing session {session_id}: {e}")
        raise


def close_session_with_denominations(
    db: Session,
    session_id: int,
    session_update: CashRegisterSessionUpdate,
    denominations: Optional[DenominationCount] = None
) -> CashRegisterSessionModel:
    """
    Close a cash register session with optional denomination counting.
    
    Args:
        db: Database session
        session_id: ID of the session to close
        session_update: Update data including final_balance and notes
        denominations: Optional denomination breakdown
        
    Returns:
        The closed session
        
    Raises:
        ValidationError: If session not found or not open
    """
    try:
        db_session = get_session(db, session_id)
        if not db_session:
            raise ValidationError("Session not found")
        if db_session.status != SessionStatus.OPEN:
            raise ValidationError("Session is not open")

        # Calculate expected balance from transactions
        expected_balance = calculate_expected_balance(db, session_id, db_session.initial_balance)

        # If denominations provided, calculate actual balance from them
        if denominations:
            actual_balance = denominations.calculate_total()
            # Store denominations in notes if needed
            denomination_note = f"\nDenominations: {denominations.dict()}"
            session_update.notes = (session_update.notes or "") + denomination_note
        else:
            actual_balance = session_update.final_balance

        # Set all the required fields for closing
        db_session.closed_at = datetime.now(timezone.utc)
        db_session.final_balance = actual_balance
        db_session.actual_balance = actual_balance
        db_session.expected_balance = expected_balance
        db_session.status = SessionStatus.CLOSED
        db_session.notes = session_update.notes

        db.commit()
        db.refresh(db_session)
        
        logger.info(f"Closed cash register session {session_id} with denominations")
        return db_session
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error closing session {session_id}: {e}")
        raise
