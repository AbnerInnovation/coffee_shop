"""
Subscription API endpoints for restaurant users.
Allows restaurants to view their subscription, usage, and upgrade options.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.db.base import get_db
from app.models import (
    User, Restaurant, RestaurantSubscription, SubscriptionPlan,
    MenuItem, Table, Category, SubscriptionStatus
)
from app.services.subscription_service import SubscriptionService
from app.services.payment_service import PaymentService
from app.services.alert_service import AlertService
from app.api.deps import get_current_user, get_current_restaurant, require_admin_or_sysadmin
from app.services.user import get_current_active_user
from app.schemas.payment import RenewalRequest, RenewalResponse, PaymentSubmit, PaymentResponse
from app.schemas.alert import AlertResponse, AlertMarkRead

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.get("/my-subscription")
def get_my_subscription(
    current_user: User = Depends(require_admin_or_sysadmin),
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
):
    """Get current restaurant's subscription details. Requires admin or sysadmin privileges."""
    
    # Get the most recent subscription (including expired ones)
    subscription = db.query(RestaurantSubscription).filter(
        RestaurantSubscription.restaurant_id == restaurant.id,
        RestaurantSubscription.deleted_at.is_(None)
    ).order_by(RestaurantSubscription.created_at.desc()).first()
    
    if not subscription:
        return {
            "has_subscription": False,
            "message": "No subscription found"
        }
    
    # Check and auto-update expiration status
    subscription.update_status(db)
    
    # Check for expiring subscriptions and create alerts if needed
    try:
        from app.services.alert_service import AlertService
        alert_service = AlertService(db)
        alert_service.check_expiring_subscriptions()
    except Exception as e:
        # Log error but don't fail the request
        print(f"Warning: Could not check expiring subscriptions: {e}")
    
    return {
        "has_subscription": True,
        "subscription": {
            "id": subscription.id,
            "plan": {
                "id": subscription.plan.id,
                "name": subscription.plan.display_name,
                "tier": subscription.plan.tier.value,
                "is_trial": subscription.plan.is_trial
            },
            "status": subscription.status.value,
            "billing_cycle": subscription.billing_cycle.value,
            "total_price": subscription.total_price,
            "start_date": subscription.start_date.isoformat(),
            "current_period_end": subscription.current_period_end.isoformat() if subscription.current_period_end else None,
            "trial_end_date": subscription.trial_end_date.isoformat() if subscription.trial_end_date else None,
            "auto_renew": subscription.auto_renew,
            "days_until_renewal": subscription.days_until_renewal
        }
    }


