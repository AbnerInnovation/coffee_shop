"""
Unit tests for cash_register/denomination_service.py

Tests expense and denomination management operations:
- Adding expenses to sessions
- Expense categorization
- Validation (session must be open)
"""

import pytest
from decimal import Decimal
from sqlalchemy.orm import Session

from app.services.cash_register.denomination_service import add_expense_to_session
from app.services.cash_register.session_service import create_session, close_session
from app.models.cash_register import TransactionType
from app.schemas.cash_register import (
    CashRegisterSessionCreate,
    CashRegisterSessionUpdate
)


class TestAddExpenseToSession:
    """Tests for add_expense_to_session function"""
    
    def test_add_expense_success(
        self, 
        db_session: Session, 
        test_restaurant, 
        test_admin_user
    ):
        """Test successfully adding an expense to an open session"""
        session_data = CashRegisterSessionCreate(
            opened_by_user_id=test_admin_user.id,
            cashier_id=test_admin_user.id,
            initial_balance=Decimal("100.00")
        )
        session = create_session(db_session, session_data, test_restaurant.id)
        
        result = add_expense_to_session(
            db_session,
            session.id,
            25.00,
            "Office supplies",
            test_admin_user.id
        )
        
        assert result.id is not None
        assert result.session_id == session.id
        assert result.transaction_type == TransactionType.EXPENSE
        assert result.amount == -25.00  # Negative for expense
        assert result.description == "Office supplies"
        assert result.created_by_user_id == test_admin_user.id
    
    def test_add_expense_with_category(
        self, 
        db_session: Session, 
        test_restaurant, 
        test_admin_user
    ):
        """Test adding expense with category"""
        session_data = CashRegisterSessionCreate(
            opened_by_user_id=test_admin_user.id,
            cashier_id=test_admin_user.id,
            initial_balance=Decimal("100.00")
        )
        session = create_session(db_session, session_data, test_restaurant.id)
        
        result = add_expense_to_session(
            db_session,
            session.id,
            50.00,
            "Cleaning products",
            test_admin_user.id,
            category="Maintenance"
        )
        
        assert "[Maintenance]" in result.description
        assert "Cleaning products" in result.description
    
    def test_add_expense_ensures_negative_amount(
        self, 
        db_session: Session, 
        test_restaurant, 
        test_admin_user
    ):
        """Test that expense amount is always negative even if positive provided"""
        session_data = CashRegisterSessionCreate(
            opened_by_user_id=test_admin_user.id,
            cashier_id=test_admin_user.id,
            initial_balance=Decimal("100.00")
        )
        session = create_session(db_session, session_data, test_restaurant.id)
        
        # Pass positive amount
        result = add_expense_to_session(
            db_session,
            session.id,
            30.00,  # Positive
            "Test expense",
            test_admin_user.id
        )
        
        # Should be converted to negative
        assert result.amount == -30.00
    
    def test_add_expense_session_not_found(self, db_session: Session, test_admin_user):
        """Test adding expense to non-existent session raises error"""
        with pytest.raises(ValueError, match="Session not found"):
            add_expense_to_session(
                db_session,
                99999,
                25.00,
                "Test expense",
                test_admin_user.id
            )
    
    def test_add_expense_to_closed_session(
        self, 
        db_session: Session, 
        test_restaurant, 
        test_admin_user
    ):
        """Test that expenses cannot be added to closed sessions"""
        session_data = CashRegisterSessionCreate(
            opened_by_user_id=test_admin_user.id,
            cashier_id=test_admin_user.id,
            initial_balance=Decimal("100.00")
        )
        session = create_session(db_session, session_data, test_restaurant.id)
        
        # Close the session
        update_data = CashRegisterSessionUpdate(
            final_balance=Decimal("150.00")
        )
        close_session(db_session, session.id, update_data)
        
        # Try to add expense
        with pytest.raises(ValueError, match="Cannot add expenses to a closed session"):
            add_expense_to_session(
                db_session,
                session.id,
                25.00,
                "Test expense",
                test_admin_user.id
            )
    
    def test_add_multiple_expenses(
        self, 
        db_session: Session, 
        test_restaurant, 
        test_admin_user
    ):
        """Test adding multiple expenses to same session"""
        session_data = CashRegisterSessionCreate(
            opened_by_user_id=test_admin_user.id,
            cashier_id=test_admin_user.id,
            initial_balance=Decimal("100.00")
        )
        session = create_session(db_session, session_data, test_restaurant.id)
        
        expenses = [
            ("Office supplies", 25.00, "Supplies"),
            ("Cleaning", 30.00, "Maintenance"),
            ("Repairs", 45.00, "Maintenance"),
        ]
        
        results = []
        for description, amount, category in expenses:
            result = add_expense_to_session(
                db_session,
                session.id,
                amount,
                description,
                test_admin_user.id,
                category=category
            )
            results.append(result)
        
        assert len(results) == 3
        assert all(r.transaction_type == TransactionType.EXPENSE for r in results)
        assert sum(r.amount for r in results) == -100.00  # Total expenses
