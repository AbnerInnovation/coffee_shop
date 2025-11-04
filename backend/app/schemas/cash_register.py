from datetime import datetime
from typing import Dict, Any, List, Optional, TYPE_CHECKING
from pydantic import Field, validator
from .base import PhoenixBaseModel as BaseModel
from enum import Enum
import json
from ..core.validators import sanitize_text

if TYPE_CHECKING:
    from .user import User

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
    EXPENSE = "expense"

class PaymentMethod(str, Enum):
    CASH = "CASH"
    CARD = "CARD"
    DIGITAL = "DIGITAL"
    OTHER = "OTHER"

class ReportType(str, Enum):
    DAILY_SUMMARY = "daily_summary"
    CASH_DIFFERENCE = "cash_difference"
    PAYMENT_BREAKDOWN = "payment_breakdown"

class CashRegisterSessionBase(BaseModel):
    opened_by_user_id: int = Field(..., ge=1, description="User ID must be positive")
    cashier_id: Optional[int] = Field(None, ge=1, description="Cashier ID must be positive")
    initial_balance: float = Field(..., ge=0, le=999999999.99, description="Initial balance must be non-negative and reasonable")
    notes: Optional[str] = Field(None, max_length=1000)
    
    @validator('notes')
    def sanitize_notes(cls, v):
        """Remove potentially dangerous characters from notes."""
        return sanitize_text(v)

class CashRegisterSessionCreate(CashRegisterSessionBase):
    pass

class CashRegisterSessionUpdate(BaseModel):
    closed_at: Optional[datetime] = None
    final_balance: Optional[float] = Field(None, ge=0, le=999999999.99)
    actual_balance: Optional[float] = Field(None, ge=0, le=999999999.99)
    status: Optional[SessionStatus] = None
    notes: Optional[str] = Field(None, max_length=1000)
    
    @validator('notes')
    def sanitize_notes(cls, v):
        """Remove potentially dangerous characters from notes."""
        return sanitize_text(v)

class CashRegisterSessionInDBBase(CashRegisterSessionBase):
    id: int
    restaurant_id: int
    session_number: int
    opened_at: datetime
    closed_at: Optional[datetime] = None
    final_balance: Optional[float] = None
    actual_balance: Optional[float] = None
    expected_balance: float
    status: SessionStatus
    created_at: datetime
    updated_at: datetime
    cashier_id: Optional[int] = None

    class Config:
        orm_mode = True

class CashTransactionBase(BaseModel):
    transaction_type: TransactionType
    amount: float = Field(..., ge=-999999999.99, le=999999999.99, description="Positive for inflows, negative for outflows")
    description: Optional[str] = Field(None, max_length=500)
    order_id: Optional[int] = Field(None, ge=1)
    created_by_user_id: int = Field(..., ge=1)
    payment_method: Optional[PaymentMethod] = None
    category: Optional[str] = Field(None, max_length=100)
    
    @validator('description')
    def sanitize_description(cls, v):
        """Remove potentially dangerous characters from description."""
        return sanitize_text(v)
    
    @validator('category')
    def sanitize_category(cls, v):
        """Remove potentially dangerous characters from category."""
        return sanitize_text(v)

class CashTransactionCreate(CashTransactionBase):
    session_id: int

class CashTransactionUpdate(BaseModel):
    amount: Optional[float] = Field(None, ge=-999999999.99, le=999999999.99)
    description: Optional[str] = Field(None, max_length=500)
    payment_method: Optional[PaymentMethod] = None
    category: Optional[str] = Field(None, max_length=100)
    
    @validator('description')
    def sanitize_description(cls, v):
        """Remove potentially dangerous characters from description."""
        return sanitize_text(v)
    
    @validator('category')
    def sanitize_category(cls, v):
        """Remove potentially dangerous characters from category."""
        return sanitize_text(v)

class CashTransactionInDBBase(CashTransactionBase):
    id: int
    session_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        use_enum_values = True

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
        # Handle enum conversion for responses
        use_enum_values = True

    @validator('data', pre=True)
    def parse_report_data(cls, v):
        """Parse JSON string to dictionary for API responses."""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return {}
        return v

# Response models
class CashRegisterSession(CashRegisterSessionInDBBase):
    transactions: List[CashTransactionInDBBase] = []
    reports: List[CashRegisterReportInDBBase] = []
    opened_by_user: Optional['User'] = None
    
    class Config:
        orm_mode = True

class CashTransaction(CashTransactionInDBBase):
    pass

class CashRegisterReport(CashRegisterReportInDBBase):
    pass

