"""
Middleware for checking active subscription status.
Blocks all operations if subscription is expired or suspended.
"""
from fastapi import Request, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.restaurant_subscription import RestaurantSubscription, SubscriptionStatus
from app.models.user import UserRole


class SubscriptionStatusMiddleware:
    """Middleware to enforce active subscription requirement"""
    
    @staticmethod
    def check_active_subscription(db: Session, restaurant_id: int, user_role: str = None) -> None:
        """
        Check if restaurant has an active subscription.
        Raises HTTPException if subscription is expired or suspended.
        
        SYSADMIN users bypass this check.
        """
        # SYSADMIN can always access (for management purposes)
        if user_role == UserRole.SYSADMIN.value:
            return
        
        # Get restaurant's most recent active or trial subscription
        subscription = db.query(RestaurantSubscription).filter(
            RestaurantSubscription.restaurant_id == restaurant_id,
            RestaurantSubscription.deleted_at.is_(None),
            RestaurantSubscription.status.in_([SubscriptionStatus.TRIAL, SubscriptionStatus.ACTIVE])
        ).order_by(RestaurantSubscription.created_at.desc()).first()
        
        # No subscription found
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No se encontró una suscripción activa. Por favor contacta al administrador para activar tu cuenta."
            )
        
        # Check and auto-update expiration status
        subscription.update_status(db)
        
        # Use the can_operate property which handles all checks
        if not subscription.can_operate:
            # Provide specific error message based on status
            if subscription.status == SubscriptionStatus.EXPIRED:
                detail = "Tu suscripción ha expirado. Por favor renueva tu plan para continuar usando el sistema."
            elif subscription.status == SubscriptionStatus.CANCELLED:
                detail = "Tu suscripción ha sido cancelada. Por favor contacta al administrador."
            elif subscription.status == SubscriptionStatus.TRIAL and subscription.is_trial_expired:
                detail = "Tu período de prueba ha expirado. Por favor elige un plan de pago para continuar."
            elif subscription.status == SubscriptionStatus.PAST_DUE:
                detail = "Tu suscripción tiene pagos pendientes. Por favor actualiza tu método de pago para continuar."
            elif subscription.status == SubscriptionStatus.PENDING_PAYMENT:
                detail = "Tu pago está en revisión. Podrás operar una vez que sea aprobado."
            elif subscription.status == SubscriptionStatus.ACTIVE:
                detail = "Tu suscripción ha vencido. Por favor renueva tu plan para continuar usando el sistema."
            else:
                detail = "Tu suscripción no está activa. Por favor contacta al administrador."
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=detail
            )


# Dependency function for FastAPI
def require_active_subscription(
    request: Request,
    db: Session
) -> None:
    """
    Dependency to check if restaurant has active subscription.
    Use this in endpoints that require active subscription.
    """
    restaurant_id = getattr(request.state, 'restaurant_id', None)
    user_role = getattr(request.state, 'user_role', None)
    
    if not restaurant_id:
        # No restaurant context, skip check (e.g., SYSADMIN endpoints)
        return
    
    SubscriptionStatusMiddleware.check_active_subscription(db, restaurant_id, user_role)
