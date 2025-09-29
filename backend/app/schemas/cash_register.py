from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum

class SessionStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"

class TransactionType(str, Enum):
    SALE = "sale"
    REFUND = "refund"
    CANCELLATION = "cancellation"
    TIP = "tip"
    MANUAL_ADD = "manual_add"
    MANUAL_WITHDRAW = "manual_withdraw"

class ReportType(str, Enum):
    DAILY_SUMMARY = "daily_summary"
    CASH_DIFFERENCE = "cash_difference"
    PAYMENT_BREAKDOWN = "payment_breakdown"

class CashRegisterSessionBase(BaseModel):
    opened_by_user_id: int
    cashier_id: Optional[int] = None
    initial_balance: float = Field(..., ge=0)
    notes: Optional[str] = None

class CashRegisterSessionCreate(CashRegisterSessionBase):
    pass

class CashRegisterSessionUpdate(BaseModel):
    closed_at: Optional[datetime] = None
    final_balance: Optional[float] = Field(None, ge=0)
    actual_balance: Optional[float] = Field(None, ge=0)
    status: Optional[SessionStatus] = None
    notes: Optional[str] = None

class CashRegisterSessionInDBBase(CashRegisterSessionBase):
    id: int
    opened_at: datetime
    closed_at: Optional[datetime] = None
    expected_balance: float
    status: SessionStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class CashTransactionBase(BaseModel):
    transaction_type: TransactionType
    amount: float = Field(..., description="Positive for inflows, negative for outflows")
    description: Optional[str] = None
    order_id: Optional[int] = None
    created_by_user_id: int

class CashTransactionCreate(CashTransactionBase):
    session_id: int

class CashTransactionUpdate(BaseModel):
    amount: Optional[float] = None
    description: Optional[str] = None

class CashTransactionInDBBase(CashTransactionBase):
    id: int
    session_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class CashRegisterReportBase(BaseModel):
    report_type: ReportType
    data: Dict[str, Any]  # JSON data for the report

class CashRegisterReportCreate(CashRegisterReportBase):
    session_id: int

class CashRegisterReportInDBBase(CashRegisterReportBase):
    id: int
    session_id: int
    generated_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Response models
class CashRegisterSession(CashRegisterSessionInDBBase):
    transactions: List[CashTransactionInDBBase] = []
    reports: List[CashRegisterReportInDBBase] = []

class CashTransaction(CashTransactionInDBBase):
    pass

class CashRegisterReport(CashRegisterReportInDBBase):
    pass

# Additional models for reports
class CashDifferenceReport(BaseModel):
    session_id: int
    expected_balance: float
    actual_balance: float
    difference: float
    notes: Optional[str] = None

class DailySummaryReport(BaseModel):
    session_id: int
    total_sales: float
    total_refunds: float
    total_tips: float
    total_transactions: int
    net_cash_flow: float
    payment_breakdown: Dict[str, float]

class PaymentBreakdownReport(BaseModel):
    session_id: int
    cash_payments: float
    card_payments: float
    digital_payments: float
    other_payments: float
