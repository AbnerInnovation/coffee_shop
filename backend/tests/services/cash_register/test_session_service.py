"""
Unit tests for cash_register/session_service.py

Tests all session management operations:
- Creating sessions with auto-incrementing session numbers
- Retrieving sessions (by ID, current, filtered list)
- Closing sessions with balance calculations
- Closing sessions with denomination counting
- Error handling and validation
"""

import pytest
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy.orm import Session
from app.services.cash_register.session_service import (
    create_session, 
    get_sessions, 
    get_session, 
    get_current_session,
    close_session
)
from app.schemas.cash_register import CashRegisterSessionCreate
from app.models.user import User
from app.core.exceptions import ConflictError
from app.models.cash_register import (
    CashRegisterSession as CashRegisterSessionModel,
    SessionStatus
)
from app.schemas.cash_register import (
    CashRegisterSessionCreate,
    CashRegisterSessionUpdate,
    DenominationCount
)


class TestCreateSession:
    """Tests for create_session function"""
    
    def test_create_first_session(self, db_session: Session, test_restaurant, test_admin_user):
        """Test creating the first session for a restaurant"""
        session_data = CashRegisterSessionCreate(
            opened_by_user_id=test_admin_user.id,
            cashier_id=test_admin_user.id,
            initial_balance=Decimal("100.00")
        )
        
        result = create_session(db_session, session_data, test_restaurant.id)
        
        assert result.id is not None
        assert result.session_number == 1
        assert result.restaurant_id == test_restaurant.id
        assert result.opened_by_user_id == test_admin_user.id
        assert result.cashier_id == test_admin_user.id
        assert result.initial_balance == Decimal("100.00")
        assert result.status == SessionStatus.OPEN
        assert result.opened_at is not None
        assert result.closed_at is None
    
    def test_create_session_auto_increment(self, db_session: Session, test_restaurant, test_admin_user):
        """Test that session numbers auto-increment correctly"""
        session_data = CashRegisterSessionCreate(
            opened_by_user_id=test_admin_user.id,
            cashier_id=test_admin_user.id,
            initial_balance=Decimal("100.00")
        )
        
        # Create first session
        session1 = create_session(db_session, session_data, test_restaurant.id)
        assert session1.session_number == 1
        
        # Close first session
        session1.status = SessionStatus.CLOSED
        db_session.commit()
        
        # Create second session
        session2 = create_session(db_session, session_data, test_restaurant.id)
        assert session2.session_number == 2
        
        # Close second session
        session2.status = SessionStatus.CLOSED
        db_session.commit()
        
        # Create third session
        session3 = create_session(db_session, session_data, test_restaurant.id)
        assert session3.session_number == 3
    
    def test_cannot_create_multiple_open_sessions_for_same_restaurant(
        self, 
        db_session: Session, 
        test_restaurant, 
        test_admin_user
    ):
        """Test that ConflictError is raised when trying to create multiple open sessions for same restaurant"""
        session_data = CashRegisterSessionCreate(
            opened_by_user_id=test_admin_user.id,
            cashier_id=test_admin_user.id,
            initial_balance=Decimal("100.00")
        )
        
        # Create first session (should succeed)
        session1 = create_session(db_session, session_data, test_restaurant.id)
        assert session1.status == SessionStatus.OPEN
        
        # Attempt to create second session without closing first (should raise ConflictError)
        with pytest.raises(ConflictError) as exc_info:
            create_session(db_session, session_data, test_restaurant.id)
        
        # Verify error message contains useful context
        error_message = str(exc_info.value.message)
        assert "Cannot open a new session" in error_message
        assert "already an open session" in error_message
        assert f"Session #{session1.session_number}" in error_message
    
    def test_create_session_different_restaurants(
        self, 
        db_session: Session, 
        test_restaurant, 
        test_admin_user
    ):
        """Test that session numbers are independent per restaurant"""
        from app.models.restaurant import Restaurant
        
        # Create second restaurant
        restaurant2 = Restaurant(
            name="Restaurant 2",
            subdomain="restaurant2"
        )
        db_session.add(restaurant2)
        db_session.commit()
        
        session_data = CashRegisterSessionCreate(
            opened_by_user_id=test_admin_user.id,
            cashier_id=test_admin_user.id,
            initial_balance=Decimal("100.00")
        )
        
        # Create session for restaurant 1
        session1 = create_session(db_session, session_data, test_restaurant.id)
        assert session1.session_number == 1
        
        # Create session for restaurant 2
        session2 = create_session(db_session, session_data, restaurant2.id)
        assert session2.session_number == 1  # Should also be 1
        
        # Create another session for restaurant 1
        session1.status = SessionStatus.CLOSED
        db_session.commit()
        session3 = create_session(db_session, session_data, test_restaurant.id)
        assert session3.session_number == 2


