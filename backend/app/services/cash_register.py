from datetime import datetime, timezone
from sqlalchemy.orm import Session, joinedload
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
    PaymentBreakdownReport,
    ReportType
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
            opened_at=datetime.now(timezone.utc),
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
    return db.query(CashRegisterSessionModel)\
        .options(joinedload(CashRegisterSessionModel.transactions))\
        .options(joinedload(CashRegisterSessionModel.reports))\
        .filter(CashRegisterSessionModel.id == session_id)\
        .first()

def get_current_session(db: Session, user_id: int) -> Optional[CashRegisterSessionModel]:
    """Get the current open session for a user."""
    return db.query(CashRegisterSessionModel)\
        .options(joinedload(CashRegisterSessionModel.transactions))\
        .options(joinedload(CashRegisterSessionModel.reports))\
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
    return db.query(CashRegisterSessionModel)\
        .options(joinedload(CashRegisterSessionModel.transactions))\
        .options(joinedload(CashRegisterSessionModel.reports))\
        .filter(CashRegisterSessionModel.status == status if status is not None else True)\
        .filter(CashRegisterSessionModel.cashier_id == cashier_id if cashier_id is not None else True)\
        .offset(skip)\
        .limit(limit)\
        .all()

def close_session(
    db: Session,
    session_id: int,
    session_update: CashRegisterSessionUpdate
) -> CashRegisterSessionModel:
    """Close a cash register session.

    Args:
        db: Database session
        session_id: ID of the session to close
        session_update: Update data including final_balance and notes

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

        # The user provides the final balance they counted physically
        # This is the "actual_balance" in the database
        actual_balance = session_update.final_balance

        # Set all the required fields for closing
        db_session.closed_at = datetime.now(timezone.utc)
        db_session.final_balance = actual_balance  # What user counted
        db_session.actual_balance = actual_balance  # Same as final balance
        db_session.expected_balance = expected_balance  # Calculated from transactions
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

def cut_session(db: Session, session_id: int, payment_breakdown: PaymentBreakdownReport) -> DailySummaryReport:
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

        # Use the provided payment breakdown data
        report_data = DailySummaryReport(
            session_id=session_id,
            total_sales=total_sales,
            total_refunds=total_refunds,
            total_tips=total_tips,
            total_transactions=len(transactions),
            net_cash_flow=net_cash_flow,
            payment_breakdown={
                "cash": payment_breakdown.cash_payments,
                "card": payment_breakdown.card_payments,
                "digital": payment_breakdown.digital_payments,
                "other": payment_breakdown.other_payments
            }
        )

        # Create report record
        db_report = CashRegisterReportModel(
            session_id=session_id,
            report_type=ReportType.DAILY_SUMMARY,
            data=json.dumps(report_data.dict()),
            generated_at=datetime.now(timezone.utc)
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
        # Convert string to enum value for proper comparison
        try:
            report_type_enum = ReportType(report_type)
            query = query.filter(CashRegisterReportModel.report_type == report_type_enum)
        except ValueError:
            # If the string doesn't match any enum value, return empty result
            return []
    return query.offset(skip).limit(limit).all()

def create_transaction_from_order(
    db: Session,
    order_id: int,
    created_by_user_id: int,
    transaction_type: TransactionType = TransactionType.SALE,
    session_id: Optional[int] = None
) -> CashTransactionModel:
    """Create a cash register transaction from an order payment."""
    from ..models.order import Order as OrderModel

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

    # Create the transaction
    transaction = CashTransactionModel(
        session_id=session_id,
        transaction_type=transaction_type,
        amount=db_order.total_amount,
        description=f"Payment for order #{order_id}",
        order_id=order_id,
        created_by_user_id=created_by_user_id
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

def get_last_cut(db: Session, session_id: int) -> Optional[DailySummaryReport]:
    """Get the last cut (daily summary report) for a session."""
    try:
        # Find the most recent daily summary report for this session
        last_report = db.query(CashRegisterReportModel)\
            .filter(
                CashRegisterReportModel.session_id == session_id,
                CashRegisterReportModel.report_type == ReportType.DAILY_SUMMARY
            )\
            .order_by(CashRegisterReportModel.generated_at.desc())\
            .first()

        if not last_report:
            return None

        # Parse the JSON data back into a DailySummaryReport object
        report_data = json.loads(last_report.data)
        return DailySummaryReport(**report_data)
    except Exception as e:
        logger.error(f"Error getting last cut for session {session_id}: {e}")
        raise

def generate_cash_difference_report(db: Session, session_id: int) -> CashDifferenceReport:
    """Generate a cash difference report for a session."""
    try:
        db_session = get_session(db, session_id)
        if not db_session:
            raise ValueError("Session not found")

        transactions = get_transactions_by_session(db, session_id)
        expected_balance = db_session.initial_balance + sum(t.amount for t in transactions)

        # Use actual_balance if available, otherwise use final_balance
        actual_balance = db_session.actual_balance or db_session.final_balance or 0
        difference = actual_balance - expected_balance

        return CashDifferenceReport(
            session_id=session_id,
            expected_balance=expected_balance,
            actual_balance=actual_balance,
            difference=difference,
            notes=db_session.notes
        )
    except Exception as e:
        logger.error(f"Error generating cash difference report for session {session_id}: {e}")
        raise
