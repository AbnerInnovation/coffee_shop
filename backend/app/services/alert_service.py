from sqlalchemy.orm import Session
from app.models.subscription_alert import SubscriptionAlert, AlertType
from app.models.restaurant_subscription import RestaurantSubscription, SubscriptionStatus
from datetime import datetime, timedelta


class AlertService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_alert(self, restaurant_id: int, subscription_id: int, 
                    alert_type: AlertType, title: str, message: str) -> SubscriptionAlert:
        """Create a new alert"""
        alert = SubscriptionAlert(
            restaurant_id=restaurant_id,
            subscription_id=subscription_id,
            alert_type=alert_type,
            title=title,
            message=message,
            is_read=False
        )
        
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        
        return alert
    
    def get_restaurant_alerts(self, restaurant_id: int, unread_only: bool = False):
        """Get alerts for a restaurant"""
        query = self.db.query(SubscriptionAlert).filter(
            SubscriptionAlert.restaurant_id == restaurant_id,
            SubscriptionAlert.deleted_at.is_(None)
        )
        
        if unread_only:
            query = query.filter(SubscriptionAlert.is_read == False)
        
        return query.order_by(SubscriptionAlert.created_at.desc()).all()
    
    def mark_as_read(self, alert_ids: list[int], restaurant_id: int):
        """Mark alerts as read"""
        self.db.query(SubscriptionAlert).filter(
            SubscriptionAlert.id.in_(alert_ids),
            SubscriptionAlert.restaurant_id == restaurant_id
        ).update({
            "is_read": True,
            "read_at": datetime.utcnow()
        }, synchronize_session=False)
        
        self.db.commit()
    
    def check_expiring_subscriptions(self):
        """Check for subscriptions expiring in 3 days and create alerts"""
        three_days_from_now = datetime.utcnow() + timedelta(days=3)
        
        subscriptions = self.db.query(RestaurantSubscription).filter(
            RestaurantSubscription.status == SubscriptionStatus.ACTIVE,
            RestaurantSubscription.current_period_end <= three_days_from_now,
            RestaurantSubscription.current_period_end > datetime.utcnow(),
            RestaurantSubscription.deleted_at.is_(None)
        ).all()
        
        for sub in subscriptions:
            # Check if alert already exists
            existing = self.db.query(SubscriptionAlert).filter(
                SubscriptionAlert.subscription_id == sub.id,
                SubscriptionAlert.alert_type == AlertType.EXPIRING_SOON,
                SubscriptionAlert.created_at >= datetime.utcnow() - timedelta(days=4)
            ).first()
            
            if not existing:
                period_end = sub.current_period_end.replace(tzinfo=None) if sub.current_period_end.tzinfo else sub.current_period_end
                days_left = (period_end - datetime.utcnow()).days
                self.create_alert(
                    restaurant_id=sub.restaurant_id,
                    subscription_id=sub.id,
                    alert_type=AlertType.EXPIRING_SOON,
                    title="Suscripción por Expirar",
                    message=f"Tu suscripción expira en {days_left} días. Renueva ahora para evitar interrupciones."
                )
