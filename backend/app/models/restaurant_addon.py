from sqlalchemy import Integer, Float, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional, TYPE_CHECKING, Dict, Any
from .base import BaseModel

if TYPE_CHECKING:
    from .restaurant_subscription import RestaurantSubscription
    from .subscription_addon import SubscriptionAddon

class RestaurantAddon(BaseModel):
    """
    Add-ons purchased by a restaurant for their subscription.
    Tracks quantity and pricing.
    """
    __tablename__ = "restaurant_addons"
    
    # Foreign keys
    subscription_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("restaurant_subscriptions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    addon_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("subscription_addons.id"),
        nullable=False,
        index=True
    )
    
    # Quantity (for quantifiable addons like extra users, tables, etc.)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    
    # Pricing (stored for historical tracking)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    total_price: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Additional metadata
    addon_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Relationships
    subscription: Mapped["RestaurantSubscription"] = relationship(
        "RestaurantSubscription",
        back_populates="addons"
    )
    addon: Mapped["SubscriptionAddon"] = relationship(
        "SubscriptionAddon",
        back_populates="restaurant_addons"
    )
    
    def __repr__(self) -> str:
        return f"<RestaurantAddon(id={self.id}, subscription_id={self.subscription_id}, addon_id={self.addon_id}, qty={self.quantity})>"
    
    def calculate_total_price(self) -> float:
        """Calculate total price based on quantity"""
        return round(self.unit_price * self.quantity, 2)
    
    def update_total_price(self) -> None:
        """Update total price based on current quantity and unit price"""
        self.total_price = self.calculate_total_price()
