from datetime import datetime
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import logging

from ..models.cash_register import (
    CashRegisterSession as CashRegisterSessionModel,
    CashTransaction as CashTransactionModel,
    CashRegisterReport as CashRegisterReportModel,
    SessionStatus,
    TransactionType
)
from ..schemas.cash_register import (
    CashRegisterSessionCreate,
    CashRegisterSessionUpdate,
    CashTransactionCreate,
    CashDifferenceReport,
    DailySummaryReport,
    PaymentBreakdownReport
)

logger = logging.getLogger(__name__)

# -----------------------------
# Cash Register Session Services
# -----------------------------

def create_session(db: Session, session_data: CashRegisterSessionCreate) -> CashRegisterSessionModel:
    """Create a new cash register session."""
    try:
        db_session = CashRegisterSessionModel(
            opened_by_user_id=session_data.opened_by_user_id,
            cashier_id=session_data.cashier_id,
            initial_balance=session_data.initial_balance,
            opened_at=datetime.utcnow(),
            status=SessionStatus.OPEN
        )
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        logger.info(f"Created cash register session {db_session.id}")
        return db_session
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating session: {e}")
        raise

def get_session(db: Session, session_id: int) -> Optional[CashRegisterSessionModel]:
    """Get a cash register session by ID."""
    return db.query(CashRegisterSessionModel).filter(
        CashRegisterSessionModel.id == session_id
    ).first()

def get_current_session(db: Session, user_id: int) -> Optional[CashRegisterSessionModel]:
    """Get the current open session for a user."""
    return db.query(CashRegisterSessionModel)\
        .filter(
            CashRegisterSessionModel.opened_by_user_id == user_id,
            CashRegisterSessionModel.status == SessionStatus.OPEN
        )\
        .order_by(CashRegisterSessionModel.opened_at.desc())\
        .first()

def get_sessions(db: Session,
                status: Optional[SessionStatus] = None,
                cashier_id: Optional[int] = None,
                skip: int = 0,
                limit: int = 100) -> List[CashRegisterSessionModel]:
    """Get cash register sessions with optional filtering."""
    query = db.query(CashRegisterSessionModel)
    
    if status is not None:
        query = query.filter(CashRegisterSessionModel.status == status)
    if cashier_id is not None:
        query = query.filter(CashRegisterSessionModel.cashier_id == cashier_id)
    
    return query.offset(skip).limit(limit).all()

def close_session(
    db: Session,
    session_id: int,
    session_update: CashRegisterSessionUpdate
) -> CashRegisterSessionModel:
    """Close a cash register session.
    
    Args:
        db: Database session
        session_id: ID of the session to close
        session_update: Update data including final_balance, actual_balance, and notes
        
    Returns:
        The closed session
    """
    try:
        db_session = get_session(db, session_id)
        if not db_session:
            raise ValueError("Session not found")
        if db_session.status != SessionStatus.OPEN:
            raise ValueError("Session is not open")

        transactions = get_transactions_by_session(db, session_id)
        expected_balance = db_session.initial_balance + sum(t.amount for t in transactions)

        db_session.closed_at = datetime.utcnow()
        db_session.final_balance = session_update.final_balance
        db_session.actual_balance = session_update.actual_balance
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

def cut_session(db: Session, session_id: int) -> DailySummaryReport:
    """Perform a partial cut (end-of-shift report) without closing the session."""
    try:
        db_session = get_session(db, session_id)
        if not db_session:
            raise ValueError("Session not found")

        transactions = get_transactions_by_session(db, session_id)

        # Correct sign handling: refunds/cancellations usually reduce cash
        total_sales = sum(t.amount for t in transactions if t.transaction_type == TransactionType.SALE)
        total_refunds = sum(t.amount for t in transactions if t.transaction_type in [TransactionType.REFUND, TransactionType.CANCELLATION])
        total_tips = sum(t.amount for t in transactions if t.transaction_type == TransactionType.TIP)
        net_cash_flow = total_sales - total_refunds + total_tips  # refunds subtracted

        payment_breakdown = PaymentBreakdownReport(
            cash=net_cash_flow,
            card=0,
            digital=0,
            other=0
        )

        report_data = DailySummaryReport(
            session_id=session_id,
            total_sales=total_sales,
            total_refunds=total_refunds,
            total_tips=total_tips,
            total_transactions=len(transactions),
            net_cash_flow=net_cash_flow,
            payment_breakdown=payment_breakdown
        )

        # Create report record
        db_report = CashRegisterReportModel(
            session_id=session_id,
            report_type="daily_summary",
            data=json.dumps(report_data.dict()),
            generated_at=datetime.utcnow()
        )
        db.add(db_report)
        db.commit()
        db.refresh(db_report)

        logger.info(f"Performed cut for session {session_id}")
        return report_data
    except Exception as e:
        db.rollback()
        logger.error(f"Error performing cut for session {session_id}: {e}")
        raise

# -----------------------------
# Transaction Services
# -----------------------------

def create_transaction(db: Session, transaction_data: CashTransactionCreate, created_by_user_id: int) -> CashTransactionModel:
    """Create a new cash transaction."""
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
    """Get all transactions for a session."""
    return db.query(CashTransactionModel).filter(
        CashTransactionModel.session_id == session_id
    ).all()

# -----------------------------
# Report Services
# -----------------------------

def get_reports(
    db: Session,
    session_id: Optional[int] = None,
    report_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[CashRegisterReportModel]:
    """Get cash register reports with optional filtering."""
    query = db.query(CashRegisterReportModel)
    if session_id:
        query = query.filter(CashRegisterReportModel.session_id == session_id)
    if report_type:
        query = query.filter(CashRegisterReportModel.report_type == report_type)
    return query.offset(skip).limit(limit).all()

def generate_cash_difference_report(db: Session, session_id: int) -> CashDifferenceReport:
    """Generate a cash difference report for a session."""
    try:
        db_session = get_session(db, session_id)
        if not db_session:
            raise ValueError("Session not found")

        transactions = get_transactions_by_session(db, session_id)
        expected_balance = db_session.initial_balance + sum(t.amount for t in transactions)
        actual_balance = db_session.actual_balance or 0  # guard against None

        difference = actual_balance - expected_balance

        report_data = CashDifferenceReport(
            session_id=session_id,
            expected_balance=expected_balance,
            actual_balance=actual_balance,
            difference=difference,
            notes=db_session.notes
        )

        logger.info(f"Generated cash difference report for session {session_id}")
        return report_data
    except Exception as e:
        logger.error(f"Error generating difference report for session {session_id}: {e}")
        raise
