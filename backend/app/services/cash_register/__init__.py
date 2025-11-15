"""
Cash Register Service Module

This module provides specialized services for cash register operations:
- session_service: Session management (open, close, get)
- transaction_service: Transaction operations (create, delete)
- report_service: Report generation (daily, weekly, cash difference)
- calculation_service: Financial calculations and aggregations
- denomination_service: Cash denomination counting
"""

from .session_service import (
    create_session,
    get_session,
    get_current_session,
    get_sessions,
    close_session,
    close_session_with_denominations,
)

from .transaction_service import (
    create_transaction,
    get_transactions_by_session,
    delete_transaction,
    create_transaction_from_order,
)

from .report_service import (
    get_reports,
    cut_session,
    get_last_cut,
    get_daily_summary_reports,
    get_weekly_summary,
    generate_cash_difference_report,
)

from .calculation_service import (
    calculate_expected_balance,
    calculate_session_totals,
)

from .denomination_service import (
    add_expense_to_session,
)

__all__ = [
    # Session operations
    'create_session',
    'get_session',
    'get_current_session',
    'get_sessions',
    'close_session',
    'close_session_with_denominations',
    
    # Transaction operations
    'create_transaction',
    'get_transactions_by_session',
    'delete_transaction',
    'create_transaction_from_order',
    
    # Report operations
    'get_reports',
    'cut_session',
    'get_last_cut',
    'get_daily_summary_reports',
    'get_weekly_summary',
    'generate_cash_difference_report',
    
    # Calculation operations
    'calculate_expected_balance',
    'calculate_session_totals',
    
    # Expense operations
    'add_expense_to_session',
]
