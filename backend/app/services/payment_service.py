from sqlalchemy.orm import Session
from app.models.subscription_payment import SubscriptionPayment, PaymentStatus, PaymentMethod
from app.models.restaurant_subscription import RestaurantSubscription, SubscriptionStatus
from app.models.subscription_alert import SubscriptionAlert, AlertType
from datetime import datetime, timedelta
import secrets


class PaymentService:
    def __init__(self, db: Session):
        self.db = db
    
    def generate_reference_number(self, restaurant_id: int) -> str:
        """Generate unique reference number for payment"""
        date_str = datetime.now().strftime("%Y%m")
        random_suffix = secrets.token_hex(3).upper()
        return f"REST-{restaurant_id:03d}-{date_str}-{random_suffix}"
    
    def create_renewal_request(self, restaurant_id: int, subscription_id: int, 
                               plan_id: int, billing_cycle: str, amount: float) -> SubscriptionPayment:
        """Create a new payment request for renewal"""
        reference_number = self.generate_reference_number(restaurant_id)
        
        payment = SubscriptionPayment(
            restaurant_id=restaurant_id,
            subscription_id=subscription_id,
            plan_id=plan_id,
            amount=amount,
            billing_cycle=billing_cycle,
            payment_method=PaymentMethod.TRANSFER,
            reference_number=reference_number,
            status=PaymentStatus.PENDING
        )
        
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        
        return payment
    
    def submit_payment_proof(self, payment_id: int, payment_date: datetime, 
                            proof_url: str = None, notes: str = None) -> SubscriptionPayment:
        """Submit payment proof for review"""
        payment = self.db.query(SubscriptionPayment).filter(
            SubscriptionPayment.id == payment_id
        ).first()
        
        if not payment:
            raise ValueError("Payment not found")
        
        if payment.status != PaymentStatus.PENDING:
            raise ValueError("Payment already processed")
        
        payment.payment_date = payment_date
        payment.proof_image_url = proof_url
        payment.notes = notes
        payment.status = PaymentStatus.PENDING
        
        # Update subscription status
        subscription = self.db.query(RestaurantSubscription).filter(
            RestaurantSubscription.id == payment.subscription_id
        ).first()
        
        if subscription:
            subscription.status = SubscriptionStatus.PENDING_PAYMENT
            subscription.pending_payment_id = payment.id
        
        self.db.commit()
        self.db.refresh(payment)
        
        return payment
    
    def approve_payment(self, payment_id: int, reviewer_id: int) -> SubscriptionPayment:
        """Approve payment and activate subscription"""
        payment = self.db.query(SubscriptionPayment).filter(
            SubscriptionPayment.id == payment_id
        ).first()
        
        if not payment:
            raise ValueError("Payment not found")
        
        if payment.status != PaymentStatus.PENDING:
            raise ValueError("Payment already processed")
        
        # Approve payment
        payment.status = PaymentStatus.APPROVED
        payment.reviewed_by = reviewer_id
        payment.reviewed_at = datetime.utcnow()
        
        # Activate subscription
        subscription = self.db.query(RestaurantSubscription).filter(
            RestaurantSubscription.id == payment.subscription_id
        ).first()
        
        if subscription:
            subscription.status = SubscriptionStatus.ACTIVE
            subscription.current_period_start = datetime.utcnow()
            
            if payment.billing_cycle == "monthly":
                subscription.current_period_end = datetime.utcnow() + timedelta(days=30)
            else:  # annual
                subscription.current_period_end = datetime.utcnow() + timedelta(days=365)
            
            subscription.grace_period_end = None
            subscription.pending_payment_id = None
            
            # Create alert
            alert = SubscriptionAlert(
                restaurant_id=payment.restaurant_id,
                subscription_id=subscription.id,
                alert_type=AlertType.PAYMENT_APPROVED,
                title="Pago Aprobado",
                message=f"Tu pago de ${payment.amount} ha sido aprobado. Tu suscripción está activa.",
                is_read=False
            )
            self.db.add(alert)
        
        self.db.commit()
        self.db.refresh(payment)
        
        return payment
    
    def reject_payment(self, payment_id: int, reviewer_id: int, reason: str) -> SubscriptionPayment:
        """Reject payment"""
        payment = self.db.query(SubscriptionPayment).filter(
            SubscriptionPayment.id == payment_id
        ).first()
        
        if not payment:
            raise ValueError("Payment not found")
        
        if payment.status != PaymentStatus.PENDING:
            raise ValueError("Payment already processed")
        
        # Reject payment
        payment.status = PaymentStatus.REJECTED
        payment.reviewed_by = reviewer_id
        payment.reviewed_at = datetime.utcnow()
        payment.rejection_reason = reason
        
        # Update subscription
        subscription = self.db.query(RestaurantSubscription).filter(
            RestaurantSubscription.id == payment.subscription_id
        ).first()
        
        if subscription:
            subscription.status = SubscriptionStatus.PAST_DUE
            subscription.pending_payment_id = None
            
            # Create alert
            alert = SubscriptionAlert(
                restaurant_id=payment.restaurant_id,
                subscription_id=subscription.id,
                alert_type=AlertType.PAYMENT_REJECTED,
                title="Pago Rechazado",
                message=f"Tu pago ha sido rechazado. Razón: {reason}",
                is_read=False
            )
            self.db.add(alert)
        
        self.db.commit()
        self.db.refresh(payment)
        
        return payment
    
    def get_pending_payments(self, restaurant_id: int = None):
        """Get all pending payments, optionally filtered by restaurant"""
        query = self.db.query(SubscriptionPayment).filter(
            SubscriptionPayment.status == PaymentStatus.PENDING,
            SubscriptionPayment.deleted_at.is_(None)
        )
        
        if restaurant_id:
            query = query.filter(SubscriptionPayment.restaurant_id == restaurant_id)
        
        return query.order_by(SubscriptionPayment.created_at.desc()).all()
    
    def get_payment_by_id(self, payment_id: int) -> SubscriptionPayment:
        """Get payment by ID"""
        return self.db.query(SubscriptionPayment).filter(
            SubscriptionPayment.id == payment_id,
            SubscriptionPayment.deleted_at.is_(None)
        ).first()
