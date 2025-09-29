"""add_cash_register

Revision ID: 01e6bf410b36
Revises: add_is_paid_to_orders
Create Date: 2025-09-26 11:47:19.036044

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '01e6bf410b36'
down_revision: Union[str, None] = 'add_is_paid_to_orders'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create cash_register_sessions table
    op.create_table('cash_register_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('opened_at', sa.DateTime(), nullable=False),
        sa.Column('closed_at', sa.DateTime(), nullable=True),
        sa.Column('opened_by_user_id', sa.Integer(), nullable=False),
        sa.Column('cashier_id', sa.Integer(), nullable=True),
        sa.Column('initial_balance', sa.DECIMAL(10, 2), nullable=False, server_default='0.00'),
        sa.Column('final_balance', sa.DECIMAL(10, 2), nullable=True),
        sa.Column('expected_balance', sa.DECIMAL(10, 2), nullable=False, server_default='0.00'),
        sa.Column('actual_balance', sa.DECIMAL(10, 2), nullable=True),
        sa.Column('status', sa.Enum('OPEN', 'CLOSED', name='session_status'), nullable=False, server_default='OPEN'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['opened_by_user_id'], ['users.id'], name='fk_sessions_opened_by_user_id'),
        sa.ForeignKeyConstraint(['cashier_id'], ['users.id'], name='fk_sessions_cashier_id'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create cash_transactions table
    op.create_table('cash_transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('transaction_type', sa.Enum('sale', 'refund', 'cancellation', 'tip', 'manual_add', 'manual_withdraw', name='transaction_type'), nullable=False),
        sa.Column('amount', sa.DECIMAL(10, 2), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('order_id', sa.Integer(), nullable=True),
        sa.Column('created_by_user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['cash_register_sessions.id'], name='fk_transactions_session_id'),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], name='fk_transactions_order_id'),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], name='fk_transactions_created_by_user_id'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create cash_register_reports table
    op.create_table('cash_register_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('report_type', sa.Enum('daily_summary', 'cash_difference', 'payment_breakdown', name='report_type'), nullable=False),
        sa.Column('data', sa.Text(), nullable=False),
        sa.Column('generated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['cash_register_sessions.id'], name='fk_reports_session_id'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    # Drop tables in reverse order to handle foreign keys
    op.drop_table('cash_register_reports')
    op.drop_table('cash_transactions')
    op.drop_table('cash_register_sessions')

    # Drop enums (if they exist)
    op.execute("DROP TYPE IF EXISTS session_status")
    op.execute("DROP TYPE IF EXISTS transaction_type")
    op.execute("DROP TYPE IF EXISTS report_type")