@router.get("/usage")
def get_subscription_usage(
    current_user: User = Depends(get_current_active_user),
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
):
    """Get current usage vs limits for the restaurant. Available to all authenticated users."""
    
    # Check if restaurant has an active subscription
    subscription = db.query(RestaurantSubscription).filter(
        RestaurantSubscription.restaurant_id == restaurant.id,
        RestaurantSubscription.deleted_at.is_(None),
        RestaurantSubscription.status.in_([SubscriptionStatus.TRIAL, SubscriptionStatus.ACTIVE])
    ).order_by(RestaurantSubscription.created_at.desc()).first()
    
    if not subscription:
        return {
            "has_subscription": False,
            "message": "No active subscription found. Please choose a plan to continue."
        }
    
    # Check and auto-update expiration status
    subscription.update_status(db)
    
    service = SubscriptionService(db)
    limits = service.get_subscription_limits(restaurant.id)
    
    # Get current usage
    usage = {
        "users": {
            "admin": db.query(User).filter(
                User.restaurant_id == restaurant.id,
                User.role == "admin",
                User.deleted_at.is_(None)
            ).count(),
            "waiter": db.query(User).filter(
                User.restaurant_id == restaurant.id,
                User.role == "staff",
                User.staff_type == "waiter",
                User.deleted_at.is_(None)
            ).count(),
            "cashier": db.query(User).filter(
                User.restaurant_id == restaurant.id,
                User.role == "staff",
                User.staff_type == "cashier",
                User.deleted_at.is_(None)
            ).count(),
            "kitchen": db.query(User).filter(
                User.restaurant_id == restaurant.id,
                User.role == "staff",
                User.staff_type == "kitchen",
                User.deleted_at.is_(None)
            ).count(),
        },
        "tables": db.query(Table).filter(
            Table.restaurant_id == restaurant.id,
            Table.deleted_at.is_(None)
        ).count(),
        "menu_items": db.query(MenuItem).filter(
            MenuItem.restaurant_id == restaurant.id,
            MenuItem.deleted_at.is_(None)
        ).count(),
        "categories": db.query(Category).filter(
            Category.restaurant_id == restaurant.id,
            Category.deleted_at.is_(None)
        ).count()
    }
    
    # Calculate percentages
    def calc_percentage(current: int, max_val: int) -> float:
        if max_val == -1:
            return 0  # Unlimited
        if max_val == 0:
            return 100
        return round((current / max_val) * 100, 1)
    
    return {
        "has_subscription": True,
        "limits": limits,
        "usage": usage,
        "percentages": {
            "admin_users": calc_percentage(usage["users"]["admin"], limits.get("max_admin_users", -1)),
            "waiter_users": calc_percentage(usage["users"]["waiter"], limits.get("max_waiter_users", -1)),
            "cashier_users": calc_percentage(usage["users"]["cashier"], limits.get("max_cashier_users", -1)),
            "kitchen_users": calc_percentage(usage["users"]["kitchen"], limits.get("max_kitchen_users", -1)),
            "tables": calc_percentage(usage["tables"], limits.get("max_tables", -1)),
            "menu_items": calc_percentage(usage["menu_items"], limits.get("max_menu_items", -1)),
            "categories": calc_percentage(usage["categories"], limits.get("max_categories", -1))
        }
    }


@router.get("/plans")
def get_available_plans(
    db: Session = Depends(get_db)
):
    """Get all available subscription plans"""
    service = SubscriptionService(db)
    plans = service.get_all_plans(include_trial=False)
    
    return [
        {
            "id": plan.id,
            "name": plan.display_name,
            "tier": plan.tier.value,
            "description": plan.description,
            "monthly_price": plan.monthly_price,
            "annual_price": plan.annual_price,
            "is_popular": plan.is_popular,
            "limits": {
                "max_admin_users": plan.max_admin_users,
                "max_waiter_users": plan.max_waiter_users,
                "max_cashier_users": plan.max_cashier_users,
                "max_kitchen_users": plan.max_kitchen_users,
                "max_owner_users": plan.max_owner_users,
                "max_tables": plan.max_tables,
                "max_menu_items": plan.max_menu_items,
                "max_categories": plan.max_categories
            },
            "features": {
                "has_kitchen_module": plan.has_kitchen_module,
                "has_ingredients_module": plan.has_ingredients_module,
                "has_inventory_module": plan.has_inventory_module,
                "has_advanced_reports": plan.has_advanced_reports,
                "has_multi_branch": plan.has_multi_branch,
                "has_priority_support": plan.has_priority_support
            }
        }
        for plan in plans
    ]


@router.get("/addons")
def get_available_addons(
    current_user: User = Depends(require_admin_or_sysadmin),
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
):
    """Get available add-ons for current plan. Requires admin or sysadmin privileges."""
    
    subscription = db.query(RestaurantSubscription).filter(
        RestaurantSubscription.restaurant_id == restaurant.id,
        RestaurantSubscription.deleted_at.is_(None),
        RestaurantSubscription.status.in_([SubscriptionStatus.TRIAL, SubscriptionStatus.ACTIVE])
    ).order_by(RestaurantSubscription.created_at.desc()).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )
    
    service = SubscriptionService(db)
    plan_tier = subscription.plan.tier.value
    addons = service.get_all_addons(plan_tier=plan_tier)
    
    return [
        {
            "id": addon.id,
            "code": addon.code,
            "name": addon.display_name,
            "description": addon.description,
            "type": addon.addon_type.value,
            "category": addon.category.value,
            "monthly_price": addon.monthly_price,
            "is_recurring": addon.is_recurring,
            "is_quantifiable": addon.is_quantifiable,
            "min_quantity": addon.min_quantity,
            "max_quantity": addon.max_quantity,
            "is_featured": addon.is_featured
        }
        for addon in addons
    ]


