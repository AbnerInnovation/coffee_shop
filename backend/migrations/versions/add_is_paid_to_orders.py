"""
add is_paid column to orders

Revision ID: add_is_paid_to_orders
Revises: feaf3a486270
Create Date: 2025-09-21
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_is_paid_to_orders'
down_revision = 'feaf3a486270'
branch_labels = None
depends_on = None

def upgrade() -> None:
    with op.batch_alter_table('orders') as batch_op:
        batch_op.add_column(sa.Column('is_paid', sa.Boolean(), nullable=False, server_default=sa.false()))
    # Remove server_default after setting existing rows
    with op.batch_alter_table('orders') as batch_op:
        batch_op.alter_column('is_paid', server_default=None)


def downgrade() -> None:
    with op.batch_alter_table('orders') as batch_op:
        batch_op.drop_column('is_paid')
