"""
Unit tests for cash_register/calculation_service.py

Tests all financial calculation operations:
- Expected balance calculations
- Session totals (sales, refunds, tips, expenses)
- Payment method breakdowns
- Cash difference calculations
- Multi-session aggregations
"""

import pytest
from decimal import Decimal
from sqlalchemy.orm import Session

from app.services.cash_register.calculation_service import (
    calculate_expected_balance,
    calculate_session_totals,
    calculate_payment_breakdown,
    calculate_cash_difference,
    aggregate_session_totals
)
from app.services.cash_register.session_service import create_session
from app.services.cash_register.transaction_service import create_transaction
from app.models.cash_register import (
    TransactionType,
    PaymentMethod
)
from app.schemas.cash_register import (
    CashRegisterSessionCreate,
    CashTransactionCreate
)


class TestCalculateExpectedBalance:
    """Tests for calculate_expected_balance function"""
    
    def test_expected_balance_no_transactions(
        self, 
        db_session: Session, 
        test_restaurant, 
        test_admin_user
    ):
        """Test expected balance equals initial balance when no transactions"""
        session_data = CashRegisterSessionCreate(
            opened_by_user_id=test_admin_user.id,
            cashier_id=test_admin_user.id,
            initial_balance=Decimal("100.00")
        )
        session = create_session(db_session, session_data, test_restaurant.id)
        
        result = calculate_expected_balance(db_session, session.id, 100.00)
        
        assert result == 100.00
    
    def test_expected_balance_with_sales(
        self, 
        db_session: Session, 
        test_restaurant, 
        test_admin_user
    ):
        """Test expected balance increases with sales"""
        session_data = CashRegisterSessionCreate(
            opened_by_user_id=test_admin_user.id,
            cashier_id=test_admin_user.id,
            initial_balance=Decimal("100.00")
        )
        session = create_session(db_session, session_data, test_restaurant.id)
        
        # Add sales
        for amount in [50.00, 75.00, 25.00]:
            transaction_data = CashTransactionCreate(
                session_id=session.id,
                transaction_type=TransactionType.SALE,
                amount=Decimal(str(amount)),
                description="Sale",
                payment_method=PaymentMethod.CASH,
                created_by_user_id=test_admin_user.id
            )
            create_transaction(db_session, transaction_data, test_admin_user.id)
        
        result = calculate_expected_balance(db_session, session.id, 100.00)
        
        # 100 + 50 + 75 + 25 = 250
        assert result == 250.00
    
    def test_expected_balance_with_expenses(
        self, 
        db_session: Session, 
        test_restaurant, 
        test_admin_user
    ):
        """Test expected balance decreases with expenses"""
        session_data = CashRegisterSessionCreate(
            opened_by_user_id=test_admin_user.id,
            cashier_id=test_admin_user.id,
            initial_balance=Decimal("100.00")
        )
        session = create_session(db_session, session_data, test_restaurant.id)
        
        # Add expense (negative amount)
        transaction_data = CashTransactionCreate(
            session_id=session.id,
            transaction_type=TransactionType.EXPENSE,
            amount=Decimal("-30.00"),
            description="Expense",
            payment_method=PaymentMethod.CASH,
            created_by_user_id=test_admin_user.id
        )
        create_transaction(db_session, transaction_data, test_admin_user.id)
        
        result = calculate_expected_balance(db_session, session.id, 100.00)
        
        # 100 - 30 = 70
        assert result == 70.00
    
    def test_expected_balance_mixed_transactions(
        self, 
        db_session: Session, 
        test_restaurant, 
        test_admin_user
    ):
        """Test expected balance with mixed transaction types"""
        session_data = CashRegisterSessionCreate(
            opened_by_user_id=test_admin_user.id,
            cashier_id=test_admin_user.id,
            initial_balance=Decimal("100.00")
        )
        session = create_session(db_session, session_data, test_restaurant.id)
        
        # Add various transactions
        transactions = [
            (TransactionType.SALE, Decimal("50.00")),
            (TransactionType.TIP, Decimal("10.00")),
            (TransactionType.EXPENSE, Decimal("-20.00")),
            (TransactionType.REFUND, Decimal("-15.00")),
        ]
        
        for trans_type, amount in transactions:
            transaction_data = CashTransactionCreate(
                session_id=session.id,
                transaction_type=trans_type,
                amount=amount,
                description="Transaction",
                payment_method=PaymentMethod.CASH,
                created_by_user_id=test_admin_user.id
            )
            create_transaction(db_session, transaction_data, test_admin_user.id)
        
        result = calculate_expected_balance(db_session, session.id, 100.00)
        
        # 100 + 50 + 10 - 20 - 15 = 125
        assert result == 125.00


