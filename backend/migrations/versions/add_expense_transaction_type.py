"""add expense transaction type

Revision ID: add_expense_type
Revises: a1b2c3d4e5f6
Create Date: 2024-10-13 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_expense_type'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    # For MySQL: Modify the ENUM column to include 'expense'
    op.execute("""
        ALTER TABLE cash_transactions 
        MODIFY COLUMN transaction_type 
        ENUM('sale', 'refund', 'cancellation', 'tip', 'manual_add', 'manual_withdraw', 'expense') 
        NOT NULL
    """)


def downgrade():
    # Remove 'expense' from the enum
    op.execute("""
        ALTER TABLE cash_transactions 
        MODIFY COLUMN transaction_type 
        ENUM('sale', 'refund', 'cancellation', 'tip', 'manual_add', 'manual_withdraw') 
        NOT NULL
    """)
