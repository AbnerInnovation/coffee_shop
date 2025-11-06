from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class AlertTypeEnum(str, Enum):
    EXPIRING_SOON = "expiring_soon"
    GRACE_PERIOD = "grace_period"
    SUSPENDED = "suspended"
    PAYMENT_APPROVED = "payment_approved"
    PAYMENT_REJECTED = "payment_rejected"


class AlertResponse(BaseModel):
    """Response schema for subscription alerts"""
    id: int
    restaurant_id: int
    subscription_id: int
    alert_type: AlertTypeEnum
    title: str
    message: str
    is_read: bool
    read_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class AlertMarkRead(BaseModel):
    """Schema for marking alert as read"""
    alert_ids: list[int]