class TestGetSession:
    """Tests for get_session function"""
    
    def test_get_existing_session(self, db_session: Session, test_restaurant, test_admin_user):
        """Test retrieving an existing session by ID"""
        session_data = CashRegisterSessionCreate(
            opened_by_user_id=test_admin_user.id,
            cashier_id=test_admin_user.id,
            initial_balance=Decimal("100.00")
        )
        
        created = create_session(db_session, session_data, test_restaurant.id)
        
        result = get_session(db_session, created.id)
        
        assert result is not None
        assert result.id == created.id
        assert result.session_number == created.session_number
    
    def test_get_nonexistent_session(self, db_session: Session):
        """Test retrieving a non-existent session returns None"""
        result = get_session(db_session, 99999)
        assert result is None


class TestGetCurrentSession:
    """Tests for get_current_session function"""
    
    def test_get_current_open_session(self, db_session: Session, test_restaurant, test_admin_user):
        """Test retrieving the current open session for a user"""
        session_data = CashRegisterSessionCreate(
            opened_by_user_id=test_admin_user.id,
            cashier_id=test_admin_user.id,
            initial_balance=Decimal("100.00")
        )
        
        created = create_session(db_session, session_data, test_restaurant.id)
        
        result = get_current_session(db_session, test_admin_user.id)
        
        assert result is not None
        assert result.id == created.id
        assert result.status == SessionStatus.OPEN
    
    def test_get_current_session_no_open_session(self, db_session: Session, test_admin_user):
        """Test that no current session is returned when all are closed"""
        result = get_current_session(db_session, test_admin_user.id)
        assert result is None
    
    def test_get_current_session_returns_most_recent(
        self, 
        db_session: Session, 
        test_restaurant, 
        test_admin_user
    ):
        """Test that get_current_session returns the most recent open session"""
        session_data = CashRegisterSessionCreate(
            opened_by_user_id=test_admin_user.id,
            cashier_id=test_admin_user.id,
            initial_balance=Decimal("100.00")
        )
        
        # Create and close first session
        session1 = create_session(db_session, session_data, test_restaurant.id)
        session1.status = SessionStatus.CLOSED
        db_session.commit()
        
        # Create second open session
        session2 = create_session(db_session, session_data, test_restaurant.id)
        
        result = get_current_session(db_session, test_admin_user.id)
        
        assert result is not None
        assert result.id == session2.id


