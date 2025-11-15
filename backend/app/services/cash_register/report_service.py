"""
Report Service - Single Responsibility: Report Generation

Handles all report generation operations:
- Daily summary reports
- Weekly summary reports
- Cash difference reports
- Session cuts
- Report retrieval
"""

from datetime import datetime, timezone
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import logging

from ...models.cash_register import (
    CashRegisterSession as CashRegisterSessionModel,
    CashRegisterReport as CashRegisterReportModel,
    SessionStatus,
    ReportType
)
from ...schemas.cash_register import (
    CashDifferenceReport,
    DailySummaryReport,
    PaymentBreakdownReport,
    WeeklySummaryReport
)
from .session_service import get_session
from .transaction_service import get_transactions_by_session
from .calculation_service import (
    calculate_session_totals,
    calculate_payment_breakdown,
    calculate_cash_difference
)

logger = logging.getLogger(__name__)


def get_reports(
    db: Session,
    session_id: Optional[int] = None,
    report_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[CashRegisterReportModel]:
    """
    Get cash register reports with optional filtering.
    
    Args:
        db: Database session
        session_id: Filter by session ID
        report_type: Filter by report type
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of cash register reports
    """
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


def cut_session(
    db: Session, 
    session_id: int, 
    payment_breakdown: PaymentBreakdownReport
) -> DailySummaryReport:
    """
    Perform a partial cut (end-of-shift report) without closing the session.
    
    Args:
        db: Database session
        session_id: ID of the cash register session
        payment_breakdown: Payment breakdown data from user
        
    Returns:
        Daily summary report
        
    Raises:
        ValueError: If session not found
    """
    try:
        db_session = get_session(db, session_id)
        if not db_session:
            raise ValueError("Session not found")

        # Calculate session totals
        total_sales, total_refunds, total_tips, total_expenses, net_cash_flow = \
            calculate_session_totals(db, session_id)
        
        transactions = get_transactions_by_session(db, session_id)

        # Use the provided payment breakdown data
        report_data = DailySummaryReport(
            session_id=session_id,
            session_number=db_session.session_number,
            total_sales=total_sales,
            total_refunds=total_refunds,
            total_tips=total_tips,
            total_expenses=total_expenses,
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


def get_last_cut(db: Session, session_id: int) -> Optional[DailySummaryReport]:
    """
    Get the last cut (daily summary report) for a session.
    
    Args:
        db: Database session
        session_id: ID of the cash register session
        
    Returns:
        Last daily summary report or None if no cuts exist
    """
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


def generate_cash_difference_report(
    db: Session, 
    session_id: int
) -> CashDifferenceReport:
    """
    Generate a cash difference report for a session.
    
    Args:
        db: Database session
        session_id: ID of the cash register session
        
    Returns:
        Cash difference report
        
    Raises:
        ValueError: If session not found
    """
    try:
        db_session = get_session(db, session_id)
        if not db_session:
            raise ValueError("Session not found")

        transactions = get_transactions_by_session(db, session_id)
        expected_balance = db_session.initial_balance + sum(t.amount for t in transactions)

        # Use actual_balance if available, otherwise use final_balance
        actual_balance = db_session.actual_balance or db_session.final_balance or 0
        difference = calculate_cash_difference(expected_balance, actual_balance)

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


def get_daily_summary_reports(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    cashier_id: Optional[int] = None,
    restaurant_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
) -> List[DailySummaryReport]:
    """
    Get daily summary reports within a date range.
    Generates reports on-the-fly from closed sessions.
    
    Args:
        db: Database session
        start_date: Optional start date filter
        end_date: Optional end date filter
        cashier_id: Optional cashier ID filter (for staff users)
        restaurant_id: Optional restaurant ID filter (for multi-restaurant isolation)
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of daily summary reports
    """
    try:
        # Query closed sessions within date range
        query = db.query(CashRegisterSessionModel).filter(
            CashRegisterSessionModel.status == SessionStatus.CLOSED
        )
        
        if start_date:
            query = query.filter(CashRegisterSessionModel.closed_at >= start_date)
        if end_date:
            query = query.filter(CashRegisterSessionModel.closed_at <= end_date)
        if cashier_id:
            query = query.filter(CashRegisterSessionModel.cashier_id == cashier_id)
        if restaurant_id:
            query = query.filter(CashRegisterSessionModel.restaurant_id == restaurant_id)
        
        sessions = query.order_by(CashRegisterSessionModel.closed_at.desc())\
            .offset(skip).limit(limit).all()
        
        # Generate report for each session
        result = []
        for session in sessions:
            total_sales, total_refunds, total_tips, total_expenses, net_cash_flow = \
                calculate_session_totals(db, session.id)
            
            payment_breakdown = calculate_payment_breakdown(db, session.id)
            transactions = get_transactions_by_session(db, session.id)
            
            result.append(DailySummaryReport(
                session_id=session.id,
                session_number=session.session_number,
                opened_at=session.opened_at,
                closed_at=session.closed_at,
                total_sales=total_sales,
                total_refunds=total_refunds,
                total_tips=total_tips,
                total_expenses=total_expenses,
                total_transactions=len(transactions),
                net_cash_flow=net_cash_flow,
                payment_breakdown=payment_breakdown
            ))
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting daily summary reports: {e}")
        raise


def get_weekly_summary(
    db: Session,
    start_date: datetime,
    end_date: datetime
) -> WeeklySummaryReport:
    """
    Generate a weekly summary report aggregating multiple sessions.
    
    Args:
        db: Database session
        start_date: Start of the week
        end_date: End of the week
        
    Returns:
        Weekly summary report
    """
    try:
        # Get all sessions within the date range
        sessions = db.query(CashRegisterSessionModel).filter(
            CashRegisterSessionModel.opened_at >= start_date,
            CashRegisterSessionModel.opened_at <= end_date
        ).all()
        
        total_sales = 0.0
        total_refunds = 0.0
        total_tips = 0.0
        total_expenses = 0.0
        total_transactions = 0
        payment_breakdown = {"cash": 0.0, "card": 0.0, "digital": 0.0, "other": 0.0}
        
        # Aggregate data from all sessions
        for session in sessions:
            session_sales, session_refunds, session_tips, session_expenses, _ = \
                calculate_session_totals(db, session.id)
            
            total_sales += session_sales
            total_refunds += session_refunds
            total_tips += session_tips
            total_expenses += session_expenses
            
            transactions = get_transactions_by_session(db, session.id)
            total_transactions += len(transactions)
            
            # Aggregate payment methods
            session_breakdown = calculate_payment_breakdown(db, session.id)
            for method, amount in session_breakdown.items():
                if method in payment_breakdown:
                    payment_breakdown[method] += amount
        
        net_cash_flow = total_sales - total_refunds + total_tips - total_expenses
        average_session_value = net_cash_flow / len(sessions) if sessions else 0.0
        
        return WeeklySummaryReport(
            start_date=start_date,
            end_date=end_date,
            total_sessions=len(sessions),
            total_sales=total_sales,
            total_refunds=total_refunds,
            total_tips=total_tips,
            total_expenses=total_expenses,
            total_transactions=total_transactions,
            net_cash_flow=net_cash_flow,
            average_session_value=average_session_value,
            payment_breakdown=payment_breakdown
        )
        
    except Exception as e:
        logger.error(f"Error generating weekly summary: {e}")
        raise