class TestCalculateSessionTotals:
    """Tests for calculate_session_totals function"""
    
    def test_session_totals_empty_session(
        self, 
        db_session: Session, 
        test_restaurant, 
        test_admin_user
    ):
        """Test totals for session with no transactions"""
        session_data = CashRegisterSessionCreate(
            opened_by_user_id=test_admin_user.id,
            cashier_id=test_admin_user.id,
            initial_balance=Decimal("100.00")
        )
        session = create_session(db_session, session_data, test_restaurant.id)
        
        sales, refunds, tips, expenses, net = calculate_session_totals(
            db_session, 
            session.id
        )
        
        assert sales == 0.0
        assert refunds == 0.0
        assert tips == 0.0
        assert expenses == 0.0
        assert net == 0.0
    
    def test_session_totals_with_sales(
        self, 
        db_session: Session, 
        test_restaurant, 
        test_admin_user
    ):
        """Test totals calculation with sales only"""
        session_data = CashRegisterSessionCreate(
            opened_by_user_id=test_admin_user.id,
            cashier_id=test_admin_user.id,
            initial_balance=Decimal("100.00")
        )
        session = create_session(db_session, session_data, test_restaurant.id)
        
        # Add sales
        for amount in [50.00, 75.00, 25.00]:
            transaction_data = CashTransactionCreate(
                session_id=session.id,
                transaction_type=TransactionType.SALE,
                amount=Decimal(str(amount)),
                description="Sale",
                payment_method=PaymentMethod.CASH,
                created_by_user_id=test_admin_user.id
            )
            create_transaction(db_session, transaction_data, test_admin_user.id)
        
        sales, refunds, tips, expenses, net = calculate_session_totals(
            db_session, 
            session.id
        )
        
        assert sales == 150.0  # 50 + 75 + 25
        assert refunds == 0.0
        assert tips == 0.0
        assert expenses == 0.0
        assert net == 150.0
    
    def test_session_totals_all_types(
        self, 
        db_session: Session, 
        test_restaurant, 
        test_admin_user
    ):
        """Test totals with all transaction types"""
        session_data = CashRegisterSessionCreate(
            opened_by_user_id=test_admin_user.id,
            cashier_id=test_admin_user.id,
            initial_balance=Decimal("100.00")
        )
        session = create_session(db_session, session_data, test_restaurant.id)
        
        # Add various transactions
        transactions = [
            (TransactionType.SALE, Decimal("100.00")),
            (TransactionType.SALE, Decimal("50.00")),
            (TransactionType.TIP, Decimal("15.00")),
            (TransactionType.REFUND, Decimal("-20.00")),
            (TransactionType.EXPENSE, Decimal("-10.00")),
        ]
        
        for trans_type, amount in transactions:
            transaction_data = CashTransactionCreate(
                session_id=session.id,
                transaction_type=trans_type,
                amount=amount,
                description="Transaction",
                payment_method=PaymentMethod.CASH,
                created_by_user_id=test_admin_user.id
            )
            create_transaction(db_session, transaction_data, test_admin_user.id)
        
        sales, refunds, tips, expenses, net = calculate_session_totals(
            db_session, 
            session.id
        )
        
        assert sales == 150.0  # 100 + 50
        assert refunds == 20.0  # abs(-20)
        assert tips == 15.0
        assert expenses == 10.0  # abs(-10)
        assert net == 135.0  # 150 - 20 + 15 - 10


