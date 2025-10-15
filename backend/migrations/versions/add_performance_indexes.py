"""add_performance_indexes

Revision ID: f1a2b3c4d5e6
Revises: add_discount_price_menu
Create Date: 2025-10-15 12:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f1a2b3c4d5e6'
down_revision: Union[str, None] = 'add_discount_price_menu'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Get database connection to check existing indexes
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    
    # Get list of existing tables
    existing_tables = inspector.get_table_names()
    
    # Helper function to create index if table and index don't exist
    def create_index_if_not_exists(index_name, table_name, columns):
        # Check if table exists first
        if table_name not in existing_tables:
            return
        
        existing_indexes = {idx['name'] for idx in inspector.get_indexes(table_name)}
        if index_name not in existing_indexes:
            op.create_index(index_name, table_name, columns, unique=False)
    
    # Orders table indexes
    create_index_if_not_exists('idx_order_restaurant_status', 'orders', ['restaurant_id', 'status'])
    create_index_if_not_exists('idx_order_restaurant_created', 'orders', ['restaurant_id', 'created_at'])
    create_index_if_not_exists('idx_order_table_id', 'orders', ['table_id'])
    
    # Menu items table indexes
    create_index_if_not_exists('idx_menuitem_restaurant_category', 'menu_items', ['restaurant_id', 'category_id'])
    create_index_if_not_exists('idx_menuitem_restaurant_available', 'menu_items', ['restaurant_id', 'is_available'])
    
    # Users table indexes (skip if already exists from multi-restaurant migration)
    if 'users' in existing_tables:
        existing_user_indexes = {idx['name'] for idx in inspector.get_indexes('users')}
        if 'idx_user_restaurant' not in existing_user_indexes and 'ix_users_restaurant_id' not in existing_user_indexes:
            op.create_index('idx_user_restaurant', 'users', ['restaurant_id'], unique=False)
    
    # Tables table indexes (skip if already exists from multi-restaurant migration)
    if 'tables' in existing_tables:
        existing_table_indexes = {idx['name'] for idx in inspector.get_indexes('tables')}
        if 'idx_table_restaurant' not in existing_table_indexes and 'ix_tables_restaurant_id' not in existing_table_indexes:
            op.create_index('idx_table_restaurant', 'tables', ['restaurant_id'], unique=False)
    
    # Order items table indexes
    create_index_if_not_exists('idx_orderitem_order', 'order_items', ['order_id'])
    create_index_if_not_exists('idx_orderitem_menuitem', 'order_items', ['menu_item_id'])
    
    # Cash register sessions indexes (only if table and columns exist)
    if 'cash_register_sessions' in existing_tables:
        session_cols = [c['name'] for c in inspector.get_columns('cash_register_sessions')]
        if 'opened_by_user_id' in session_cols:
            create_index_if_not_exists('idx_cashsession_user', 'cash_register_sessions', ['opened_by_user_id'])
    
    # Cash transactions indexes (only if table exists)
    create_index_if_not_exists('idx_cashtransaction_session', 'cash_transactions', ['session_id'])
    create_index_if_not_exists('idx_cashtransaction_order', 'cash_transactions', ['order_id'])
    
    # CRITICAL: Soft delete indexes - queries filter on deleted_at IS NULL frequently
    create_index_if_not_exists('idx_order_deleted', 'orders', ['deleted_at'])
    create_index_if_not_exists('idx_menuitem_deleted', 'menu_items', ['deleted_at'])
    create_index_if_not_exists('idx_orderitem_deleted', 'order_items', ['deleted_at'])
    create_index_if_not_exists('idx_category_deleted', 'categories', ['deleted_at'])
    
    # IMPORTANT: Composite indexes for common query patterns
    # Orders filtered by restaurant + deleted_at (very common pattern)
    create_index_if_not_exists('idx_order_restaurant_deleted', 'orders', ['restaurant_id', 'deleted_at'])
    
    # Menu items filtered by restaurant + deleted_at
    create_index_if_not_exists('idx_menuitem_restaurant_deleted', 'menu_items', ['restaurant_id', 'deleted_at'])
    
    # Categories filtered by restaurant + deleted_at
    create_index_if_not_exists('idx_category_restaurant_deleted', 'categories', ['restaurant_id', 'deleted_at'])
    
    # Cash register sessions filtered by status (for finding open sessions)
    create_index_if_not_exists('idx_cashsession_status', 'cash_register_sessions', ['status'])
    
    # Cash register sessions filtered by user + status (get_current_session query)
    create_index_if_not_exists('idx_cashsession_user_status', 'cash_register_sessions', ['opened_by_user_id', 'status'])
    
    # Cash register sessions ordered by opened_at (for reports)
    create_index_if_not_exists('idx_cashsession_opened', 'cash_register_sessions', ['opened_at'])
    
    # Cash register sessions filtered by closed_at (for date range queries in reports)
    create_index_if_not_exists('idx_cashsession_closed', 'cash_register_sessions', ['closed_at'])
    
    # Cash register sessions by status + closed_at (daily summary reports)
    create_index_if_not_exists('idx_cashsession_status_closed', 'cash_register_sessions', ['status', 'closed_at'])
    
    # Cash register reports filtered by session + type
    create_index_if_not_exists('idx_cashreport_session_type', 'cash_register_reports', ['session_id', 'report_type'])
    
    # Cash register reports ordered by generated_at (for finding last cut)
    create_index_if_not_exists('idx_cashreport_generated', 'cash_register_reports', ['generated_at'])
    
    # Cash transactions filtered by payment_method (for payment breakdown)
    create_index_if_not_exists('idx_cashtransaction_payment', 'cash_transactions', ['payment_method'])
    
    # Orders filtered by is_paid (for finding unpaid orders)
    create_index_if_not_exists('idx_order_paid', 'orders', ['is_paid'])


def downgrade() -> None:
    # Get database connection to check existing indexes
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    
    # Get list of existing tables
    existing_tables = inspector.get_table_names()
    
    # Helper function to drop index if table and index exist
    def drop_index_if_exists(index_name, table_name):
        # Check if table exists first
        if table_name not in existing_tables:
            return
        
        existing_indexes = {idx['name'] for idx in inspector.get_indexes(table_name)}
        if index_name in existing_indexes:
            op.drop_index(index_name, table_name=table_name)
    
    # Drop all indexes in reverse order (only if they exist)
    drop_index_if_exists('idx_order_paid', 'orders')
    drop_index_if_exists('idx_cashtransaction_payment', 'cash_transactions')
    drop_index_if_exists('idx_cashreport_generated', 'cash_register_reports')
    drop_index_if_exists('idx_cashreport_session_type', 'cash_register_reports')
    drop_index_if_exists('idx_cashsession_status_closed', 'cash_register_sessions')
    drop_index_if_exists('idx_cashsession_closed', 'cash_register_sessions')
    drop_index_if_exists('idx_cashsession_opened', 'cash_register_sessions')
    drop_index_if_exists('idx_cashsession_user_status', 'cash_register_sessions')
    drop_index_if_exists('idx_cashsession_status', 'cash_register_sessions')
    drop_index_if_exists('idx_category_restaurant_deleted', 'categories')
    drop_index_if_exists('idx_menuitem_restaurant_deleted', 'menu_items')
    drop_index_if_exists('idx_order_restaurant_deleted', 'orders')
    drop_index_if_exists('idx_category_deleted', 'categories')
    drop_index_if_exists('idx_orderitem_deleted', 'order_items')
    drop_index_if_exists('idx_menuitem_deleted', 'menu_items')
    drop_index_if_exists('idx_order_deleted', 'orders')
    drop_index_if_exists('idx_cashtransaction_order', 'cash_transactions')
    drop_index_if_exists('idx_cashtransaction_session', 'cash_transactions')
    drop_index_if_exists('idx_cashsession_user', 'cash_register_sessions')
    drop_index_if_exists('idx_orderitem_menuitem', 'order_items')
    drop_index_if_exists('idx_orderitem_order', 'order_items')
    drop_index_if_exists('idx_table_restaurant', 'tables')
    drop_index_if_exists('idx_user_restaurant', 'users')
    drop_index_if_exists('idx_menuitem_restaurant_available', 'menu_items')
    drop_index_if_exists('idx_menuitem_restaurant_category', 'menu_items')
    drop_index_if_exists('idx_order_table_id', 'orders')
    drop_index_if_exists('idx_order_restaurant_created', 'orders')
    drop_index_if_exists('idx_order_restaurant_status', 'orders')
