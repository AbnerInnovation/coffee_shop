from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Text, Boolean, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from enum import Enum
from .base import BaseModel

if TYPE_CHECKING:
    from .restaurant import Restaurant
    from .restaurant_subscription import RestaurantSubscription
    from .subscription_plan import SubscriptionPlan
    from .user import User


class PaymentStatus(str, Enum):
    """Payment status enum"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    FAILED = "failed"


class PaymentMethod(str, Enum):
    """Payment method enum"""
    TRANSFER = "transfer"
    CASH = "cash"
    CARD = "card"
    STRIPE = "stripe"
    PAYPAL = "paypal"
    OTHER = "other"


class SubscriptionPayment(BaseModel):
    """
    Subscription payment records for manual and automatic payments.
    Tracks payment submissions, approvals, and rejections.
    """
    __tablename__ = "subscription_payments"
    
    # Foreign Keys
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurants.id"), nullable=False, index=True)
    subscription_id: Mapped[int] = mapped_column(ForeignKey("restaurant_subscriptions.id"), nullable=False)
    plan_id: Mapped[int] = mapped_column(ForeignKey("subscription_plans.id"), nullable=False)
    
    # Payment details
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    billing_cycle: Mapped[str] = mapped_column(String(20), nullable=False)  # 'monthly' | 'annual'
    payment_method: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # Manual payment fields
    reference_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, unique=True, index=True)
    payment_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    proof_image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Automatic payment fields (for future use)
    stripe_payment_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    card_last4: Mapped[Optional[str]] = mapped_column(String(4), nullable=True)
    card_brand: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    auto_approved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default='pending', nullable=False, index=True)
    
    # Review information
    reviewed_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Retry logic (for automatic payments)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    next_retry_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    restaurant: Mapped["Restaurant"] = relationship("Restaurant", back_populates="payments")
    subscription: Mapped["RestaurantSubscription"] = relationship("RestaurantSubscription", foreign_keys=[subscription_id])
    plan: Mapped["SubscriptionPlan"] = relationship("SubscriptionPlan")
    reviewer: Mapped[Optional["User"]] = relationship("User", foreign_keys=[reviewed_by])
    
    def __repr__(self) -> str:
        return f"<SubscriptionPayment(id={self.id}, restaurant_id={self.restaurant_id}, amount={self.amount}, status={self.status})>"