class TestCalculatePaymentBreakdown:
    """Tests for calculate_payment_breakdown function"""
    
    def test_payment_breakdown_empty_session(
        self, 
        db_session: Session, 
        test_restaurant, 
        test_admin_user
    ):
        """Test payment breakdown for empty session"""
        session_data = CashRegisterSessionCreate(
            opened_by_user_id=test_admin_user.id,
            cashier_id=test_admin_user.id,
            initial_balance=Decimal("100.00")
        )
        session = create_session(db_session, session_data, test_restaurant.id)
        
        result = calculate_payment_breakdown(db_session, session.id)
        
        assert result == {
            "cash": 0.0,
            "card": 0.0,
            "digital": 0.0,
            "other": 0.0
        }
    
    def test_payment_breakdown_cash_only(
        self, 
        db_session: Session, 
        test_restaurant, 
        test_admin_user
    ):
        """Test payment breakdown with cash transactions only"""
        session_data = CashRegisterSessionCreate(
            opened_by_user_id=test_admin_user.id,
            cashier_id=test_admin_user.id,
            initial_balance=Decimal("100.00")
        )
        session = create_session(db_session, session_data, test_restaurant.id)
        
        # Add cash transactions
        for amount in [50.00, 75.00]:
            transaction_data = CashTransactionCreate(
                session_id=session.id,
                transaction_type=TransactionType.SALE,
                amount=Decimal(str(amount)),
                description="Cash sale",
                payment_method=PaymentMethod.CASH,
                created_by_user_id=test_admin_user.id
            )
            create_transaction(db_session, transaction_data, test_admin_user.id)
        
        result = calculate_payment_breakdown(db_session, session.id)
        
        assert result["cash"] == 125.0
        assert result["card"] == 0.0
        assert result["digital"] == 0.0
    
    def test_payment_breakdown_mixed_methods(
        self, 
        db_session: Session, 
        test_restaurant, 
        test_admin_user
    ):
        """Test payment breakdown with multiple payment methods"""
        session_data = CashRegisterSessionCreate(
            opened_by_user_id=test_admin_user.id,
            cashier_id=test_admin_user.id,
            initial_balance=Decimal("100.00")
        )
        session = create_session(db_session, session_data, test_restaurant.id)
        
        # Add transactions with different payment methods
        transactions = [
            (PaymentMethod.CASH, Decimal("50.00")),
            (PaymentMethod.CASH, Decimal("30.00")),
            (PaymentMethod.CARD, Decimal("75.00")),
            (PaymentMethod.DIGITAL, Decimal("25.00")),
        ]
        
        for payment_method, amount in transactions:
            transaction_data = CashTransactionCreate(
                session_id=session.id,
                transaction_type=TransactionType.SALE,
                amount=amount,
                description="Sale",
                payment_method=payment_method,
                created_by_user_id=test_admin_user.id
            )
            create_transaction(db_session, transaction_data, test_admin_user.id)
        
        result = calculate_payment_breakdown(db_session, session.id)
        
        assert result["cash"] == 80.0  # 50 + 30
        assert result["card"] == 75.0
        assert result["digital"] == 25.0
        assert result["other"] == 0.0


class TestCalculateCashDifference:
    """Tests for calculate_cash_difference function"""
    
    def test_cash_difference_exact_match(self):
        """Test when expected and actual balance match"""
        result = calculate_cash_difference(100.00, 100.00)
        assert result == 0.0
    
    def test_cash_difference_surplus(self):
        """Test when actual balance is higher (surplus)"""
        result = calculate_cash_difference(100.00, 110.00)
        assert result == 10.0
    
    def test_cash_difference_shortage(self):
        """Test when actual balance is lower (shortage)"""
        result = calculate_cash_difference(100.00, 95.00)
        assert result == -5.0
    
    def test_cash_difference_large_amounts(self):
        """Test with large amounts"""
        result = calculate_cash_difference(5000.00, 5025.50)
        assert result == 25.50


