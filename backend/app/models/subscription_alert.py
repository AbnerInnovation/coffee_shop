from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, Boolean, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from enum import Enum
from .base import BaseModel

if TYPE_CHECKING:
    from .restaurant import Restaurant
    from .restaurant_subscription import RestaurantSubscription


class AlertType(str, Enum):
    """Alert type enum"""
    EXPIRING_SOON = "expiring_soon"  # 3 days before expiration
    GRACE_PERIOD = "grace_period"    # During 3-day grace period
    SUSPENDED = "suspended"          # Account suspended
    PAYMENT_APPROVED = "payment_approved"  # Payment was approved
    PAYMENT_REJECTED = "payment_rejected"  # Payment was rejected


class SubscriptionAlert(BaseModel):
    """
    Subscription alerts for restaurant admins.
    Tracks important subscription events and notifications.
    """
    __tablename__ = "subscription_alerts"
    
    # Foreign Keys
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurants.id"), nullable=False, index=True)
    subscription_id: Mapped[int] = mapped_column(ForeignKey("restaurant_subscriptions.id"), nullable=False)
    
    # Alert details
    alert_type: Mapped[AlertType] = mapped_column(
        SQLEnum(AlertType, name='alert_type', values_callable=lambda obj: [e.value for e in obj]),
        nullable=False, 
        index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Status
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    restaurant: Mapped["Restaurant"] = relationship("Restaurant", back_populates="alerts")
    subscription: Mapped["RestaurantSubscription"] = relationship("RestaurantSubscription")
    
    def __repr__(self) -> str:
        return f"<SubscriptionAlert(id={self.id}, restaurant_id={self.restaurant_id}, type={self.alert_type}, read={self.is_read})>"
