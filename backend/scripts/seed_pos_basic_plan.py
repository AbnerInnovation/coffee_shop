"""
Seed script to create POS Basic subscription plan

This script creates a new subscription plan specifically designed for
POS-only businesses like churrerías, paleterías, etc.

Usage:
    python -m scripts.seed_pos_basic_plan
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.db.base import SessionLocal
from app.models.subscription_plan import SubscriptionPlan, PlanTier
from app.core.operation_modes import OperationMode


def create_pos_basic_plan(db: Session):
    """Create POS Basic subscription plan"""
    
    # Check if plan already exists
    existing_plan = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.name == "pos_basic"
    ).first()
    
    if existing_plan:
        print("✓ POS Básico plan already exists")
        return existing_plan
    
    # Create POS Basic plan
    pos_basic_plan = SubscriptionPlan(
        name="pos_basic",
        tier=PlanTier.POS_BASIC,
        display_name="POS Básico",
        description="Plan diseñado para negocios de venta directa como churrerías, paleterías, cafeterías pequeñas. Sin mesas ni cocina digital.",
        
        # Pricing
        monthly_price=699.0,
        annual_price=6990.0,  # 2 months free (16.6% discount)
        
        # Operation mode
        operation_mode=OperationMode.POS_ONLY,
        
        # User limits (only cashiers needed)
        max_admin_users=1,
        max_waiter_users=0,      # No waiters in POS mode
        max_cashier_users=2,     # 2 cashiers for shifts
        max_kitchen_users=0,     # No kitchen module
        max_owner_users=0,
        
        # Resource limits
        max_tables=0,            # No tables in POS mode
        max_menu_items=100,      # Sufficient for most POS businesses
        max_categories=15,
        
        # Feature flags
        has_kitchen_module=False,
        has_ingredients_module=False,
        has_inventory_module=False,  # Can be added as addon
        has_advanced_reports=False,  # Basic reports only
        has_multi_branch=False,
        has_priority_support=False,
        
        # Report retention
        report_retention_days=30,
        
        # Support
        support_hours_monthly=2.0,
        
        # Display settings
        is_trial=False,
        is_popular=False,
        is_active=True,
        sort_order=15  # After Starter, before Basic
    )
    
    db.add(pos_basic_plan)
    db.commit()
    db.refresh(pos_basic_plan)
    
    print(f"✓ Created POS Básico plan (ID: {pos_basic_plan.id})")
    print(f"  - Monthly price: ${pos_basic_plan.monthly_price}")
    print(f"  - Annual price: ${pos_basic_plan.annual_price}")
    print(f"  - Operation mode: {pos_basic_plan.operation_mode.value}")
    print(f"  - Max cashiers: {pos_basic_plan.max_cashier_users}")
    print(f"  - Max menu items: {pos_basic_plan.max_menu_items}")
    
    return pos_basic_plan


def update_existing_plans_operation_mode(db: Session):
    """Update existing plans to have operation_mode set"""
    
    # Map plan tiers to operation modes
    tier_mode_map = {
        PlanTier.TRIAL: OperationMode.FULL_RESTAURANT,
        PlanTier.STARTER: OperationMode.FULL_RESTAURANT,
        PlanTier.BASIC: OperationMode.FULL_RESTAURANT,
        PlanTier.PRO: OperationMode.FULL_RESTAURANT,
        PlanTier.BUSINESS: OperationMode.FULL_RESTAURANT,
        PlanTier.ENTERPRISE: OperationMode.FULL_RESTAURANT,
    }
    
    updated_count = 0
    
    for tier, mode in tier_mode_map.items():
        plans = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.tier == tier
        ).all()
        
        for plan in plans:
            if not hasattr(plan, 'operation_mode') or plan.operation_mode is None:
                plan.operation_mode = mode
                updated_count += 1
    
    if updated_count > 0:
        db.commit()
        print(f"✓ Updated {updated_count} existing plans with operation_mode")
    else:
        print("✓ All existing plans already have operation_mode set")


def main():
    """Main execution function"""
    print("=" * 60)
    print("Seeding POS Basic Subscription Plan")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Update existing plans first
        print("\n1. Updating existing plans...")
        update_existing_plans_operation_mode(db)
        
        # Create POS Basic plan
        print("\n2. Creating POS Básico plan...")
        create_pos_basic_plan(db)
        
        print("\n" + "=" * 60)
        print("✓ Seed completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error during seed: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
