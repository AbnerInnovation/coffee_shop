"""add payment method to transactions

Revision ID: add_payment_method_tx
Revises: add_expense_type
Create Date: 2025-10-13 00:09:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'add_payment_method_tx'
down_revision = 'add_expense_type'
branch_labels = None
depends_on = None


def upgrade():
    # For MySQL: Add payment_method column as ENUM
    op.execute("""
        ALTER TABLE cash_transactions 
        ADD COLUMN payment_method ENUM('CASH', 'CARD', 'DIGITAL', 'OTHER') NULL
    """)
    
    # Add category column for better expense tracking
    op.add_column('cash_transactions', 
        sa.Column('category', sa.String(100), nullable=True)
    )


def downgrade():
    op.drop_column('cash_transactions', 'category')
    op.drop_column('cash_transactions', 'payment_method')