class TestGetSessions:
    """Tests for get_sessions function"""
    
    def test_get_all_sessions(self, db_session: Session, test_restaurant, test_admin_user):
        """Test retrieving all sessions without filters"""
        from app.models.restaurant import Restaurant
        from app.services.cash_register.session_service import close_session
        from app.schemas.cash_register import CashRegisterSessionUpdate
        
        # Create additional restaurants for multiple sessions
        restaurant2 = Restaurant(
            name="Restaurant 2",
            subdomain="restaurant2"
        )
        restaurant3 = Restaurant(
            name="Restaurant 3", 
            subdomain="restaurant3"
        )
        db_session.add_all([restaurant2, restaurant3])
        db_session.commit()
        
        session_data = CashRegisterSessionCreate(
            opened_by_user_id=test_admin_user.id,
            cashier_id=test_admin_user.id,
            initial_balance=Decimal("100.00")
        )
        
        # Create sessions for different restaurants (1 per restaurant to respect business rule)
        session1 = create_session(db_session, session_data, test_restaurant.id)
        session2 = create_session(db_session, session_data, restaurant2.id)
        session3 = create_session(db_session, session_data, restaurant3.id)
        
        result = get_sessions(db_session)
        
        assert len(result) == 3
    
    def test_get_sessions_filter_by_restaurant(
        self, 
        db_session: Session, 
        test_restaurant, 
        test_admin_user
    ):
        """Test filtering sessions by restaurant ID"""
        from app.models.restaurant import Restaurant
        from app.services.cash_register.session_service import close_session
        from app.schemas.cash_register import CashRegisterSessionUpdate
        
        # Create second restaurant
        restaurant2 = Restaurant(
            name="Restaurant 2",
            subdomain="restaurant2"
        )
        db_session.add(restaurant2)
        db_session.commit()
        
        session_data = CashRegisterSessionCreate(
            opened_by_user_id=test_admin_user.id,
            cashier_id=test_admin_user.id,
            initial_balance=Decimal("100.00")
        )
        
        # Create sessions: 2 for test_restaurant (sequentially), 1 for restaurant2
        session1 = create_session(db_session, session_data, test_restaurant.id)
        # Close first session to allow second one for same restaurant
        close_session(db_session, session1.id, CashRegisterSessionUpdate(final_balance=100.00))
        session2 = create_session(db_session, session_data, test_restaurant.id)
        session3 = create_session(db_session, session_data, restaurant2.id)
        
        result = get_sessions(db_session, restaurant_id=test_restaurant.id)
        
        assert len(result) == 2
        assert all(s.restaurant_id == test_restaurant.id for s in result)
    
    def test_get_sessions_filter_by_status(
        self, 
        db_session: Session, 
        test_restaurant, 
        test_admin_user
    ):
        """Test filtering sessions by status"""
        from app.models.restaurant import Restaurant
        from app.services.cash_register.session_service import close_session
        from app.schemas.cash_register import CashRegisterSessionUpdate
        
        session_data = CashRegisterSessionCreate(
            opened_by_user_id=test_admin_user.id,
            cashier_id=test_admin_user.id,
            initial_balance=Decimal("100.00")
        )
        
        # Create 3 sessions sequentially for the SAME restaurant: closed, open, closed
        session1 = create_session(db_session, session_data, test_restaurant.id)
        # Close first session
        close_session(db_session, session1.id, CashRegisterSessionUpdate(final_balance=100.00))
        
        # Create second session and close it
        session2 = create_session(db_session, session_data, test_restaurant.id)
        close_session(db_session, session2.id, CashRegisterSessionUpdate(final_balance=100.00))
        
        # Create third session (will be open)
        session3 = create_session(db_session, session_data, test_restaurant.id)
        
        result = get_sessions(db_session, status=SessionStatus.OPEN)
        
        assert len(result) == 1
        assert all(s.status == SessionStatus.OPEN for s in result)
    
    def test_get_sessions_pagination(self, db_session: Session, test_restaurant, test_admin_user):
        """Test pagination with skip and limit"""
        from app.models.restaurant import Restaurant
        from app.services.cash_register.session_service import close_session
        from app.schemas.cash_register import CashRegisterSessionUpdate
        
        session_data = CashRegisterSessionCreate(
            opened_by_user_id=test_admin_user.id,
            cashier_id=test_admin_user.id,
            initial_balance=Decimal("100.00")
        )
        
        # Create 5 sessions for different restaurants to test pagination properly
        restaurants = []
        for i in range(5):
            restaurant = Restaurant(
                name=f"Restaurant {i+2}",  # Start from 2 since test_restaurant is 1
                subdomain=f"restaurant{i+2}"
            )
            restaurants.append(restaurant)
        db_session.add_all(restaurants)
        db_session.commit()
        
        # Create 1 session per restaurant
        for restaurant in restaurants:
            create_session(db_session, session_data, restaurant.id)
        
        # Get first 2
        result1 = get_sessions(db_session, skip=0, limit=2)
        assert len(result1) == 2
        
        # Get next 2
        result2 = get_sessions(db_session, skip=2, limit=2)
        assert len(result2) == 2
        
        # Verify they're different
        assert result1[0].id != result2[0].id


