"""
Subscription service for managing restaurant subscriptions.
Handles automatic cost calculations, upgrades, downgrades, and limit enforcement.
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models import (
    Restaurant,
    SubscriptionPlan, PlanTier,
    SubscriptionAddon, AddonType,
    RestaurantSubscription, SubscriptionStatus, BillingCycle,
    RestaurantAddon
)
from app.core.exceptions import ResourceNotFoundError, ValidationError, ConflictError


class SubscriptionService:
    """Service for managing restaurant subscriptions"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ==================== PLAN MANAGEMENT ====================
    
    def get_all_plans(self, include_trial: bool = True) -> List[SubscriptionPlan]:
        """Get all active subscription plans"""
        query = self.db.query(SubscriptionPlan).filter(SubscriptionPlan.is_active == True)
        
        if not include_trial:
            query = query.filter(SubscriptionPlan.is_trial == False)
        
        return query.order_by(SubscriptionPlan.sort_order).all()
    
    def get_plan_by_tier(self, tier: PlanTier) -> Optional[SubscriptionPlan]:
        """Get plan by tier"""
        return self.db.query(SubscriptionPlan).filter(
            SubscriptionPlan.tier == tier,
            SubscriptionPlan.is_active == True
        ).first()
    
    def get_plan_by_id(self, plan_id: int) -> SubscriptionPlan:
        """Get plan by ID"""
        plan = self.db.query(SubscriptionPlan).filter(SubscriptionPlan.id == plan_id).first()
        if not plan:
            raise ResourceNotFoundError("SubscriptionPlan", plan_id)
        return plan
    
    # ==================== ADDON MANAGEMENT ====================
    
    def get_all_addons(self, plan_tier: Optional[str] = None) -> List[SubscriptionAddon]:
        """Get all active addons, optionally filtered by plan availability"""
        addons = self.db.query(SubscriptionAddon).filter(
            SubscriptionAddon.is_active == True
        ).order_by(SubscriptionAddon.sort_order).all()
        
        if plan_tier:
            # Filter addons available for this plan
            return [addon for addon in addons if addon.is_available_for_plan(plan_tier)]
        
        return addons
    
    def get_addon_by_code(self, code: str) -> SubscriptionAddon:
        """Get addon by code"""
        addon = self.db.query(SubscriptionAddon).filter(
            SubscriptionAddon.code == code,
            SubscriptionAddon.is_active == True
        ).first()
        if not addon:
            raise ResourceNotFoundError("SubscriptionAddon", code)
        return addon
    
    # ==================== SUBSCRIPTION QUERIES ====================
    
    def get_restaurant_subscription(self, restaurant_id: int) -> Optional[RestaurantSubscription]:
        """Get active or trial subscription for a restaurant"""
        return self.db.query(RestaurantSubscription).filter(
            RestaurantSubscription.restaurant_id == restaurant_id,
            RestaurantSubscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIAL])
        ).first()
    
    # ==================== SUBSCRIPTION CREATION ====================
    
    def create_trial_subscription(self, restaurant_id: int, trial_days: int = 14) -> RestaurantSubscription:
        """Create a trial subscription for a new restaurant
        
        Args:
            restaurant_id: ID of the restaurant
            trial_days: Number of trial days (14, 30, or 60)
        """
        # Check if restaurant already has a subscription
        existing = self.db.query(RestaurantSubscription).filter(
            RestaurantSubscription.restaurant_id == restaurant_id
        ).first()
        
        if existing:
            raise ConflictError("Restaurant already has a subscription")
        
        # Get trial plan
        trial_plan = self.get_plan_by_tier(PlanTier.TRIAL)
        if not trial_plan:
            raise ValidationError("Trial plan not found in system")
        
        # Calculate dates using custom trial_days
        now = datetime.utcnow()
        trial_end = now + timedelta(days=trial_days)
        
        # Create subscription
        subscription = RestaurantSubscription(
            restaurant_id=restaurant_id,
            plan_id=trial_plan.id,
            status=SubscriptionStatus.TRIAL,
            billing_cycle=BillingCycle.MONTHLY,
            start_date=now,
            trial_end_date=trial_end,
            current_period_start=now,
            current_period_end=trial_end,
            base_price=0.0,
            total_price=0.0,
            auto_renew=True
        )
        
        self.db.add(subscription)
        self.db.commit()
        self.db.refresh(subscription)
        
        return subscription
    
    def create_paid_subscription(
        self,
        restaurant_id: int,
        plan_id: int,
        billing_cycle: BillingCycle = BillingCycle.MONTHLY,
        discount_code: Optional[str] = None
    ) -> RestaurantSubscription:
        """Create a paid subscription"""
        # Get plan
        plan = self.get_plan_by_id(plan_id)
        
        # Calculate price based on billing cycle
        if billing_cycle == BillingCycle.ANNUAL and plan.annual_price:
            base_price = plan.annual_price
        else:
            base_price = plan.monthly_price
        
        # Calculate dates
        now = datetime.utcnow()
        if billing_cycle == BillingCycle.MONTHLY:
            period_end = now + timedelta(days=30)
        else:
            period_end = now + timedelta(days=365)
        
        # Create subscription
        subscription = RestaurantSubscription(
            restaurant_id=restaurant_id,
            plan_id=plan_id,
            status=SubscriptionStatus.ACTIVE,
            billing_cycle=billing_cycle,
            start_date=now,
            trial_end_date=None,
            current_period_start=now,
            current_period_end=period_end,
            base_price=base_price,
            total_price=base_price,
            discount_code=discount_code,
            auto_renew=True
        )
        
        # Apply discount if provided
        if discount_code:
            subscription = self._apply_discount(subscription, discount_code)
        
        self.db.add(subscription)
        self.db.commit()
        self.db.refresh(subscription)
        
        return subscription
    
    # ==================== SUBSCRIPTION UPDATES ====================
    
    def _validate_plan_limits(
        self,
        restaurant_id: int,
        new_plan: SubscriptionPlan
    ) -> List[str]:
        """
        Validate current usage against plan limits.
        Returns list of violation messages.
        
        Args:
            restaurant_id: ID of the restaurant to validate
            new_plan: The plan to validate against
            
        Returns:
            List of violation messages (empty if no violations)
        """
        from app.models import User, Table, MenuItem, Category
        
        violations = []
        
        # Check tables
        current_tables = self.db.query(Table).filter(
            Table.restaurant_id == restaurant_id,
            Table.deleted_at.is_(None)
        ).count()
        if new_plan.max_tables != -1 and current_tables > new_plan.max_tables:
            violations.append(
                f"Tienes {current_tables} mesas pero el plan {new_plan.display_name} "
                f"solo permite {new_plan.max_tables}"
            )
        
        # Check menu items
        current_items = self.db.query(MenuItem).filter(
            MenuItem.restaurant_id == restaurant_id,
            MenuItem.deleted_at.is_(None)
        ).count()
        if new_plan.max_menu_items != -1 and current_items > new_plan.max_menu_items:
            violations.append(
                f"Tienes {current_items} productos pero el plan {new_plan.display_name} "
                f"solo permite {new_plan.max_menu_items}"
            )
        
        # Check categories
        current_categories = self.db.query(Category).filter(
            Category.restaurant_id == restaurant_id,
            Category.deleted_at.is_(None)
        ).count()
        if new_plan.max_categories != -1 and current_categories > new_plan.max_categories:
            violations.append(
                f"Tienes {current_categories} categorías pero el plan {new_plan.display_name} "
                f"solo permite {new_plan.max_categories}"
            )
        
        # Check users by role
        role_limits = {
            'admin': ('max_admin_users', 'administradores'),
            'waiter': ('max_waiter_users', 'meseros'),
            'cashier': ('max_cashier_users', 'cajeros'),
            'kitchen': ('max_kitchen_users', 'usuarios de cocina'),
            'owner': ('max_owner_users', 'dueños')
        }
        
        for role, (limit_key, role_name) in role_limits.items():
            current_users = self.db.query(User).filter(
                User.restaurant_id == restaurant_id,
                User.role == role,
                User.deleted_at.is_(None)
            ).count()
            max_allowed = getattr(new_plan, limit_key, -1)
            if max_allowed != -1 and current_users > max_allowed:
                violations.append(
                    f"Tienes {current_users} {role_name} pero el plan {new_plan.display_name} "
                    f"solo permite {max_allowed}"
                )
        
        return violations
    
    def upgrade_subscription(
        self,
        subscription_id: int,
        new_plan_id: int
    ) -> RestaurantSubscription:
        """Change subscription plan (upgrade or downgrade with validation)"""
        subscription = self.db.query(RestaurantSubscription).filter(
            RestaurantSubscription.id == subscription_id
        ).first()
        
        if not subscription:
            raise ResourceNotFoundError("RestaurantSubscription", subscription_id)
        
        new_plan = self.get_plan_by_id(new_plan_id)
        old_plan = subscription.plan
        
        # Determine if it's an upgrade or downgrade
        tier_order = ["trial", "starter", "basic", "pro", "business", "enterprise"]
        old_tier_index = tier_order.index(old_plan.tier.value)
        new_tier_index = tier_order.index(new_plan.tier.value)
        
        is_downgrade = new_tier_index < old_tier_index
        
        # If downgrade, validate current usage
        if is_downgrade:
            violations = self._validate_plan_limits(subscription.restaurant_id, new_plan)
            
            # If there are violations, raise error with details
            if violations:
                error_msg = "No puedes cambiar a este plan porque excedes los siguientes límites:\n" + "\n".join(f"• {v}" for v in violations)
                error_msg += "\n\nPor favor elimina algunos recursos antes de cambiar de plan."
                raise ValidationError(error_msg)
        
        # Update subscription
        subscription.plan_id = new_plan_id
        
        # Recalculate price
        if subscription.billing_cycle == BillingCycle.ANNUAL and new_plan.annual_price:
            subscription.base_price = new_plan.annual_price
        else:
            subscription.base_price = new_plan.monthly_price
        
        subscription.total_price = subscription.calculate_total_cost()
        
        # If was trial, change to active
        if subscription.status == SubscriptionStatus.TRIAL:
            subscription.status = SubscriptionStatus.ACTIVE
            subscription.trial_end_date = None
        
        self.db.commit()
        self.db.refresh(subscription)
        
        return subscription
    
    def downgrade_subscription(
        self,
        subscription_id: int,
        new_plan_id: int
    ) -> RestaurantSubscription:
        """Downgrade subscription to a lower tier (effective at end of current period)"""
        subscription = self.db.query(RestaurantSubscription).filter(
            RestaurantSubscription.id == subscription_id
        ).first()
        
        if not subscription:
            raise ResourceNotFoundError("RestaurantSubscription", subscription_id)
        
        new_plan = self.get_plan_by_id(new_plan_id)
        
        # Validate current usage against new plan limits
        violations = self._validate_plan_limits(subscription.restaurant_id, new_plan)
        
        # If there are violations, raise error with details
        if violations:
            error_msg = "No puedes cambiar a este plan porque excedes los siguientes límites:\n" + "\n".join(f"• {v}" for v in violations)
            error_msg += "\n\nPor favor elimina algunos recursos antes de cambiar de plan."
            raise ValidationError(error_msg)
        
        # Store downgrade info in metadata for processing at period end
        if not subscription.subscription_metadata:
            subscription.subscription_metadata = {}
        
        subscription.subscription_metadata['pending_downgrade'] = {
            'new_plan_id': new_plan_id,
            'scheduled_date': subscription.current_period_end.isoformat()
        }
        
        self.db.commit()
        self.db.refresh(subscription)
        
        return subscription
    
    def cancel_subscription(self, subscription_id: int, immediate: bool = False) -> RestaurantSubscription:
        """Cancel subscription"""
        subscription = self.db.query(RestaurantSubscription).filter(
            RestaurantSubscription.id == subscription_id
        ).first()
        
        if not subscription:
            raise ResourceNotFoundError("RestaurantSubscription", subscription_id)
        
        if immediate:
            subscription.status = SubscriptionStatus.CANCELLED
            subscription.cancelled_at = datetime.utcnow()
            subscription.current_period_end = datetime.utcnow()
        else:
            # Cancel at end of period
            subscription.auto_renew = False
            subscription.cancelled_at = datetime.utcnow()
            if not subscription.subscription_metadata:
                subscription.subscription_metadata = {}
            subscription.subscription_metadata['cancel_at_period_end'] = True
        
        self.db.commit()
        self.db.refresh(subscription)
        
        return subscription
    
    # ==================== ADDON MANAGEMENT ====================
    
    def add_addon_to_subscription(
        self,
        subscription_id: int,
        addon_code: str,
        quantity: int = 1
    ) -> RestaurantAddon:
        """Add an addon to a subscription"""
        subscription = self.db.query(RestaurantSubscription).filter(
            RestaurantSubscription.id == subscription_id
        ).first()
        
        if not subscription:
            raise ResourceNotFoundError("RestaurantSubscription", subscription_id)
        
        addon = self.get_addon_by_code(addon_code)
        
        # Validate addon is available for this plan
        if not addon.is_available_for_plan(subscription.plan.tier.value):
            raise ValidationError(f"Addon '{addon_code}' is not available for plan '{subscription.plan.tier.value}'")
        
        # Validate quantity
        if quantity < addon.min_quantity:
            raise ValidationError(f"Minimum quantity for this addon is {addon.min_quantity}")
        
        if addon.max_quantity and quantity > addon.max_quantity:
            raise ValidationError(f"Maximum quantity for this addon is {addon.max_quantity}")
        
        # Check if addon already exists
        existing = self.db.query(RestaurantAddon).filter(
            RestaurantAddon.subscription_id == subscription_id,
            RestaurantAddon.addon_id == addon.id
        ).first()
        
        if existing:
            # Update quantity
            existing.quantity = quantity
            existing.update_total_price()
            restaurant_addon = existing
        else:
            # Create new addon
            restaurant_addon = RestaurantAddon(
                subscription_id=subscription_id,
                addon_id=addon.id,
                quantity=quantity,
                unit_price=addon.monthly_price,
                total_price=addon.monthly_price * quantity,
                is_active=True
            )
            self.db.add(restaurant_addon)
        
        # Recalculate subscription total
        subscription.total_price = subscription.calculate_total_cost()
        
        self.db.commit()
        self.db.refresh(restaurant_addon)
        
        return restaurant_addon
    
    def remove_addon_from_subscription(
        self,
        subscription_id: int,
        addon_code: str
    ) -> None:
        """Remove an addon from a subscription"""
        addon = self.get_addon_by_code(addon_code)
        
        restaurant_addon = self.db.query(RestaurantAddon).filter(
            RestaurantAddon.subscription_id == subscription_id,
            RestaurantAddon.addon_id == addon.id
        ).first()
        
        if not restaurant_addon:
            raise ResourceNotFoundError("RestaurantAddon", f"{subscription_id}/{addon_code}")
        
        self.db.delete(restaurant_addon)
        
        # Recalculate subscription total
        subscription = self.db.query(RestaurantSubscription).filter(
            RestaurantSubscription.id == subscription_id
        ).first()
        
        if subscription:
            subscription.total_price = subscription.calculate_total_cost()
        
        self.db.commit()
    
    # ==================== LIMIT CHECKING ====================
    
    def get_subscription_limits(self, restaurant_id: int) -> Dict[str, Any]:
        """Get all limits for a restaurant's subscription"""
        subscription = self.db.query(RestaurantSubscription).filter(
            RestaurantSubscription.restaurant_id == restaurant_id,
            RestaurantSubscription.status.in_([SubscriptionStatus.TRIAL, SubscriptionStatus.ACTIVE])
        ).first()
        
        if not subscription:
            # Return default trial limits if no subscription
            trial_plan = self.get_plan_by_tier(PlanTier.TRIAL)
            if trial_plan:
                return {
                    'max_admin_users': trial_plan.max_admin_users,
                    'max_waiter_users': trial_plan.max_waiter_users,
                    'max_cashier_users': trial_plan.max_cashier_users,
                    'max_kitchen_users': trial_plan.max_kitchen_users,
                    'max_owner_users': trial_plan.max_owner_users,
                    'max_tables': trial_plan.max_tables,
                    'max_menu_items': trial_plan.max_menu_items,
                    'max_categories': trial_plan.max_categories,
                    'has_kitchen_module': trial_plan.has_kitchen_module,
                    'has_ingredients_module': trial_plan.has_ingredients_module,
                    'has_inventory_module': trial_plan.has_inventory_module,
                    'has_advanced_reports': trial_plan.has_advanced_reports,
                    'has_multi_branch': trial_plan.has_multi_branch,
                    'report_retention_days': trial_plan.report_retention_days,
                }
            return {}
        
        return subscription.get_limits()
    
    def check_limit(
        self,
        restaurant_id: int,
        limit_type: str,
        current_count: int
    ) -> bool:
        """Check if a limit has been reached"""
        limits = self.get_subscription_limits(restaurant_id)
        
        if limit_type not in limits:
            return True  # No limit defined, allow
        
        limit_value = limits[limit_type]
        
        # For boolean features
        if isinstance(limit_value, bool):
            return limit_value
        
        # For numeric limits (-1 means unlimited)
        if limit_value == -1:
            return True
        
        return current_count < limit_value
    
    # ==================== COST CALCULATION ====================
    
    def calculate_subscription_cost(
        self,
        plan_id: int,
        billing_cycle: BillingCycle,
        addon_codes: Optional[List[Dict[str, Any]]] = None,
        discount_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate total subscription cost.
        
        Args:
            plan_id: ID of the subscription plan
            billing_cycle: Monthly or annual
            addon_codes: List of dicts with 'code' and 'quantity' keys
            discount_code: Optional discount code
        
        Returns:
            Dict with cost breakdown
        """
        plan = self.get_plan_by_id(plan_id)
        
        # Base price
        if billing_cycle == BillingCycle.ANNUAL and plan.annual_price:
            base_price = plan.annual_price
            billing_period = "annual"
        else:
            base_price = plan.monthly_price
            billing_period = "monthly"
        
        # Addon costs
        addon_details = []
        addon_total = 0.0
        
        if addon_codes:
            for addon_info in addon_codes:
                addon = self.get_addon_by_code(addon_info['code'])
                quantity = addon_info.get('quantity', 1)
                
                addon_cost = addon.monthly_price * quantity
                addon_total += addon_cost
                
                addon_details.append({
                    'code': addon.code,
                    'name': addon.display_name,
                    'quantity': quantity,
                    'unit_price': addon.monthly_price,
                    'total': addon_cost
                })
        
        # Subtotal
        subtotal = base_price + addon_total
        
        # Apply discount
        discount_amount = 0.0
        discount_percentage = 0.0
        
        if discount_code:
            # TODO: Implement discount code logic
            pass
        
        # Total
        total = subtotal - discount_amount
        
        return {
            'plan': {
                'id': plan.id,
                'name': plan.display_name,
                'tier': plan.tier.value,
                'price': base_price,
                'billing_period': billing_period
            },
            'addons': addon_details,
            'subtotal': round(subtotal, 2),
            'discount': {
                'code': discount_code,
                'percentage': discount_percentage,
                'amount': round(discount_amount, 2)
            },
            'total': round(total, 2),
            'currency': 'MXN'
        }
    
    # ==================== PRIVATE METHODS ====================
    
    def _apply_discount(
        self,
        subscription: RestaurantSubscription,
        discount_code: str
    ) -> RestaurantSubscription:
        """Apply discount code to subscription"""
        # TODO: Implement discount code validation and application
        # For now, just store the code
        subscription.discount_code = discount_code
        return subscription
