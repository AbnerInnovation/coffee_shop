"""
Tests for Subscription Limit Validator

These tests ensure that user counting works correctly with the role/staff_type structure:
- Admin users: role='admin'
- Staff users: role='staff' + staff_type in ['waiter', 'cashier', 'kitchen']
- Owner users: role='owner'
"""

import pytest
from datetime import datetime, timezone

from app.services.subscription.limit_validator import (
    get_current_usage,
    validate_plan_limits,
    check_resource_limit,
    can_add_resource,
)
from app.models import User, Table, MenuItem, Category, SubscriptionPlan, PlanTier


class TestGetCurrentUsage:
    """Test suite for get_current_usage function"""
    
    def test_counts_admin_users_correctly(self, db_session, sample_restaurant):
        """Test that admin users are counted by role='admin'"""
        # Arrange - Create 2 admin users
        for i in range(2):
            user = User(
                email=f"admin{i}@test.com",
                hashed_password="hashed",
                full_name=f"Admin User {i}",  # Required field
                role="admin",
                restaurant_id=sample_restaurant.id
            )
            db_session.add(user)
        db_session.commit()
        
        # Act
        usage = get_current_usage(db_session, sample_restaurant.id)
        
        # Assert
        assert usage['users_admin'] == 2
    
    def test_counts_staff_users_by_staff_type(self, db_session, sample_restaurant):
        """Test that staff users are counted by staff_type, not role"""
        # Arrange - Create staff users with different types
        staff_data = [
            ('waiter', 3),
            ('cashier', 2),
            ('kitchen', 1),
        ]
        
        for staff_type, count in staff_data:
            for i in range(count):
                user = User(
                    email=f"{staff_type}{i}@test.com",
                    hashed_password="hashed",
                    full_name=f"{staff_type.title()} User {i}",  # Required field
                    role="staff",  # Important: role is 'staff'
                    staff_type=staff_type,  # staff_type differentiates them
                    restaurant_id=sample_restaurant.id
                )
                db_session.add(user)
        db_session.commit()
        
        # Act
        usage = get_current_usage(db_session, sample_restaurant.id)
        
        # Assert
        assert usage['users_waiter'] == 3, "Should count 3 waiters"
        assert usage['users_cashier'] == 2, "Should count 2 cashiers"
        assert usage['users_kitchen'] == 1, "Should count 1 kitchen user"
    
    def test_excludes_deleted_users(self, db_session, sample_restaurant):
        """Test that soft-deleted users are not counted"""
        # Arrange - Create active and deleted users
        active_user = User(
            email="active@test.com",
            hashed_password="hashed",
            full_name="Active Waiter",  # Required field
            role="staff",
            staff_type="waiter",
            restaurant_id=sample_restaurant.id
        )
        deleted_user = User(
            email="deleted@test.com",
            hashed_password="hashed",
            full_name="Deleted Waiter",  # Required field
            role="staff",
            staff_type="waiter",
            restaurant_id=sample_restaurant.id,
            deleted_at=datetime.now(timezone.utc)  # Soft deleted
        )
        db_session.add_all([active_user, deleted_user])
        db_session.commit()
        
        # Act
        usage = get_current_usage(db_session, sample_restaurant.id)
        
        # Assert
        assert usage['users_waiter'] == 1, "Should only count active waiter"
    
    def test_counts_resources_correctly(self, db_session, sample_restaurant):
        """Test that tables, menu items, and categories are counted"""
        # Arrange - Create resources
        for i in range(5):
            table = Table(
                number=i + 1,
                capacity=4,
                location=f"Zone {i+1}",  # Required field
                restaurant_id=sample_restaurant.id
            )
            db_session.add(table)
        
        for i in range(10):
            item = MenuItem(
                name=f"Item {i}",
                price=10.0,
                restaurant_id=sample_restaurant.id,
                category_id=1
            )
            db_session.add(item)
        
        for i in range(3):
            category = Category(
                name=f"Category {i}",
                restaurant_id=sample_restaurant.id
            )
            db_session.add(category)
        
        db_session.commit()
        
        # Act
        usage = get_current_usage(db_session, sample_restaurant.id)
        
        # Assert
        assert usage['tables'] == 5
        assert usage['menu_items'] == 10
        assert usage['categories'] == 3
    
    def test_isolates_by_restaurant(self, db_session, sample_restaurant):
        """Test that usage is isolated by restaurant_id"""
        # Arrange - Create another restaurant
        other_restaurant = type('Restaurant', (), {'id': 999})()
        
        # Create users for different restaurants
        user1 = User(
            email="user1@test.com",
            hashed_password="hashed",
            full_name="User 1",  # Required field
            role="staff",
            staff_type="waiter",
            restaurant_id=sample_restaurant.id
        )
        user2 = User(
            email="user2@test.com",
            hashed_password="hashed",
            full_name="User 2",  # Required field
            role="staff",
            staff_type="waiter",
            restaurant_id=999  # Different restaurant
        )
        db_session.add_all([user1, user2])
        db_session.commit()
        
        # Act
        usage = get_current_usage(db_session, sample_restaurant.id)
        
        # Assert
        assert usage['users_waiter'] == 1, "Should only count users from this restaurant"


