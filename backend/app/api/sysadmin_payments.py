"""
SysAdmin endpoints for payment management.
Allows sysadmin to approve/reject subscription payments.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.base import get_db
from app.models import User, Restaurant, SubscriptionPlan
from app.services.payment_service import PaymentService
from app.api.deps import require_sysadmin
from app.schemas.payment import PaymentResponse, PaymentReject

router = APIRouter(prefix="/sysadmin/payments", tags=["sysadmin-payments"])


@router.get("/pending", response_model=List[PaymentResponse])
def get_pending_payments(
    current_user: User = Depends(require_sysadmin),
    db: Session = Depends(get_db)
):
    """Get all pending payments for review"""
    payment_service = PaymentService(db)
    payments = payment_service.get_pending_payments()
    
    result = []
    for payment in payments:
        # Get restaurant and plan names
        restaurant = db.query(Restaurant).filter(Restaurant.id == payment.restaurant_id).first()
        plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == payment.plan_id).first()
        
        result.append(PaymentResponse(
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
            updated_at=payment.updated_at,
            restaurant_name=restaurant.name if restaurant else None,
            plan_name=plan.display_name if plan else None
        ))
    
    return result


@router.post("/{payment_id}/approve", response_model=PaymentResponse)
def approve_payment(
    payment_id: int,
    current_user: User = Depends(require_sysadmin),
    db: Session = Depends(get_db)
):
    """Approve a payment and activate subscription"""
    payment_service = PaymentService(db)
    
    try:
        payment = payment_service.approve_payment(payment_id, current_user.id)
        
        # Get restaurant and plan names
        restaurant = db.query(Restaurant).filter(Restaurant.id == payment.restaurant_id).first()
        plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == payment.plan_id).first()
        
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
            updated_at=payment.updated_at,
            restaurant_name=restaurant.name if restaurant else None,
            plan_name=plan.display_name if plan else None,
            reviewer_name=current_user.full_name
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{payment_id}/reject", response_model=PaymentResponse)
def reject_payment(
    payment_id: int,
    data: PaymentReject,
    current_user: User = Depends(require_sysadmin),
    db: Session = Depends(get_db)
):
    """Reject a payment"""
    payment_service = PaymentService(db)
    
    try:
        payment = payment_service.reject_payment(payment_id, current_user.id, data.reason)
        
        # Get restaurant and plan names
        restaurant = db.query(Restaurant).filter(Restaurant.id == payment.restaurant_id).first()
        plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == payment.plan_id).first()
        
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
            updated_at=payment.updated_at,
            restaurant_name=restaurant.name if restaurant else None,
            plan_name=plan.display_name if plan else None,
            reviewer_name=current_user.full_name
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
