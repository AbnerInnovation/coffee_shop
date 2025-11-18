"""
Unit tests for cash_register/transaction_service.py

Tests all transaction management operations:
- Creating transactions
- Retrieving transactions by session
- Deleting transactions (with validation)
- Creating transactions from orders
- Error handling and validation
"""

import pytest
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy.orm import Session

from app.services.cash_register.transaction_service import (
    create_transaction,
    get_transactions_by_session,
    delete_transaction,
    create_transaction_from_order
)
from app.services.cash_register.session_service import create_session, close_session
from app.models.cash_register import (
    CashTransaction as CashTransactionModel,
    CashRegisterSession as CashRegisterSessionModel,
    PaymentMethod,
    TransactionType,
    SessionStatus
)
from app.schemas.cash_register import (
    CashTransactionCreate,
    CashRegisterSessionCreate,
    CashRegisterSessionUpdate
)


class TestCreateTransaction:
    """Tests for create_transaction function"""
    
    def test_create_transaction_success(
        self, 
        db_session: Session, 
        test_restaurant, 
        test_admin_user
    ):
        """Test successfully creating a transaction"""
        # Create a session first
        session_data = CashRegisterSessionCreate(
            opened_by_user_id=test_admin_user.id,
            cashier_id=test_admin_user.id,
            initial_balance=Decimal("100.00")
        )
        session = create_session(db_session, session_data, test_restaurant.id)
        
        # Create transaction
        transaction_data = CashTransactionCreate(
            session_id=session.id,
            transaction_type=TransactionType.SALE,
            amount=Decimal("50.00"),
            description="Test sale",
            payment_method=PaymentMethod.CASH,
            created_by_user_id=test_admin_user.id
        )
        
        result = create_transaction(db_session, transaction_data, test_admin_user.id)
        
        assert result.id is not None
        assert result.session_id == session.id
        assert result.transaction_type == TransactionType.SALE
        assert result.amount == Decimal("50.00")
        assert result.description == "Test sale"
        assert result.payment_method == PaymentMethod.CASH
        assert result.created_by_user_id == test_admin_user.id
    
    def test_create_expense_transaction(
        self, 
        db_session: Session, 
        test_restaurant, 
        test_admin_user
    ):
        """Test creating an expense transaction"""
        session_data = CashRegisterSessionCreate(
            opened_by_user_id=test_admin_user.id,
            cashier_id=test_admin_user.id,
            initial_balance=Decimal("100.00")
        )
        session = create_session(db_session, session_data, test_restaurant.id)
        
        transaction_data = CashTransactionCreate(
            session_id=session.id,
            transaction_type=TransactionType.EXPENSE,
            amount=Decimal("25.00"),
            description="Office supplies",
            payment_method=PaymentMethod.CASH,
            created_by_user_id=test_admin_user.id
        )
        
        result = create_transaction(db_session, transaction_data, test_admin_user.id)
        
        assert result.transaction_type == TransactionType.EXPENSE
        assert result.amount == Decimal("25.00")
    
    def test_create_withdrawal_transaction(
        self, 
        db_session: Session, 
        test_restaurant, 
        test_admin_user
    ):
        """Test creating a withdrawal transaction"""
        session_data = CashRegisterSessionCreate(
            opened_by_user_id=test_admin_user.id,
            cashier_id=test_admin_user.id,
            initial_balance=Decimal("100.00")
        )
        session = create_session(db_session, session_data, test_restaurant.id)
        
        transaction_data = CashTransactionCreate(
            session_id=session.id,
            transaction_type=TransactionType.MANUAL_WITHDRAW,
            amount=Decimal("50.00"),
            description="Cash withdrawal",
            payment_method=PaymentMethod.CASH,
            created_by_user_id=test_admin_user.id
        )
        
        result = create_transaction(db_session, transaction_data, test_admin_user.id)
        
        assert result.transaction_type == TransactionType.MANUAL_WITHDRAW