class TestAggregateSessionTotals:
    """Tests for aggregate_session_totals function"""
    
    def test_aggregate_empty_list(self):
        """Test aggregating empty session list"""
        result = aggregate_session_totals([])
        
        sales, refunds, tips, expenses, transactions, breakdown = result
        
        assert sales == 0.0
        assert refunds == 0.0
        assert tips == 0.0
        assert expenses == 0.0
        assert transactions == 0
        assert breakdown == {"cash": 0.0, "card": 0.0, "digital": 0.0, "other": 0.0}
    
    def test_aggregate_single_session(self):
        """Test aggregating a single session"""
        sessions = [
            {
                'total_sales': 100.0,
                'total_refunds': 10.0,
                'total_tips': 15.0,
                'total_expenses': 5.0,
                'total_transactions': 10,
                'payment_breakdown': {
                    'cash': 80.0,
                    'card': 20.0,
                    'digital': 0.0,
                    'other': 0.0
                }
            }
        ]
        
        result = aggregate_session_totals(sessions)
        sales, refunds, tips, expenses, transactions, breakdown = result
        
        assert sales == 100.0
        assert refunds == 10.0
        assert tips == 15.0
        assert expenses == 5.0
        assert transactions == 10
        assert breakdown['cash'] == 80.0
        assert breakdown['card'] == 20.0
    
    def test_aggregate_multiple_sessions(self):
        """Test aggregating multiple sessions"""
        sessions = [
            {
                'total_sales': 100.0,
                'total_refunds': 10.0,
                'total_tips': 15.0,
                'total_expenses': 5.0,
                'total_transactions': 10,
                'payment_breakdown': {
                    'cash': 80.0,
                    'card': 20.0,
                    'digital': 0.0,
                    'other': 0.0
                }
            },
            {
                'total_sales': 200.0,
                'total_refunds': 20.0,
                'total_tips': 25.0,
                'total_expenses': 10.0,
                'total_transactions': 15,
                'payment_breakdown': {
                    'cash': 150.0,
                    'card': 50.0,
                    'digital': 0.0,
                    'other': 0.0
                }
            },
            {
                'total_sales': 150.0,
                'total_refunds': 5.0,
                'total_tips': 20.0,
                'total_expenses': 8.0,
                'total_transactions': 12,
                'payment_breakdown': {
                    'cash': 100.0,
                    'card': 30.0,
                    'digital': 20.0,
                    'other': 0.0
                }
            }
        ]
        
        result = aggregate_session_totals(sessions)
        sales, refunds, tips, expenses, transactions, breakdown = result
        
        assert sales == 450.0  # 100 + 200 + 150
        assert refunds == 35.0  # 10 + 20 + 5
        assert tips == 60.0  # 15 + 25 + 20
        assert expenses == 23.0  # 5 + 10 + 8
        assert transactions == 37  # 10 + 15 + 12
        assert breakdown['cash'] == 330.0  # 80 + 150 + 100
        assert breakdown['card'] == 100.0  # 20 + 50 + 30
        assert breakdown['digital'] == 20.0  # 0 + 0 + 20
        assert breakdown['other'] == 0.0
    
    def test_aggregate_handles_missing_fields(self):
        """Test that aggregation handles missing fields gracefully"""
        sessions = [
            {
                'total_sales': 100.0,
                # Missing other fields
            },
            {
                'total_sales': 200.0,
                'total_refunds': 20.0,
                # Missing other fields
            }
        ]
        
        result = aggregate_session_totals(sessions)
        sales, refunds, tips, expenses, transactions, breakdown = result
        
        assert sales == 300.0
        assert refunds == 20.0
        assert tips == 0.0  # Default value
        assert expenses == 0.0  # Default value
        assert transactions == 0  # Default value
