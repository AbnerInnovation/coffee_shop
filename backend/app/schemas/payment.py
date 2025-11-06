from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class PaymentMethodEnum(str, Enum):
    TRANSFER = "transfer"
    CASH = "cash"
    CARD = "card"
    STRIPE = "stripe"
    PAYPAL = "paypal"
    OTHER = "other"


class PaymentStatusEnum(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    FAILED = "failed"


# Request schemas
class PaymentSubmit(BaseModel):
    """Schema for submitting payment proof"""
    reference_number: str
    payment_date: datetime
    proof_image_url: Optional[str] = None
    notes: Optional[str] = None


class PaymentApprove(BaseModel):
    """Schema for approving a payment"""
    pass  # No additional data needed


class PaymentReject(BaseModel):
    """Schema for rejecting a payment"""
    reason: str = Field(..., min_length=10, max_length=500)


# Response schemas
class PaymentResponse(BaseModel):
    """Response schema for payment details"""
    id: int
    restaurant_id: int
    subscription_id: int
    plan_id: int
    amount: float
    billing_cycle: str
    payment_method: PaymentMethodEnum
    reference_number: Optional[str]
    payment_date: Optional[datetime]
    proof_image_url: Optional[str]
    notes: Optional[str]
    status: PaymentStatusEnum
    reviewed_by: Optional[int]
    reviewed_at: Optional[datetime]
    rejection_reason: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    # Nested data
    restaurant_name: Optional[str] = None
    plan_name: Optional[str] = None
    reviewer_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class RenewalRequest(BaseModel):
    """Schema for requesting subscription renewal"""
    plan_id: int
    billing_cycle: str = Field(..., pattern="^(monthly|annual)$")
    notes: Optional[str] = None


class RenewalResponse(BaseModel):
    """Response after requesting renewal"""
    payment_id: int
    reference_number: str
    amount: float
    instructions: str
    bank_details: dict