# Additional models for reports
class CashDifferenceReport(BaseModel):
    session_id: int = Field(..., ge=1)
    expected_balance: float = Field(..., ge=-999999999.99, le=999999999.99)
    actual_balance: float = Field(..., ge=-999999999.99, le=999999999.99)
    difference: float = Field(..., ge=-999999999.99, le=999999999.99)
    notes: Optional[str] = Field(None, max_length=1000)
    
    @validator('notes')
    def sanitize_notes(cls, v):
        """Remove potentially dangerous characters from notes."""
        return sanitize_text(v)

class DailySummaryReport(BaseModel):
    session_id: int
    session_number: int
    opened_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    total_sales: float = 0.0
    total_refunds: float = 0.0
    total_tips: float = 0.0
    total_expenses: float = 0.0
    total_transactions: int = 0
    net_cash_flow: float = 0.0
    payment_breakdown: Dict[str, float] = {}

class PaymentBreakdownReport(BaseModel):
    session_id: int
    cash_payments: float
    card_payments: float
    digital_payments: float
    other_payments: float

class ExpenseCreate(BaseModel):
    amount: float = Field(..., gt=0, le=999999999.99, description="Expense amount (always positive)")
    description: str = Field(..., min_length=1, max_length=500, description="Description of the expense")
    category: Optional[str] = Field(None, max_length=100, description="Expense category (e.g., supplies, utilities, maintenance)")
    
    @validator('description')
    def sanitize_description(cls, v):
        """Remove potentially dangerous characters from description."""
        return sanitize_text(v)
    
    @validator('category')
    def sanitize_category(cls, v):
        """Remove potentially dangerous characters from category."""
        return sanitize_text(v)

# Denomination counting models
class DenominationCount(BaseModel):
    """Cash denomination breakdown for counting drawer (Mexican Pesos).
    
    MXN denominations:
    - Bills: $1000, $500, $200, $100, $50, $20
    - Coins: $20, $10, $5, $2, $1, $0.50
    """
    # MXN Bills
    bills_1000: int = Field(default=0, ge=0, le=10000, description="$1000 MXN bills")
    bills_500: int = Field(default=0, ge=0, le=10000, description="$500 MXN bills")
    bills_200: int = Field(default=0, ge=0, le=10000, description="$200 MXN bills")
    bills_100: int = Field(default=0, ge=0, le=10000, description="$100 MXN bills")
    bills_50: int = Field(default=0, ge=0, le=10000, description="$50 MXN bills")
    bills_20: int = Field(default=0, ge=0, le=10000, description="$20 MXN bills")
    
    # MXN Coins
    coins_20: int = Field(default=0, ge=0, le=10000, description="$20 MXN coins")
    coins_10: int = Field(default=0, ge=0, le=10000, description="$10 MXN coins")
    coins_5: int = Field(default=0, ge=0, le=10000, description="$5 MXN coins")
    coins_2: int = Field(default=0, ge=0, le=10000, description="$2 MXN coins")
    coins_1: int = Field(default=0, ge=0, le=10000, description="$1 MXN coins")
    coins_50_cent: int = Field(default=0, ge=0, le=10000, description="$0.50 MXN coins")

    def calculate_total(self) -> float:
        """Calculate total amount from MXN denominations."""
        return (
            self.bills_1000 * 1000.00 +
            self.bills_500 * 500.00 +
            self.bills_200 * 200.00 +
            self.bills_100 * 100.00 +
            self.bills_50 * 50.00 +
            self.bills_20 * 20.00 +
            self.coins_20 * 20.00 +
            self.coins_10 * 10.00 +
            self.coins_5 * 5.00 +
            self.coins_2 * 2.00 +
            self.coins_1 * 1.00 +
            self.coins_50_cent * 0.50
        )

class SessionCloseWithDenominations(CashRegisterSessionUpdate):
    """Session close data with denomination counting."""
    denominations: Optional[DenominationCount] = None

class CutWithDenominations(PaymentBreakdownReport):
    """Cut data with denomination counting."""
    denominations: Optional[DenominationCount] = None

# Report query models
class ReportDateRange(BaseModel):
    """Date range for report queries."""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    report_type: Optional[ReportType] = None

class WeeklySummaryReport(BaseModel):
    """Weekly summary aggregating multiple sessions."""
    start_date: datetime
    end_date: datetime
    total_sessions: int
    total_sales: float
    total_refunds: float
    total_tips: float
    total_expenses: float
    total_transactions: int
    net_cash_flow: float
    average_session_value: float
    payment_breakdown: Dict[str, float]

# Update forward references
from .user import User
CashRegisterSession.update_forward_refs()