@router.post("/upgrade")
def upgrade_subscription(
    plan_id: int,
    billing_cycle: str,
    current_user: User = Depends(require_admin_or_sysadmin),
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
):
    """
    Upgrade or change subscription plan for the restaurant.
    Creates new subscription if none exists.
    Validates downgrade limits before allowing the change.
    Requires admin or sysadmin privileges.
    """
    from app.services.subscription_service import SubscriptionService
    from app.core.exceptions import ValidationError, ResourceNotFoundError
    
    # Validate billing cycle
    if billing_cycle not in ['monthly', 'annual']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid billing cycle. Must be 'monthly' or 'annual'"
        )
    
    service = SubscriptionService(db)
    
    # Get ALL active/trial subscriptions for this restaurant
    existing_subscriptions = db.query(RestaurantSubscription).filter(
        RestaurantSubscription.restaurant_id == restaurant.id,
        RestaurantSubscription.status.in_([SubscriptionStatus.TRIAL, SubscriptionStatus.ACTIVE])
    ).all()
    
    try:
        if existing_subscriptions:
            # Use the most recent subscription
            existing_subscription = max(existing_subscriptions, key=lambda s: s.created_at)
            
            # Cancel all other subscriptions to avoid duplicates
            from datetime import datetime
            for sub in existing_subscriptions:
                if sub.id != existing_subscription.id:
                    sub.status = SubscriptionStatus.CANCELLED
                    sub.cancelled_at = datetime.utcnow()
            db.commit()
            # Use the service method which includes downgrade validation
            subscription = service.upgrade_subscription(
                existing_subscription.id,
                plan_id
            )
            
            # Update billing cycle if changed
            if subscription.billing_cycle != billing_cycle:
                subscription.billing_cycle = billing_cycle
                # Recalculate price
                new_plan = subscription.plan
                if billing_cycle == 'annual' and new_plan.annual_price:
                    subscription.base_price = new_plan.annual_price
                else:
                    subscription.base_price = new_plan.monthly_price
                subscription.total_price = subscription.calculate_total_cost()
                db.commit()
                db.refresh(subscription)
        else:
            # Create new subscription
            subscription = service.create_paid_subscription(
                restaurant_id=restaurant.id,
                plan_id=plan_id,
                billing_cycle=billing_cycle
            )
        
        return {
            "success": True,
            "message": "Suscripción actualizada exitosamente",
            "subscription": {
                "id": subscription.id,
                "plan_name": subscription.plan.display_name,
                "status": subscription.status.value,
                "billing_cycle": subscription.billing_cycle,
                "price": subscription.total_price,
                "current_period_end": subscription.current_period_end.isoformat()
            }
        }
    except ValidationError as e:
        # Return validation error with details (e.g., downgrade limits exceeded)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ResourceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/status")
