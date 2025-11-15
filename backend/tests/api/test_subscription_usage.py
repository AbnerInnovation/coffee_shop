"""
Integration tests for subscription usage endpoints

These tests verify that the API correctly returns user counts
considering the role/staff_type structure.
"""

import pytest
from fastapi.testclient import TestClient

from app.models import User, SubscriptionPlan, RestaurantSubscription, PlanTier, SubscriptionStatus, BillingCycle
from datetime import datetime, timedelta, timezone


class TestSubscriptionUsageEndpoint:
    """Test suite for /api/v1/subscriptions/usage endpoint"""
    
    def test_returns_correct_user_counts(
        self, 
        client: TestClient, 
        db_session, 
        sample_restaurant,
        auth_headers
    ):
        """Test that endpoint returns correct user counts by type"""
        # Arrange - Create users with different roles/types
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        users_data = [
            {'role': 'admin', 'staff_type': None, 'email': f'admin-{unique_id}@test.com'},
            {'role': 'staff', 'staff_type': 'waiter', 'email': f'waiter1-{unique_id}@test.com'},
            {'role': 'staff', 'staff_type': 'waiter', 'email': f'waiter2-{unique_id}@test.com'},
            {'role': 'staff', 'staff_type': 'cashier', 'email': f'cashier-{unique_id}@test.com'},
            {'role': 'staff', 'staff_type': 'kitchen', 'email': f'kitchen-{unique_id}@test.com'},
        ]
        
        for user_data in users_data:
            user = User(
                email=user_data['email'],
                hashed_password='hashed',
                full_name=user_data['email'].split('@')[0].title(),  # Required field
                role=user_data['role'],
                staff_type=user_data['staff_type'],
                restaurant_id=sample_restaurant.id
            )
            db_session.add(user)
        
        # Create subscription
        plan = SubscriptionPlan(
            name='pro',  # Required field
            tier=PlanTier.PRO,
            display_name='Pro Plan',
            monthly_price=99.0,
            max_admin_users=5,
            max_waiter_users=10,
            max_cashier_users=5,
            max_kitchen_users=5,
            max_owner_users=2,
            max_tables=20,
            max_menu_items=100,
            max_categories=10,
            is_active=True
        )
        db_session.add(plan)
        db_session.flush()
        
        subscription = RestaurantSubscription(
            restaurant_id=sample_restaurant.id,
            plan_id=plan.id,
            status=SubscriptionStatus.ACTIVE,
            billing_cycle=BillingCycle.MONTHLY,
            start_date=datetime.now(timezone.utc),
            current_period_start=datetime.now(timezone.utc),
            current_period_end=datetime.now(timezone.utc) + timedelta(days=30),
            base_price=99.0,
            total_price=99.0
        )
        db_session.add(subscription)
        db_session.commit()
        
        # Act
        response = client.get(
            '/api/v1/subscriptions/usage',
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert 'usage' in data
        assert 'users' in data['usage']
        
        # Verify counts
        assert data['usage']['users']['admin'] == 1, "Should count 1 admin"
        assert data['usage']['users']['waiter'] == 2, "Should count 2 waiters"
        assert data['usage']['users']['cashier'] == 1, "Should count 1 cashier"
        assert data['usage']['users']['kitchen'] == 1, "Should count 1 kitchen user"
    
    def test_excludes_deleted_users_from_count(
        self,
        client: TestClient,
        db_session,
        sample_restaurant,
        auth_headers
    ):
        """Test that soft-deleted users are not included in counts"""
        # Arrange - Create active and deleted users
        active_user = User(
            email='active@test.com',
            hashed_password='hashed',
            full_name='Active Waiter',  # Required field
            role='staff',
            staff_type='waiter',
            restaurant_id=sample_restaurant.id
        )
        deleted_user = User(
            email='deleted@test.com',
            hashed_password='hashed',
            full_name='Deleted Waiter',  # Required field
            role='staff',
            staff_type='waiter',
            restaurant_id=sample_restaurant.id,
            deleted_at=datetime.now(timezone.utc)
        )
        db_session.add_all([active_user, deleted_user])
        
        # Create subscription (required for endpoint)
        plan = SubscriptionPlan(
            name='starter',  # Required field
            tier=PlanTier.STARTER,
            display_name='Starter Plan',
            monthly_price=29.0,
            max_admin_users=1,
            max_waiter_users=5,
            max_cashier_users=2,
            max_kitchen_users=2,
            max_owner_users=1,
            max_tables=10,
            max_menu_items=50,
            max_categories=5,
            is_active=True
        )
        db_session.add(plan)
        db_session.flush()
        
        subscription = RestaurantSubscription(
            restaurant_id=sample_restaurant.id,
            plan_id=plan.id,
            status=SubscriptionStatus.ACTIVE,
            billing_cycle=BillingCycle.MONTHLY,
            start_date=datetime.now(timezone.utc),
            current_period_start=datetime.now(timezone.utc),
            current_period_end=datetime.now(timezone.utc) + timedelta(days=30),
            base_price=29.0,
            total_price=29.0
        )
        db_session.add(subscription)
        db_session.commit()
        
        # Act
        response = client.get(
            '/api/v1/subscriptions/usage',
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data['usage']['users']['waiter'] == 1, "Should only count active waiter"
    
    def test_shows_correct_percentages(
        self,
        client: TestClient,
        db_session,
        sample_restaurant,
        auth_headers
    ):
        """Test that usage percentages are calculated correctly"""
        # Arrange - Create 2 waiters with limit of 5 (40%)
        for i in range(2):
            user = User(
                email=f'waiter{i}@test.com',
                hashed_password='hashed',
                full_name=f'Waiter {i}',  # Required field
                role='staff',
                staff_type='waiter',
                restaurant_id=sample_restaurant.id
            )
            db_session.add(user)
        
        # Create subscription with limit of 5 waiters
        plan = SubscriptionPlan(
            name='starter',  # Required field
            tier=PlanTier.STARTER,
            display_name='Starter Plan',
            monthly_price=29.0,
            max_admin_users=1,
            max_waiter_users=5,  # Limit: 5
            max_cashier_users=2,
            max_kitchen_users=2,
            max_owner_users=1,
            max_tables=10,
            max_menu_items=50,
            max_categories=5,
            is_active=True
        )
        db_session.add(plan)
        db_session.flush()
        
        subscription = RestaurantSubscription(
            restaurant_id=sample_restaurant.id,
            plan_id=plan.id,
            status=SubscriptionStatus.ACTIVE,
            billing_cycle=BillingCycle.MONTHLY,
            start_date=datetime.now(timezone.utc),
            current_period_start=datetime.now(timezone.utc),
            current_period_end=datetime.now(timezone.utc) + timedelta(days=30),
            base_price=29.0,
            total_price=29.0
        )
        db_session.add(subscription)
        db_session.commit()
        
        # Act
        response = client.get(
            '/api/v1/subscriptions/usage',
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        # 2 out of 5 = 40%
        assert 'percentages' in data
        assert data['percentages']['waiter_users'] == 40.0, "Should show 40% usage"


# Fixtures would be defined in conftest.py
@pytest.fixture
def sample_restaurant():
    """Sample restaurant for testing"""
    return type('Restaurant', (), {
        'id': 1,
        'name': 'Test Restaurant',
        'subdomain': 'test'
    })()


@pytest.fixture
def auth_headers():
    """Authentication headers for testing"""
    return {
        'Authorization': 'Bearer test_token'
    }