class TestValidatePlanLimits:
    """Test suite for validate_plan_limits function"""
    
    def test_no_violations_when_within_limits(self, db_session, sample_restaurant):
        """Test that no violations are returned when usage is within limits"""
        # Arrange - Create a plan with generous limits
        plan = SubscriptionPlan(
            tier=PlanTier.PRO,
            display_name="Pro Plan",
            max_admin_users=5,
            max_waiter_users=10,
            max_cashier_users=5,
            max_kitchen_users=5,
            max_owner_users=2,
            max_tables=20,
            max_menu_items=100,
            max_categories=10
        )
        
        # Create 1 waiter (within limit of 10)
        user = User(
            email="waiter@test.com",
            hashed_password="hashed",
            full_name="Test Waiter",  # Required field
            role="staff",
            staff_type="waiter",
            restaurant_id=sample_restaurant.id
        )
        db_session.add(user)
        db_session.commit()
        
        # Act
        violations = validate_plan_limits(db_session, sample_restaurant.id, plan)
        
        # Assert
        assert len(violations) == 0, "Should have no violations"
    
    def test_detects_user_limit_violations(self, db_session, sample_restaurant):
        """Test that violations are detected when user limits are exceeded"""
        # Arrange - Create a plan with strict limits
        plan = SubscriptionPlan(
            tier=PlanTier.STARTER,
            display_name="Starter Plan",
            max_admin_users=1,
            max_waiter_users=2,  # Limit: 2 waiters
            max_cashier_users=1,
            max_kitchen_users=1,
            max_owner_users=1,
            max_tables=10,
            max_menu_items=50,
            max_categories=5
        )
        
        # Create 3 waiters (exceeds limit of 2)
        for i in range(3):
            user = User(
                email=f"waiter{i}@test.com",
                hashed_password="hashed",
                full_name=f"Waiter {i}",  # Required field
                role="staff",
                staff_type="waiter",
                restaurant_id=sample_restaurant.id
            )
            db_session.add(user)
        db_session.commit()
        
        # Act
        violations = validate_plan_limits(db_session, sample_restaurant.id, plan)
        
        # Assert
        assert len(violations) > 0, "Should detect violation"
        assert any("meseros" in v for v in violations), "Should mention waiters in Spanish"
        assert any("3" in v and "2" in v for v in violations), "Should show current (3) vs limit (2)"
    
    def test_unlimited_resources_never_violate(self, db_session, sample_restaurant):
        """Test that -1 (unlimited) never causes violations"""
        # Arrange - Create plan with unlimited waiters
        plan = SubscriptionPlan(
            tier=PlanTier.ENTERPRISE,
            display_name="Enterprise Plan",
            max_admin_users=-1,  # Unlimited
            max_waiter_users=-1,  # Unlimited
            max_cashier_users=-1,
            max_kitchen_users=-1,
            max_owner_users=-1,
            max_tables=-1,
            max_menu_items=-1,
            max_categories=-1
        )
        
        # Create many users
        for i in range(100):
            user = User(
                email=f"waiter{i}@test.com",
                hashed_password="hashed",
                full_name=f"Waiter {i}",  # Required field
                role="staff",
                staff_type="waiter",
                restaurant_id=sample_restaurant.id
            )
            db_session.add(user)
        db_session.commit()
        
        # Act
        violations = validate_plan_limits(db_session, sample_restaurant.id, plan)
        
        # Assert
        assert len(violations) == 0, "Unlimited resources should never violate"


