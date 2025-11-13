"""
Pytest configuration and shared fixtures.

This file contains reusable fixtures for testing the Coffee Shop Admin API.
"""
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base, get_db
from app.core.config import settings
from app.models.user import User, UserRole
from app.models.restaurant import Restaurant
from app.models.subscription_plan import SubscriptionPlan, PlanTier
from app.models.restaurant_subscription import RestaurantSubscription, BillingCycle, SubscriptionStatus
from app.core.security import get_password_hash
from app.services.user import get_current_user, get_current_active_user
from app.core.dependencies import get_current_restaurant, get_current_user_with_restaurant, get_current_user_with_active_subscription
from datetime import datetime, timedelta, timezone


# Test database URL (SQLite in-memory for fast tests)
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

# Create test engine with in-memory SQLite
test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """
    Create a fresh database session for each test.
    
    This fixture:
    - Creates all tables before the test
    - Provides a clean database session
    - Rolls back all changes after the test
    - Drops all tables after the test
    
    Yields:
        Session: SQLAlchemy database session
    """
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    
    # Create a new session
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Drop all tables to ensure clean state
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(
    db_session: Session,
    test_restaurant: Restaurant,
    test_admin_user: User
) -> Generator[TestClient, None, None]:
    """
    Create a test client with overridden dependencies.
    
    This fixture:
    - Overrides the get_db dependency to use test database
    - Overrides authentication dependencies to bypass auth in tests
    - Provides a TestClient for making API requests
    - Automatically handles cleanup
    - Sets base_url with subdomain to bypass restaurant middleware
    
    Args:
        db_session: Database session fixture
        test_restaurant: Test restaurant fixture
        test_admin_user: Test admin user fixture
        
    Yields:
        TestClient: FastAPI test client
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    def override_get_current_user():
        return test_admin_user
    
    def override_get_current_active_user():
        return test_admin_user
    
    def override_get_current_restaurant():
        return test_restaurant
    
    def override_get_current_user_with_restaurant():
        return test_admin_user
    
    def override_get_current_user_with_active_subscription():
        return test_admin_user
    
    # Override all dependencies
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user
    app.dependency_overrides[get_current_restaurant] = override_get_current_restaurant
    app.dependency_overrides[get_current_user_with_restaurant] = override_get_current_user_with_restaurant
    app.dependency_overrides[get_current_user_with_active_subscription] = override_get_current_user_with_active_subscription
    
    # Use subdomain in base_url to bypass restaurant middleware in tests
    with TestClient(app, base_url="http://default.testserver") as test_client:
        yield test_client
    
    # Clear overrides after test
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client_no_auth(db_session: Session) -> Generator[TestClient, None, None]:
    """
    Create a test client WITHOUT auth overrides for testing unauthorized access.
    
    This fixture:
    - Only overrides get_db (not auth dependencies)
    - Used for testing 401 Unauthorized responses
    - Automatically handles cleanup
    
    Args:
        db_session: Database session fixture
        
    Yields:
        TestClient: FastAPI test client without auth
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    # Only override database, NOT auth
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app, base_url="http://default.testserver") as test_client:
        yield test_client
    
    # Clear overrides after test
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_restaurant(db_session: Session) -> Restaurant:
    """
    Create a test restaurant.
    
    Args:
        db_session: Database session fixture
        
    Returns:
        Restaurant: Test restaurant instance
    """
    restaurant = Restaurant(
        name="Test Restaurant",
        subdomain="default",
        phone="+1234567890",
        address="123 Test St",
        email="restaurant@test.com",
        currency="USD"
    )
    db_session.add(restaurant)
    db_session.commit()
    db_session.refresh(restaurant)
    return restaurant