class TestCloseSession:
    """Tests for close_session function"""
    
    def test_close_session_success(self, db_session: Session, test_restaurant, test_admin_user):
        """Test successfully closing an open session"""
        session_data = CashRegisterSessionCreate(
            opened_by_user_id=test_admin_user.id,
            cashier_id=test_admin_user.id,
            initial_balance=Decimal("100.00")
        )
        
        session = create_session(db_session, session_data, test_restaurant.id)
        
        update_data = CashRegisterSessionUpdate(
            final_balance=Decimal("150.00"),
            notes="Test closing"
        )
        
        result = close_session(db_session, session.id, update_data)
        
        assert result.status == SessionStatus.CLOSED
        assert result.final_balance == Decimal("150.00")
        assert result.actual_balance == Decimal("150.00")
        assert result.closed_at is not None
        assert result.notes == "Test closing"
    
    def test_close_session_not_found(self, db_session: Session):
        """Test closing a non-existent session raises error"""
        update_data = CashRegisterSessionUpdate(
            final_balance=Decimal("150.00")
        )
        
        with pytest.raises(ValueError, match="Session not found"):
            close_session(db_session, 99999, update_data)
    
    def test_close_already_closed_session(
        self, 
        db_session: Session, 
        test_restaurant, 
        test_admin_user
    ):
        """Test closing an already closed session raises error"""
        session_data = CashRegisterSessionCreate(
            opened_by_user_id=test_admin_user.id,
            cashier_id=test_admin_user.id,
            initial_balance=Decimal("100.00")
        )
        
        session = create_session(db_session, session_data, test_restaurant.id)
        
        update_data = CashRegisterSessionUpdate(
            final_balance=Decimal("150.00")
        )
        
        # Close once
        close_session(db_session, session.id, update_data)
        
        # Try to close again
        with pytest.raises(ValueError, match="Session is not open"):
            close_session(db_session, session.id, update_data)


class TestCloseSessionWithDenominations:
    """Tests for close_session_with_denominations function"""
    
    def test_close_with_denominations(
        self, 
        db_session: Session, 
        test_restaurant, 
        test_admin_user
    ):
        """Test closing session with denomination counting"""
        session_data = CashRegisterSessionCreate(
            opened_by_user_id=test_admin_user.id,
            cashier_id=test_admin_user.id,
            initial_balance=Decimal("100.00")
        )
        
        session = create_session(db_session, session_data, test_restaurant.id)
        
        update_data = CashRegisterSessionUpdate(
            final_balance=Decimal("0.00"),  # Will be calculated from denominations
            notes="Counted denominations"
        )
        
        denominations = DenominationCount(
            bills_1000=1,   # 1000
            bills_500=2,    # 1000
            bills_200=3,    # 600
            bills_100=4,    # 400
            bills_50=5,     # 250
            bills_20=6,     # 120
            coins_10=7,     # 70
            coins_5=8,      # 40
            coins_2=9,      # 18
            coins_1=10      # 10
        )
        
        result = close_session_with_denominations(
            db_session, 
            session.id, 
            update_data, 
            denominations
        )
        
        expected_total = Decimal("3508.00")
        assert result.status == SessionStatus.CLOSED
        assert result.final_balance == expected_total
        assert result.actual_balance == expected_total
        assert "Denominations:" in result.notes
    
    def test_close_without_denominations(
        self, 
        db_session: Session, 
        test_restaurant, 
        test_admin_user
    ):
        """Test closing session without denominations uses final_balance"""
        session_data = CashRegisterSessionCreate(
            opened_by_user_id=test_admin_user.id,
            cashier_id=test_admin_user.id,
            initial_balance=Decimal("100.00")
        )
        
        session = create_session(db_session, session_data, test_restaurant.id)
        
        update_data = CashRegisterSessionUpdate(
            final_balance=Decimal("200.00"),
            notes="Manual count"
        )
        
        result = close_session_with_denominations(
            db_session, 
            session.id, 
            update_data, 
            None
        )
        
        assert result.final_balance == Decimal("200.00")
        assert result.actual_balance == Decimal("200.00")
        assert "Denominations:" not in result.notes