def check_subscription_status(
    current_user: User = Depends(get_current_active_user),
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
):
    """
    Check if restaurant's subscription is active.
    Returns status information including whether operations are allowed.
    """
    from datetime import datetime
    
    # Get restaurant's most recent active or trial subscription
    subscription = db.query(RestaurantSubscription).filter(
        RestaurantSubscription.restaurant_id == restaurant.id,
        RestaurantSubscription.deleted_at.is_(None),
        RestaurantSubscription.status.in_([SubscriptionStatus.TRIAL, SubscriptionStatus.ACTIVE])
    ).order_by(RestaurantSubscription.created_at.desc()).first()
    
    # No subscription found
    if not subscription:
        return {
            "is_active": False,
            "status": "no_subscription",
            "message": "No se encontró una suscripción activa. Por favor contacta al administrador.",
            "can_operate": False,
            "days_remaining": 0
        }
    
    # Check and auto-update expiration status
    subscription.update_status(db)
    
    # Use the can_operate property for consistent logic
    can_operate = subscription.can_operate
    is_expired = subscription.is_expired
    
    # Debug logging
    print(f"[STATUS ENDPOINT] Subscription ID: {subscription.id}")
    print(f"[STATUS ENDPOINT] Status: {subscription.status}")
    print(f"[STATUS ENDPOINT] Can operate: {can_operate}")
    print(f"[STATUS ENDPOINT] Is expired: {is_expired}")
    print(f"[STATUS ENDPOINT] Current period end: {subscription.current_period_end}")
    print(f"[STATUS ENDPOINT] Days until renewal: {subscription.days_until_renewal}")
    
    # If cannot operate, provide specific error message
    if not can_operate:
        if subscription.status == SubscriptionStatus.EXPIRED:
            message = "Tu suscripción ha expirado. Por favor renueva tu plan para continuar."
            status_str = "expired"
        elif subscription.status == SubscriptionStatus.CANCELLED:
            message = "Tu suscripción ha sido cancelada. Por favor contacta al administrador."
            status_str = "cancelled"
        elif subscription.status == SubscriptionStatus.TRIAL and subscription.is_trial_expired:
            message = "Tu período de prueba ha expirado. Por favor elige un plan de pago."
            status_str = "trial_expired"
        elif subscription.status == SubscriptionStatus.PAST_DUE:
            message = "Tu suscripción tiene pagos pendientes. Por favor actualiza tu método de pago."
            status_str = "past_due"
        elif subscription.status == SubscriptionStatus.PENDING_PAYMENT:
            message = "Tu pago está en revisión. Podrás operar una vez que sea aprobado."
            status_str = "pending_payment"
        elif subscription.status == SubscriptionStatus.ACTIVE:
            message = "Tu suscripción ha vencido. Por favor renueva tu plan."
            status_str = "period_ended"
        else:
            message = "Tu suscripción no está activa. Por favor contacta al administrador."
            status_str = subscription.status.value
        
        return {
            "is_active": False,
            "status": status_str,
            "message": message,
            "can_operate": False,
            "days_remaining": 0
        }
    
    # Subscription is active and can operate
    days_remaining = subscription.days_until_renewal
    if subscription.status == SubscriptionStatus.TRIAL:
        days_remaining = subscription.trial_days_remaining
    
    return {
        "is_active": True,
        "status": subscription.status.value,
        "message": "Suscripción activa",
        "can_operate": True,
        "days_remaining": days_remaining,
        "plan_name": subscription.plan.display_name
    }


# ============================================================================
# PAYMENT ENDPOINTS
# ============================================================================

@router.post("/request-renewal", response_model=RenewalResponse)
def request_renewal(
    request: RenewalRequest,
    current_user: User = Depends(require_admin_or_sysadmin),
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
):
    """Request subscription renewal - generates payment instructions"""
    # Get current subscription
    subscription = db.query(RestaurantSubscription).filter(
        RestaurantSubscription.restaurant_id == restaurant.id,
        RestaurantSubscription.deleted_at.is_(None)
    ).order_by(RestaurantSubscription.created_at.desc()).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No subscription found"
        )
    
    # Get plan details
    plan = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.id == request.plan_id
    ).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    
    # Calculate amount
    if request.billing_cycle == "monthly":
        amount = plan.monthly_price
    else:
        amount = plan.annual_price
    
    # Create payment request
    payment_service = PaymentService(db)
    payment = payment_service.create_renewal_request(
        restaurant_id=restaurant.id,
        subscription_id=subscription.id,
        plan_id=request.plan_id,
        billing_cycle=request.billing_cycle,
        amount=amount
    )
    
    # Bank details (TODO: move to config)
    bank_details = {
        "bank": "Banorte",
        "clabe": "072778011569810433",
    }
    
    instructions = f"""
Realiza una transferencia bancaria con los siguientes datos:

Banco: {bank_details['bank']}
CLABE: {bank_details['clabe']}

IMPORTANTE: Incluye el número de referencia en tu transferencia.
Número de Referencia: {payment.reference_number}

Una vez realizada la transferencia, sube tu comprobante de pago.
"""
    
    return RenewalResponse(
        payment_id=payment.id,
        reference_number=payment.reference_number,
        amount=amount,
        instructions=instructions,
        bank_details=bank_details
    )


