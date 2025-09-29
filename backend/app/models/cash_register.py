from enum import Enum as PyEnum
from sqlalchemy import Column, DateTime, Enum as SQLEnum, ForeignKey, Text, DECIMAL, Integer, event
from sqlalchemy.orm import relationship, validates
from typing import TYPE_CHECKING, Optional
from .base import BaseModel

if TYPE_CHECKING:
    from .user import User
    from .order import Order

# Define enums for cash register
class SessionStatus(str, PyEnum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"

class TransactionType(str, PyEnum):
    SALE = "sale"
    REFUND = "refund"
    CANCELLATION = "cancellation"
    TIP = "tip"
    MANUAL_ADD = "manual_add"
    MANUAL_WITHDRAW = "manual_withdraw"

class ReportType(str, PyEnum):
    DAILY_SUMMARY = "daily_summary"
    CASH_DIFFERENCE = "cash_difference"
    PAYMENT_BREAKDOWN = "payment_breakdown"

class CashRegisterSession(BaseModel):
    __tablename__ = "cash_register_sessions"

    opened_at = Column(DateTime, nullable=False)
    closed_at = Column(DateTime, nullable=True)
    opened_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    cashier_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    initial_balance = Column(DECIMAL(10, 2), nullable=False, default=0.00)
    final_balance = Column(DECIMAL(10, 2), nullable=True)
    expected_balance = Column(DECIMAL(10, 2), nullable=False, default=0.00)
    actual_balance = Column(DECIMAL(10, 2), nullable=True)
    status = Column(SQLEnum(SessionStatus, name='session_status'), default=SessionStatus.OPEN, nullable=False)
    notes = Column(Text, nullable=True)

    # Relationships
    opened_by_user = relationship("User", foreign_keys=[opened_by_user_id])
    cashier = relationship("User", foreign_keys=[cashier_id])
    transactions = relationship("CashTransaction", back_populates="session")
    reports = relationship("CashRegisterReport", back_populates="session")

    def __repr__(self) -> str:
        return f"<CashRegisterSession(id={self.id}, status='{self.status}', opened_by={self.opened_by_user_id})>"

class CashTransaction(BaseModel):
    __tablename__ = "cash_transactions"

    session_id = Column(Integer, ForeignKey("cash_register_sessions.id"), nullable=False)
    transaction_type = Column(SQLEnum(TransactionType, name='transaction_type', values_callable=lambda x: [e.value for e in x]), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    description = Column(Text, nullable=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    session = relationship("CashRegisterSession", back_populates="transactions")
    order = relationship("Order")
    created_by_user = relationship("User")

    def __repr__(self) -> str:
        return f"<CashTransaction(id={self.id}, type='{self.transaction_type}', amount={self.amount})>"


class CashRegisterReport(BaseModel):
    __tablename__ = "cash_register_reports"

    session_id = Column(Integer, ForeignKey("cash_register_sessions.id"), nullable=False)
    report_type = Column(SQLEnum(ReportType, name='report_type', values_callable=lambda x: [e.value for e in x]), nullable=False)
    data = Column(Text, nullable=False)  # JSON string for report data
    generated_at = Column(DateTime, nullable=False)

    # Relationships
    session = relationship("CashRegisterSession", back_populates="reports")

    def __repr__(self) -> str:
        return f"<CashRegisterReport(id={self.id}, type='{self.report_type}', session={self.session_id})>"