@pytest.fixture(scope="function")
def test_admin_user(db_session: Session, test_restaurant: Restaurant) -> User:
    """
    Create a test admin user.
    
    Args:
        db_session: Database session fixture
        test_restaurant: Test restaurant fixture
        
    Returns:
        User: Test admin user instance
    """
    user = User(
        email="admin@test.com",
        full_name="Admin User",
        hashed_password=get_password_hash("testpassword123"),
        role=UserRole.SYSADMIN,  # Use SYSADMIN to bypass subscription checks in tests
        restaurant_id=test_restaurant.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_staff_user(db_session: Session, test_restaurant: Restaurant) -> User:
    """
    Create a test staff user.
    
    Args:
        db_session: Database session fixture
        test_restaurant: Test restaurant fixture
        
    Returns:
        User: Test staff user instance
    """
    user = User(
        email="staff@test.com",
        full_name="Staff User",
        hashed_password=get_password_hash("testpassword123"),
        role=UserRole.STAFF,
        restaurant_id=test_restaurant.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_sysadmin_user(db_session: Session) -> User:
    """
    Create a test sysadmin user.
    
    Args:
        db_session: Database session fixture
        
    Returns:
        User: Test sysadmin user instance
    """
    user = User(
        email="sysadmin@test.com",
        full_name="SysAdmin User",
        hashed_password=get_password_hash("testpassword123"),
        role=UserRole.SYSADMIN,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def admin_token_headers(client: TestClient, test_admin_user: User) -> dict:
    """
    Get authentication headers for admin user.
    
    Args:
        client: Test client fixture
        test_admin_user: Test admin user fixture
        
    Returns:
        dict: Headers with authentication token
    """
    login_data = {
        "username": test_admin_user.email,
        "password": "testpassword123"
    }
    response = client.post(
        "/api/v1/auth/token",
        data=login_data,
        headers={"Host": "default.testserver"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def staff_token_headers(client: TestClient, test_staff_user: User) -> dict:
    """
    Get authentication headers for staff user.
    
    Args:
        client: Test client fixture
        test_staff_user: Test staff user fixture
        
    Returns:
        dict: Headers with authentication token
    """
    login_data = {
        "username": test_staff_user.email,
        "password": "testpassword123"
    }
    response = client.post("/api/v1/auth/token", data=login_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def sysadmin_token_headers(client: TestClient, test_sysadmin_user: User) -> dict:
    """
    Get authentication headers for sysadmin user.
    
    Args:
        client: Test client fixture
        test_sysadmin_user: Test sysadmin user fixture
        
    Returns:
        dict: Headers with authentication token
    """
    login_data = {
        "username": test_sysadmin_user.email,
        "password": "testpassword123"
    }
    response = client.post("/api/v1/auth/token", data=login_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def test_subscription_plan(db_session: Session) -> SubscriptionPlan:
    """
    Create a test subscription plan.
    
    Args:
        db_session: Database session fixture
        
    Returns:
        SubscriptionPlan: Test subscription plan instance
    """
    plan = SubscriptionPlan(
        name="Pro",
        tier=PlanTier.PRO,
        display_name="Plan Pro",
        description="Plan Pro para tests",
        monthly_price=999.00,
        annual_price=9990.00,
        max_admin_users=1,
        max_waiter_users=4,
        max_cashier_users=2,
        max_kitchen_users=2,
        max_owner_users=0,
        max_tables=35,
        max_menu_items=400,
        max_categories=50,
        has_kitchen_module=True,
        has_ingredients_module=True,
        has_advanced_reports=True,
        is_active=True,
        sort_order=3
    )
    db_session.add(plan)
    db_session.commit()
    db_session.refresh(plan)
    return plan


@pytest.fixture(scope="function")
def test_restaurant_subscription(
    db_session: Session, 
    test_restaurant: Restaurant,
    test_subscription_plan: SubscriptionPlan
) -> RestaurantSubscription:
    """
    Create an active subscription for test restaurant.
    
    Args:
        db_session: Database session fixture
        test_restaurant: Test restaurant fixture
        test_subscription_plan: Test subscription plan fixture
        
    Returns:
        RestaurantSubscription: Active subscription instance
    """
    now = datetime.now(timezone.utc)
    subscription = RestaurantSubscription(
        restaurant_id=test_restaurant.id,
        plan_id=test_subscription_plan.id,
        status=SubscriptionStatus.ACTIVE,
        billing_cycle=BillingCycle.MONTHLY,
        start_date=now,
        current_period_start=now,
        current_period_end=now + timedelta(days=30),
        base_price=test_subscription_plan.monthly_price,
        total_price=test_subscription_plan.monthly_price,
        auto_renew=True
    )
    db_session.add(subscription)
    db_session.commit()
    db_session.refresh(subscription)
    return subscription