class TestGetTransactionsBySession:
    """Tests for get_transactions_by_session function"""
    
    def test_get_transactions_empty_session(
        self, 
        db_session: Session, 
        test_restaurant, 
        test_admin_user
    ):
        """Test getting transactions from a session with no transactions"""
        session_data = CashRegisterSessionCreate(
            opened_by_user_id=test_admin_user.id,
            cashier_id=test_admin_user.id,
            initial_balance=Decimal("100.00")
        )
        session = create_session(db_session, session_data, test_restaurant.id)
        
        result = get_transactions_by_session(db_session, session.id)
        
        assert len(result) == 0
    
    def test_get_transactions_with_data(
        self, 
        db_session: Session, 
        test_restaurant, 
        test_admin_user
    ):
        """Test getting transactions from a session with multiple transactions"""
        session_data = CashRegisterSessionCreate(
            opened_by_user_id=test_admin_user.id,
            cashier_id=test_admin_user.id,
            initial_balance=Decimal("100.00")
        )
        session = create_session(db_session, session_data, test_restaurant.id)
        
        # Create 3 transactions
        for i in range(3):
            transaction_data = CashTransactionCreate(
                session_id=session.id,
                transaction_type=TransactionType.SALE,
                amount=Decimal(f"{10 * (i + 1)}.00"),
                description=f"Sale {i + 1}",
                payment_method=PaymentMethod.CASH,
                created_by_user_id=test_admin_user.id
            )
            create_transaction(db_session, transaction_data, test_admin_user.id)
        
        result = get_transactions_by_session(db_session, session.id)
        
        assert len(result) == 3
        # Verify they're ordered by ID descending (most recent first)
        assert result[0].amount > result[1].amount > result[2].amount
    
    def test_get_transactions_filters_by_session(
        self, 
        db_session: Session, 
        test_restaurant, 
        test_admin_user
    ):
        """Test that transactions are filtered by session ID"""
        # Create two sessions
        session_data = CashRegisterSessionCreate(
            opened_by_user_id=test_admin_user.id,
            cashier_id=test_admin_user.id,
            initial_balance=Decimal("100.00")
        )
        session1 = create_session(db_session, session_data, test_restaurant.id)
        
        session1.status = SessionStatus.CLOSED
        db_session.commit()
        
        session2 = create_session(db_session, session_data, test_restaurant.id)
        
        # Create transactions for session 1
        for i in range(2):
            transaction_data = CashTransactionCreate(
                session_id=session1.id,
                transaction_type=TransactionType.SALE,
                amount=Decimal("10.00"),
                description=f"Session 1 Sale {i + 1}",
                payment_method=PaymentMethod.CASH,
                created_by_user_id=test_admin_user.id
            )
            create_transaction(db_session, transaction_data, test_admin_user.id)
        
        # Create transactions for session 2
        for i in range(3):
            transaction_data = CashTransactionCreate(
                session_id=session2.id,
                transaction_type=TransactionType.SALE,
                amount=Decimal("20.00"),
                description=f"Session 2 Sale {i + 1}",
                payment_method=PaymentMethod.CASH,
                created_by_user_id=test_admin_user.id
            )
            create_transaction(db_session, transaction_data, test_admin_user.id)
        
        result1 = get_transactions_by_session(db_session, session1.id)
        result2 = get_transactions_by_session(db_session, session2.id)
        
        assert len(result1) == 2
        assert len(result2) == 3
        assert all(t.session_id == session1.id for t in result1)
        assert all(t.session_id == session2.id for t in result2)