class TestCheckResourceLimit:
    """Test suite for check_resource_limit function"""
    
    def test_can_check_specific_user_type(self, db_session, sample_restaurant):
        """Test checking limit for specific user type"""
        # Arrange
        plan = SubscriptionPlan(
            tier=PlanTier.PRO,
            display_name="Pro Plan",
            max_waiter_users=5,
            max_admin_users=2,
            max_cashier_users=2,
            max_kitchen_users=2,
            max_owner_users=1,
            max_tables=10,
            max_menu_items=50,
            max_categories=5
        )
        
        # Create 3 waiters
        for i in range(3):
            user = User(
                email=f"waiter{i}@test.com",
                hashed_password="hashed",
                full_name=f"Waiter {i}",  # Required field
                role="staff",
                staff_type="waiter",
                restaurant_id=sample_restaurant.id
            )
            db_session.add(user)
        db_session.commit()
        
        # Act
        is_within_limit, message = check_resource_limit(
            db_session, sample_restaurant.id, "users_waiter", plan
        )
        
        # Assert
        assert is_within_limit is True, "3 waiters should be within limit of 5"


class TestCanAddResource:
    """Test suite for can_add_resource function"""
    
    def test_can_add_when_below_limit(self, db_session, sample_restaurant):
        """Test that resources can be added when below limit"""
        # Arrange
        plan = SubscriptionPlan(
            tier=PlanTier.PRO,
            display_name="Pro Plan",
            max_tables=10,
            max_admin_users=2,
            max_waiter_users=5,
            max_cashier_users=2,
            max_kitchen_users=2,
            max_owner_users=1,
            max_menu_items=50,
            max_categories=5
        )
        
        # Create 5 tables (below limit of 10)
        for i in range(5):
            table = Table(
                number=i + 1,
                capacity=4,
                location=f"Zone {i+1}",  # Required field
                restaurant_id=sample_restaurant.id
            )
            db_session.add(table)
        db_session.commit()
        
        # Act
        can_add = can_add_resource(db_session, sample_restaurant.id, "tables", plan)
        
        # Assert
        assert can_add is True, "Should be able to add more tables"
    
    def test_cannot_add_when_at_limit(self, db_session, sample_restaurant):
        """Test that resources cannot be added when at limit"""
        # Arrange
        plan = SubscriptionPlan(
            tier=PlanTier.STARTER,
            display_name="Starter Plan",
            max_tables=5,  # Strict limit
            max_admin_users=1,
            max_waiter_users=2,
            max_cashier_users=1,
            max_kitchen_users=1,
            max_owner_users=1,
            max_menu_items=20,
            max_categories=3
        )
        
        # Create exactly 5 tables (at limit)
        for i in range(5):
            table = Table(
                number=i + 1,
                capacity=4,
                location=f"Zone {i+1}",  # Required field
                restaurant_id=sample_restaurant.id
            )
            db_session.add(table)
        db_session.commit()
        
        # Act
        can_add = can_add_resource(db_session, sample_restaurant.id, "tables", plan)
        
        # Assert
        assert can_add is False, "Should not be able to add more tables"


# Fixtures
@pytest.fixture
def sample_restaurant(db_session):
    """Create a sample restaurant for testing"""
    restaurant = type('Restaurant', (), {
        'id': 1,
        'name': 'Test Restaurant',
        'subdomain': 'test'
    })()
    return restaurant