@router.post("/submit-payment/{payment_id}", response_model=PaymentResponse)
def submit_payment(
    payment_id: int,
    data: PaymentSubmit,
    current_user: User = Depends(require_admin_or_sysadmin),
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
):
    """Submit payment proof for review"""
    payment_service = PaymentService(db)
    
    # Verify payment belongs to restaurant
    payment = payment_service.get_payment_by_id(payment_id)
    if not payment or payment.restaurant_id != restaurant.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    try:
        payment = payment_service.submit_payment_proof(
            payment_id=payment_id,
            payment_date=data.payment_date,
            proof_url=data.proof_image_url,
            notes=data.notes
        )
        
        return PaymentResponse(
            id=payment.id,
            restaurant_id=payment.restaurant_id,
            subscription_id=payment.subscription_id,
            plan_id=payment.plan_id,
            amount=payment.amount,
            billing_cycle=payment.billing_cycle,
            payment_method=payment.payment_method,
            reference_number=payment.reference_number,
            payment_date=payment.payment_date,
            proof_image_url=payment.proof_image_url,
            notes=payment.notes,
            status=payment.status,
            reviewed_by=payment.reviewed_by,
            reviewed_at=payment.reviewed_at,
            rejection_reason=payment.rejection_reason,
            created_at=payment.created_at,
            updated_at=payment.updated_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/payment-status/{payment_id}", response_model=PaymentResponse)
def get_payment_status(
    payment_id: int,
    current_user: User = Depends(require_admin_or_sysadmin),
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
):
    """Get payment status"""
    payment_service = PaymentService(db)
    payment = payment_service.get_payment_by_id(payment_id)
    
    if not payment or payment.restaurant_id != restaurant.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    return PaymentResponse(
        id=payment.id,
        restaurant_id=payment.restaurant_id,
        subscription_id=payment.subscription_id,
        plan_id=payment.plan_id,
        amount=payment.amount,
        billing_cycle=payment.billing_cycle,
        payment_method=payment.payment_method,
        reference_number=payment.reference_number,
        payment_date=payment.payment_date,
        proof_image_url=payment.proof_image_url,
        notes=payment.notes,
        status=payment.status,
        reviewed_by=payment.reviewed_by,
        reviewed_at=payment.reviewed_at,
        rejection_reason=payment.rejection_reason,
        created_at=payment.created_at,
        updated_at=payment.updated_at
    )


# ============================================================================
# ALERT ENDPOINTS
# ============================================================================

@router.get("/alerts", response_model=list[AlertResponse])
def get_alerts(
    unread_only: bool = False,
    current_user: User = Depends(require_admin_or_sysadmin),
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
):
    """Get subscription alerts for restaurant"""
    alert_service = AlertService(db)
    alerts = alert_service.get_restaurant_alerts(restaurant.id, unread_only)
    
    return [
        AlertResponse(
            id=alert.id,
            restaurant_id=alert.restaurant_id,
            subscription_id=alert.subscription_id,
            alert_type=alert.alert_type,
            title=alert.title,
            message=alert.message,
            is_read=alert.is_read,
            read_at=alert.read_at,
            created_at=alert.created_at
        )
        for alert in alerts
    ]


@router.post("/alerts/mark-read")
def mark_alerts_read(
    data: AlertMarkRead,
    current_user: User = Depends(require_admin_or_sysadmin),
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
):
    """Mark alerts as read"""
    alert_service = AlertService(db)
    alert_service.mark_as_read(data.alert_ids, restaurant.id)
    
    return {"message": "Alerts marked as read"}