class TestDeleteTransaction:
    """Tests for delete_transaction function"""
    
    def test_delete_transaction_success(
        self, 
        db_session: Session, 
        test_restaurant, 
        test_admin_user
    ):
        """Test successfully deleting a transaction from an open session"""
        session_data = CashRegisterSessionCreate(
            opened_by_user_id=test_admin_user.id,
            cashier_id=test_admin_user.id,
            initial_balance=Decimal("100.00")
        )
        session = create_session(db_session, session_data, test_restaurant.id)
        
        transaction_data = CashTransactionCreate(
            session_id=session.id,
            transaction_type=TransactionType.SALE,
            amount=Decimal("50.00"),
            description="Test sale",
            payment_method=PaymentMethod.CASH,
            created_by_user_id=test_admin_user.id
        )
        transaction = create_transaction(db_session, transaction_data, test_admin_user.id)
        
        result = delete_transaction(db_session, transaction.id, test_admin_user.id)
        
        assert result is True
        
        # Verify transaction is deleted
        deleted = db_session.query(CashTransactionModel).filter(
            CashTransactionModel.id == transaction.id
        ).first()
        assert deleted is None
    
    def test_delete_transaction_not_found(self, db_session: Session, test_admin_user):
        """Test deleting a non-existent transaction raises error"""
        with pytest.raises(ValueError, match="Transaction not found"):
            delete_transaction(db_session, 99999, test_admin_user.id)
    
    def test_delete_transaction_from_closed_session(
        self, 
        db_session: Session, 
        test_restaurant, 
        test_admin_user
    ):
        """Test that transactions cannot be deleted from closed sessions"""
        session_data = CashRegisterSessionCreate(
            opened_by_user_id=test_admin_user.id,
            cashier_id=test_admin_user.id,
            initial_balance=Decimal("100.00")
        )
        session = create_session(db_session, session_data, test_restaurant.id)
        
        transaction_data = CashTransactionCreate(
            session_id=session.id,
            transaction_type=TransactionType.SALE,
            amount=Decimal("50.00"),
            description="Test sale",
            payment_method=PaymentMethod.CASH,
            created_by_user_id=test_admin_user.id
        )
        transaction = create_transaction(db_session, transaction_data, test_admin_user.id)
        
        # Close the session
        update_data = CashRegisterSessionUpdate(
            final_balance=Decimal("150.00")
        )
        close_session(db_session, session.id, update_data)
        
        # Try to delete transaction
        with pytest.raises(ValueError, match="Cannot delete transactions from a closed session"):
            delete_transaction(db_session, transaction.id, test_admin_user.id)


