"""
Unit tests for cash_register/report_service.py

Tests report generation operations:
- Daily session reports
- Session detail reports
- Report data aggregation
- Multi-session reports
"""

import pytest
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy.orm import Session

from app.services.cash_register.report_service import (
    get_daily_summary_reports,
    get_reports,
    generate_cash_difference_report
)
from app.services.cash_register.session_service import create_session, close_session
from app.services.cash_register.transaction_service import create_transaction
from app.models.cash_register import (
    CashRegisterReport as CashRegisterReportModel,
    TransactionType,
    PaymentMethod
)
from app.schemas.cash_register import (
    CashRegisterSessionCreate,
    CashRegisterSessionUpdate,
    CashTransactionCreate
)


class TestGenerateCashDifferenceReport:
    """Tests for generate_cash_difference_report function"""
    
    def test_generate_cash_difference_report_success(
        self, 
        db_session: Session, 
        test_restaurant, 
        test_admin_user
    ):
        """Test generating cash difference report"""
        session_data = CashRegisterSessionCreate(
            opened_by_user_id=test_admin_user.id,
            cashier_id=test_admin_user.id,
            initial_balance=Decimal("100.00")
        )
        session = create_session(db_session, session_data, test_restaurant.id)
        
        # Add transaction
        transaction_data = CashTransactionCreate(
            session_id=session.id,
            transaction_type=TransactionType.SALE,
            amount=Decimal("50.00"),
            description="Sale",
            payment_method=PaymentMethod.CASH,
            created_by_user_id=test_admin_user.id
        )
        create_transaction(db_session, transaction_data, test_admin_user.id)
        
        # Close session with actual balance
        update_data = CashRegisterSessionUpdate(
            final_balance=Decimal("145.00")  # 5 less than expected
        )
        close_session(db_session, session.id, update_data)
        
        result = generate_cash_difference_report(db_session, session.id)
        
        assert result.session_id == session.id
        assert result.expected_balance == 150.0  # 100 + 50
        assert result.actual_balance == 145.0
        assert result.difference == -5.0  # Shortage
    
    def test_generate_cash_difference_report_not_found(
        self, 
        db_session: Session
    ):
        """Test generating report for non-existent session raises error"""
        with pytest.raises(ValueError, match="Session not found"):
            generate_cash_difference_report(db_session, 99999)


class TestGetReports:
    """Tests for get_reports function"""
    
    def test_get_reports_empty(self, db_session: Session):
        """Test getting reports when none exist"""
        result = get_reports(db_session)
        
        assert len(result) == 0
    
    def test_get_reports_filters_by_session(
        self, 
        db_session: Session, 
        test_restaurant, 
        test_admin_user
    ):
        """Test that reports can be filtered by session"""
        from app.models.cash_register import ReportType
        import json
        
        # Create two sessions
        session_data = CashRegisterSessionCreate(
            opened_by_user_id=test_admin_user.id,
            cashier_id=test_admin_user.id,
            initial_balance=Decimal("100.00")
        )
        
        session1 = create_session(db_session, session_data, test_restaurant.id)
        session1.status = "CLOSED"
        db_session.commit()
        
        session2 = create_session(db_session, session_data, test_restaurant.id)
        
        # Create reports manually
        report1 = CashRegisterReportModel(
            session_id=session1.id,
            report_type=ReportType.DAILY_SUMMARY,
            data=json.dumps({"test": "data1"}),
            generated_at=datetime.now(timezone.utc)
        )
        report2 = CashRegisterReportModel(
            session_id=session2.id,
            report_type=ReportType.DAILY_SUMMARY,
            data=json.dumps({"test": "data2"}),
            generated_at=datetime.now(timezone.utc)
        )
        db_session.add(report1)
        db_session.add(report2)
        db_session.commit()
        
        # Get reports for session 1
        result = get_reports(db_session, session_id=session1.id)
        
        assert len(result) == 1
        assert result[0].session_id == session1.id


class TestGetDailySummaryReports:
    """Tests for get_daily_summary_reports function"""
    
    def test_get_daily_summary_empty(
        self, 
        db_session: Session, 
        test_restaurant
    ):
        """Test getting daily summaries when no closed sessions exist"""
        result = get_daily_summary_reports(
            db_session, 
            restaurant_id=test_restaurant.id
        )
        
        assert len(result) == 0
    
    def test_get_daily_summary_with_closed_sessions(
        self, 
        db_session: Session, 
        test_restaurant, 
        test_admin_user
    ):
        """Test getting daily summaries for closed sessions"""
        session_data = CashRegisterSessionCreate(
            opened_by_user_id=test_admin_user.id,
            cashier_id=test_admin_user.id,
            initial_balance=Decimal("100.00")
        )
        session = create_session(db_session, session_data, test_restaurant.id)
        
        # Add transaction
        transaction_data = CashTransactionCreate(
            session_id=session.id,
            transaction_type=TransactionType.SALE,
            amount=Decimal("50.00"),
            description="Sale",
            payment_method=PaymentMethod.CASH,
            created_by_user_id=test_admin_user.id
        )
        create_transaction(db_session, transaction_data, test_admin_user.id)
        
        # Close session
        update_data = CashRegisterSessionUpdate(
            final_balance=Decimal("150.00")
        )
        close_session(db_session, session.id, update_data)
        
        # Get daily summaries
        result = get_daily_summary_reports(
            db_session,
            restaurant_id=test_restaurant.id
        )
        
        assert len(result) == 1
        assert result[0].session_id == session.id
        assert result[0].total_sales == 50.0
        assert result[0].total_transactions == 1
    
    def test_get_daily_summary_filters_by_cashier(
        self, 
        db_session: Session, 
        test_restaurant, 
        test_admin_user
    ):
        """Test filtering daily summaries by cashier"""
        from app.models.user import User, UserRole
        
        # Create second user
        user2 = User(
            email="cashier2@test.com",
            full_name="Cashier Two",
            hashed_password="hashed",
            role=UserRole.STAFF,
            restaurant_id=test_restaurant.id
        )
        db_session.add(user2)
        db_session.commit()
        
        # Create sessions for both users
        session_data1 = CashRegisterSessionCreate(
            opened_by_user_id=test_admin_user.id,
            cashier_id=test_admin_user.id,
            initial_balance=Decimal("100.00")
        )
        session1 = create_session(db_session, session_data1, test_restaurant.id)
        update_data = CashRegisterSessionUpdate(final_balance=Decimal("100.00"))
        close_session(db_session, session1.id, update_data)
        
        session_data2 = CashRegisterSessionCreate(
            opened_by_user_id=user2.id,
            cashier_id=user2.id,
            initial_balance=Decimal("100.00")
        )
        session2 = create_session(db_session, session_data2, test_restaurant.id)
        close_session(db_session, session2.id, update_data)
        
        # Get reports for first cashier only
        result = get_daily_summary_reports(
            db_session,
            cashier_id=test_admin_user.id,
            restaurant_id=test_restaurant.id
        )
        
        assert len(result) == 1
        assert result[0].session_id == session1.id
