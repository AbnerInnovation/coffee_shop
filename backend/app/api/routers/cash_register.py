from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from enum import Enum

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
    PaymentBreakdownReport
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

@router.get("/sessions/{session_id}/difference-report", response_model=CashDifferenceReport)
def get_cash_difference_report(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> CashDifferenceReport:
    try:
        return cash_register_service.generate_cash_difference_report(db, session_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating difference report: {str(e)}")