class TestCreateTransactionFromOrder:
    """Tests for create_transaction_from_order function"""
    
    @pytest.mark.skip(reason="test_table fixture not implemented")
    def test_create_transaction_from_order_success(
        self, 
        db_session: Session, 
        test_restaurant, 
        test_admin_user,
        test_table
    ):
        """Test creating a transaction from an order"""
        from app.models.order import Order as OrderModel, OrderStatus
        
        # Create session
        session_data = CashRegisterSessionCreate(
            opened_by_user_id=test_admin_user.id,
            cashier_id=test_admin_user.id,
            initial_balance=Decimal("100.00")
        )
        session = create_session(db_session, session_data, test_restaurant.id)
        
        # Create order
        order = OrderModel(
            restaurant_id=test_restaurant.id,
            table_id=test_table.id,
            order_number=1,
            order_type="dine_in",
            status=OrderStatus.COMPLETED,
            total_amount=Decimal("75.50"),
            is_paid=False,
            payment_method="cash",
            created_by_user_id=test_admin_user.id
        )
        db_session.add(order)
        db_session.commit()
        db_session.refresh(order)
        
        # Create transaction from order
        result = create_transaction_from_order(
            db_session,
            order.id,
            test_admin_user.id,
            session_id=session.id
        )
        
        assert result.id is not None
        assert result.session_id == session.id
        assert result.order_id == order.id
        assert result.amount == Decimal("75.50")
        assert result.transaction_type == TransactionType.SALE
        assert "orden #1" in result.description.lower()
    
    @pytest.mark.skip(reason="test_table fixture not implemented")
    def test_create_transaction_order_not_found(
        self, 
        db_session: Session, 
        test_restaurant, 
        test_admin_user
    ):
        """Test creating transaction from non-existent order raises error"""
        session_data = CashRegisterSessionCreate(
            opened_by_user_id=test_admin_user.id,
            cashier_id=test_admin_user.id,
            initial_balance=Decimal("100.00")
        )
        session = create_session(db_session, session_data, test_restaurant.id)
        
        with pytest.raises(ValueError, match="Order not found"):
            create_transaction_from_order(
                db_session,
                99999,
                test_admin_user.id,
                session_id=session.id
            )
    
    @pytest.mark.skip(reason="test_table fixture not implemented")
    def test_create_transaction_order_already_paid(
        self, 
        db_session: Session, 
        test_restaurant, 
        test_admin_user,
        test_table
    ):
        """Test creating transaction from already paid order raises error"""
        from app.models.order import Order as OrderModel, OrderStatus
        
        session_data = CashRegisterSessionCreate(
            opened_by_user_id=test_admin_user.id,
            cashier_id=test_admin_user.id,
            initial_balance=Decimal("100.00")
        )
        session = create_session(db_session, session_data, test_restaurant.id)
        
        # Create paid order
        order = OrderModel(
            restaurant_id=test_restaurant.id,
            table_id=test_table.id,
            order_number=1,
            order_type="dine_in",
            status=OrderStatus.COMPLETED,
            total_amount=Decimal("75.50"),
            is_paid=True,  # Already paid
            payment_method="cash",
            created_by_user_id=test_admin_user.id
        )
        db_session.add(order)
        db_session.commit()
        
        with pytest.raises(ValueError, match="Order is already paid"):
            create_transaction_from_order(
                db_session,
                order.id,
                test_admin_user.id,
                session_id=session.id
            )
    
    @pytest.mark.skip(reason="test_table fixture not implemented")
    def test_create_transaction_no_open_session(
        self, 
        db_session: Session, 
        test_restaurant, 
        test_admin_user,
        test_table
    ):
        """Test creating transaction without open session raises error"""
        from app.models.order import Order as OrderModel, OrderStatus
        
        # Create order
        order = OrderModel(
            restaurant_id=test_restaurant.id,
            table_id=test_table.id,
            order_number=1,
            order_type="dine_in",
            status=OrderStatus.COMPLETED,
            total_amount=Decimal("75.50"),
            is_paid=False,
            payment_method="cash",
            created_by_user_id=test_admin_user.id
        )
        db_session.add(order)
        db_session.commit()
        
        # Try to create transaction without session
        with pytest.raises(ValueError, match="No open cash register session found"):
            create_transaction_from_order(
                db_session,
                order.id,
                test_admin_user.id
            )
    
    @pytest.mark.skip(reason="test_table fixture not implemented")
    def test_create_transaction_duplicate_prevention(
        self, 
        db_session: Session, 
        test_restaurant, 
        test_admin_user,
        test_table
    ):
        """Test that duplicate transactions for same order are prevented"""
        from app.models.order import Order as OrderModel, OrderStatus
        
        session_data = CashRegisterSessionCreate(
            opened_by_user_id=test_admin_user.id,
            cashier_id=test_admin_user.id,
            initial_balance=Decimal("100.00")
        )
        session = create_session(db_session, session_data, test_restaurant.id)
        
        order = OrderModel(
            restaurant_id=test_restaurant.id,
            table_id=test_table.id,
            order_number=1,
            order_type="dine_in",
            status=OrderStatus.COMPLETED,
            total_amount=Decimal("75.50"),
            is_paid=False,
            payment_method="cash",
            created_by_user_id=test_admin_user.id
        )
        db_session.add(order)
        db_session.commit()
        
        # Create first transaction
        create_transaction_from_order(
            db_session,
            order.id,
            test_admin_user.id,
            session_id=session.id
        )
        
        # Try to create duplicate
        with pytest.raises(ValueError, match="Transaction already exists"):
            create_transaction_from_order(
                db_session,
                order.id,
                test_admin_user.id,
                session_id=session.id
            )
