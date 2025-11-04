from sqlalchemy import String, Integer, Float, Boolean, DateTime, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional, TYPE_CHECKING, Dict, Any, List
from datetime import datetime, timedelta
from enum import Enum as PyEnum
from .base import BaseModel

if TYPE_CHECKING:
    from .restaurant import Restaurant
    from .subscription_plan import SubscriptionPlan

class SubscriptionStatus(str, PyEnum):
    """Subscription status enumeration"""
    TRIAL = "trial"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

class BillingCycle(str, PyEnum):
    """Billing cycle enumeration"""
    MONTHLY = "monthly"
    ANNUAL = "annual"

class RestaurantSubscription(BaseModel):
    """
    Active subscription for a restaurant.
    Links restaurant to a plan and tracks billing.
    """
    __tablename__ = "restaurant_subscriptions"
    
    # Foreign keys
    restaurant_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("restaurants.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    plan_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("subscription_plans.id"),
        nullable=False,
        index=True
    )
    
    # Subscription details
    status: Mapped[SubscriptionStatus] = mapped_column(
        SQLEnum(SubscriptionStatus, name='subscription_status', values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        default=SubscriptionStatus.TRIAL,
        index=True
    )
    billing_cycle: Mapped[BillingCycle] = mapped_column(
        SQLEnum(BillingCycle, name='billing_cycle', values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        default=BillingCycle.MONTHLY
    )
    
    # Dates
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    trial_end_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    current_period_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    current_period_end: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Pricing (stored for historical tracking)
    base_price: Mapped[float] = mapped_column(Float, nullable=False)
    total_price: Mapped[float] = mapped_column(Float, nullable=False)  # Base + addons
    
    # Discount tracking
    discount_percentage: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    discount_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    discount_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Auto-renewal
    auto_renew: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Additional metadata
    subscription_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Relationships
    restaurant: Mapped["Restaurant"] = relationship("Restaurant", back_populates="subscription")
    plan: Mapped["SubscriptionPlan"] = relationship("SubscriptionPlan", back_populates="subscriptions")
    addons: Mapped[List["RestaurantAddon"]] = relationship(
        "RestaurantAddon",
        back_populates="subscription",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<RestaurantSubscription(id={self.id}, restaurant_id={self.restaurant_id}, status='{self.status}')>"
    
    @property
    def is_trial(self) -> bool:
        """Check if subscription is in trial period"""
        return self.status == SubscriptionStatus.TRIAL
    
    @property
    def is_active(self) -> bool:
        """Check if subscription is active (including trial)"""
        return self.status in [SubscriptionStatus.TRIAL, SubscriptionStatus.ACTIVE]
    
    @property
    def can_operate(self) -> bool:
        """
        Check if restaurant can operate based on subscription status and expiration.
        This is the single source of truth for subscription validation.
        """
        # Check status first
        if self.status not in [SubscriptionStatus.TRIAL, SubscriptionStatus.ACTIVE]:
            return False
        
        # For TRIAL, check if trial has expired
        if self.status == SubscriptionStatus.TRIAL and self.is_trial_expired:
            return False
        
        # For ACTIVE, check if current period has ended
        if self.status == SubscriptionStatus.ACTIVE:
            if self.current_period_end:
                now = datetime.utcnow()
                # Remove timezone info from both for comparison if needed
                period_end = self.current_period_end.replace(tzinfo=None) if self.current_period_end.tzinfo else self.current_period_end
                
                # Debug logging
                print(f"[CAN_OPERATE] Now (UTC): {now}")
                print(f"[CAN_OPERATE] Period end: {period_end}")
                print(f"[CAN_OPERATE] Period end < now: {period_end < now}")
                print(f"[CAN_OPERATE] Days until renewal: {self.days_until_renewal}")
                
                # If period has ended, subscription is expired
                if period_end < now:
                    print(f"[CAN_OPERATE] Subscription {self.id} period has ended - cannot operate")
                    return False
        
        return True
    
    @property
    def is_expired(self) -> bool:
        """
        Check if subscription period has expired (regardless of status field).
        This checks the actual dates, not just the status field.
        """
        if self.status == SubscriptionStatus.TRIAL:
            return self.is_trial_expired
        
        if self.status == SubscriptionStatus.ACTIVE:
            if self.current_period_end:
                now = datetime.utcnow()
                period_end = self.current_period_end.replace(tzinfo=None) if self.current_period_end.tzinfo else self.current_period_end
                return period_end < now
        
        # If status is already EXPIRED, CANCELLED, etc.
        return self.status not in [SubscriptionStatus.TRIAL, SubscriptionStatus.ACTIVE]
    
    def check_and_update_expiration(self, db_session) -> bool:
        """
        Check if subscription has expired and update status automatically.
        Returns True if status was updated, False otherwise.
        
        This should be called whenever subscription is accessed to ensure
        the status field reflects the actual expiration state.
        """
        # Skip if already in a terminal state
        if self.status in [SubscriptionStatus.EXPIRED, SubscriptionStatus.CANCELLED]:
            return False
        
        # Check if trial has expired
        if self.status == SubscriptionStatus.TRIAL and self.is_trial_expired:
            print(f"[AUTO-EXPIRE] Trial subscription {self.id} has expired, updating status")
            self.status = SubscriptionStatus.EXPIRED
            db_session.commit()
            return True
        
        # Check if active subscription period has ended
        if self.status == SubscriptionStatus.ACTIVE and self.current_period_end:
            now = datetime.utcnow()
            period_end = self.current_period_end.replace(tzinfo=None) if self.current_period_end.tzinfo else self.current_period_end
            
            if period_end < now:
                print(f"[AUTO-EXPIRE] Active subscription {self.id} period has ended, updating status to EXPIRED")
                self.status = SubscriptionStatus.EXPIRED
                db_session.commit()
                return True
        
        return False
    
    @property
    def days_until_renewal(self) -> int:
        """Calculate days until next renewal"""
        if not self.current_period_end:
            return 0
        
        now = datetime.utcnow()
        # Remove timezone info for comparison if needed
        period_end = self.current_period_end.replace(tzinfo=None) if self.current_period_end.tzinfo else self.current_period_end
        
        delta = period_end - now
        return max(0, delta.days)
    
    @property
    def trial_days_remaining(self) -> int:
        """Calculate trial days remaining"""
        if not self.trial_end_date or self.status != SubscriptionStatus.TRIAL:
            return 0
        
        now = datetime.utcnow()
        # Remove timezone info for comparison if needed
        trial_end = self.trial_end_date.replace(tzinfo=None) if self.trial_end_date.tzinfo else self.trial_end_date
        
        delta = trial_end - now
        return max(0, delta.days)
    
    @property
    def is_trial_expired(self) -> bool:
        """Check if trial has expired"""
        if not self.trial_end_date:
            return False
        
        now = datetime.utcnow()
        # Remove timezone info for comparison if needed
        trial_end = self.trial_end_date.replace(tzinfo=None) if self.trial_end_date.tzinfo else self.trial_end_date
        
        return now > trial_end
    
    def calculate_total_cost(self) -> float:
        """Calculate total cost including addons"""
        total = self.base_price
        
        # Add addon costs
        for addon in self.addons:
            if addon.is_active:
                total += addon.total_price
        
        # Apply discount
        if self.discount_percentage > 0:
            total = total * (1 - self.discount_percentage / 100)
        elif self.discount_amount > 0:
            total = max(0, total - self.discount_amount)
        
        return round(total, 2)
    
    def get_limits(self) -> Dict[str, Any]:
        """Get all limits for this subscription (plan + addons)"""
        limits = {
            'max_admin_users': self.plan.max_admin_users,
            'max_waiter_users': self.plan.max_waiter_users,
            'max_cashier_users': self.plan.max_cashier_users,
            'max_kitchen_users': self.plan.max_kitchen_users,
            'max_owner_users': self.plan.max_owner_users,
            'max_tables': self.plan.max_tables,
            'max_menu_items': self.plan.max_menu_items,
            'max_categories': self.plan.max_categories,
            'has_kitchen_module': self.plan.has_kitchen_module,
            'has_ingredients_module': self.plan.has_ingredients_module,
            'has_inventory_module': self.plan.has_inventory_module,
            'has_advanced_reports': self.plan.has_advanced_reports,
            'has_multi_branch': self.plan.has_multi_branch,
            'report_retention_days': self.plan.report_retention_days,
        }
        
        # Add limits from addons
        for restaurant_addon in self.addons:
            if restaurant_addon.is_active:
                addon = restaurant_addon.addon
                limits['max_tables'] += addon.provides_tables * restaurant_addon.quantity
                limits['max_menu_items'] += addon.provides_menu_items * restaurant_addon.quantity
                
                # Add users from addons
                if addon.provides_users > 0:
                    # Distribute extra users (could be any role)
                    limits['max_waiter_users'] += addon.provides_users * restaurant_addon.quantity
                
                # Enable features from addons
                if addon.enables_inventory:
                    limits['has_inventory_module'] = True
                if addon.enables_advanced_reports:
                    limits['has_advanced_reports'] = True
                if addon.enables_kitchen:
                    limits['has_kitchen_module'] = True
        
        return limits
