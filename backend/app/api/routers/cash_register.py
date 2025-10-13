from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from enum import Enum
from datetime import datetime, timedelta

from ...db.base import get_db
from ...models.cash_register import (
    CashRegisterSession as CashRegisterSessionModel,
    CashTransaction as CashTransactionModel,
    CashRegisterReport as CashRegisterReportModel,
    SessionStatus,
    TransactionType
)
from ...schemas.cash_register import (
    CashRegisterSession,
    CashRegisterSessionCreate,
    CashRegisterSessionUpdate,
    CashTransaction,
    CashTransactionCreate,
    CashTransactionUpdate,
    CashRegisterReport,
    CashRegisterReportCreate,
    CashDifferenceReport,
    DailySummaryReport,
    PaymentBreakdownReport,
    ExpenseCreate,
    WeeklySummaryReport,
    DenominationCount,
    SessionCloseWithDenominations
)
from ...services.user import get_current_active_user
from ...services import cash_register as cash_register_service
from ...models.user import User

router = APIRouter(
    prefix="/cash-register",
    tags=["cash-register"],
    responses={404: {"description": "Not found"}},
)

# -----------------------------
# Sessions
# -----------------------------

@router.post("/sessions", response_model=CashRegisterSession, status_code=status.HTTP_201_CREATED)
def create_session(
    session: CashRegisterSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> CashRegisterSession:
    try:
        return cash_register_service.create_session(db, session)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating session: {str(e)}")

@router.get("/sessions/current", response_model=Optional[CashRegisterSession])
def get_current_session(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Optional[CashRegisterSession]:
    """Get the current open session for the authenticated user."""
    try:
        session = cash_register_service.get_current_session(db, current_user.id)
        if not session:
            return None
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving current session: {str(e)}")

@router.get("/sessions/{session_id}", response_model=CashRegisterSession)
def get_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> CashRegisterSession:
    try:
        db_session = cash_register_service.get_session(db, session_id)
        if not db_session:
            raise HTTPException(status_code=404, detail="Session not found")
        return db_session
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving session: {str(e)}")

@router.get("/sessions", response_model=List[CashRegisterSession])
def get_sessions(
    status: Optional[SessionStatus] = None,
    cashier_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[CashRegisterSession]:
    try:
        return cash_register_service.get_sessions(
            db, status=status, cashier_id=cashier_id, skip=skip, limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving sessions: {str(e)}")

@router.patch("/sessions/{session_id}/close", response_model=CashRegisterSession)
def close_session(
    session_id: int,
    session_update: CashRegisterSessionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> CashRegisterSession:
    try:
        return cash_register_service.close_session(db, session_id, session_update)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error closing session: {str(e)}")

@router.post("/sessions/{session_id}/cut", response_model=DailySummaryReport)
def cut_session(
    session_id: int,
    payment_breakdown: PaymentBreakdownReport,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> DailySummaryReport:
    try:
        return cash_register_service.cut_session(db, session_id, payment_breakdown)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error performing cut: {str(e)}")

# -----------------------------
# Transactions
# -----------------------------

@router.get("/transactions", response_model=List[CashTransaction])
def get_transactions(
    session_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[CashTransaction]:
    """Get transactions with optional session filtering."""
    try:
        query = db.query(CashTransactionModel)

        if session_id is not None:
            query = query.filter(CashTransactionModel.session_id == session_id)

        transactions = query.offset(skip).limit(limit).all()
        return transactions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving transactions: {str(e)}")

# -----------------------------
# Reports
# -----------------------------

@router.get("/reports", response_model=List[CashRegisterReport])
def get_reports(
    session_id: Optional[int] = None,
    report_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[CashRegisterReport]:
    try:
        return cash_register_service.get_reports(
            db, session_id=session_id, report_type=report_type, skip=skip, limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving reports: {str(e)}")

@router.get("/reports/session/{session_id}", response_model=List[CashRegisterReport])
def get_session_reports(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[CashRegisterReport]:
    """Get all reports for a specific session."""
    try:
        return cash_register_service.get_reports(db, session_id=session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving session reports: {str(e)}")

@router.get("/sessions/{session_id}/last-cut", response_model=Optional[DailySummaryReport])
def get_last_cut(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Optional[DailySummaryReport]:
    """Get the last cut (most recent daily summary report) for a session."""
    try:
        return cash_register_service.get_last_cut(db, session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving last cut: {str(e)}")

# -----------------------------
# Expenses
# -----------------------------

@router.post("/sessions/{session_id}/expenses", response_model=CashTransaction, status_code=status.HTTP_201_CREATED)
def add_expense(
    session_id: int,
    expense: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> CashTransaction:
    """Add an expense to a cash register session."""
    try:
        transaction = cash_register_service.add_expense_to_session(
            db=db,
            session_id=session_id,
            amount=expense.amount,
            description=expense.description,
            created_by_user_id=current_user.id,
            category=expense.category
        )
        return transaction
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding expense: {str(e)}")

@router.delete("/transactions/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a transaction from an open cash register session."""
    try:
        cash_register_service.delete_transaction(db, transaction_id, current_user.id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting transaction: {str(e)}")

# -----------------------------
# Advanced Reports
# -----------------------------

@router.get("/reports/daily-summaries", response_model=List[DailySummaryReport])
def get_daily_summaries(
    start_date: Optional[str] = Query(None, description="Start date for filtering reports (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date for filtering reports (YYYY-MM-DD)"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[DailySummaryReport]:
    """Get daily summary reports within a date range."""
    try:
        # Convert date strings to datetime objects
        start_datetime = None
        end_datetime = None
        
        if start_date:
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d").replace(hour=0, minute=0, second=0, microsecond=0)
        if end_date:
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59, microsecond=999999)
        
        return cash_register_service.get_daily_summary_reports(
            db, start_date=start_datetime, end_date=end_datetime, skip=skip, limit=limit
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format. Use YYYY-MM-DD: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving daily summaries: {str(e)}")

@router.get("/reports/weekly-summary", response_model=WeeklySummaryReport)
def get_weekly_summary(
    start_date: Optional[str] = Query(None, description="Start of the week (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End of the week (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> WeeklySummaryReport:
    """Generate a weekly summary report."""
    try:
        # Convert date strings to datetime objects
        if start_date:
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d").replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            start_datetime = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=7)
        
        if end_date:
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59, microsecond=999999)
        else:
            end_datetime = datetime.now()
        
        return cash_register_service.get_weekly_summary(db, start_datetime, end_datetime)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format. Use YYYY-MM-DD: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating weekly summary: {str(e)}")

@router.patch("/sessions/{session_id}/close-with-denominations", response_model=CashRegisterSession)
def close_session_with_denominations(
    session_id: int,
    close_data: SessionCloseWithDenominations,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> CashRegisterSession:
    """Close a session with denomination counting."""
    try:
        return cash_register_service.close_session_with_denominations(
            db, session_id, close_data, close_data.denominations
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error closing session: {str(e)}")
