"""add_sort_field_to_orders

Revision ID: 257282c9b4a4
Revises: f14ffeff223d
Create Date: 2025-10-21 08:23:47.178679

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '257282c9b4a4'
down_revision: Union[str, None] = 'f14ffeff223d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add sort column to orders table with default value of 50
    op.add_column('orders', sa.Column('sort', sa.Integer(), nullable=False, server_default='50'))


def downgrade() -> None:
    # Remove sort column from orders table
    op.drop_column('orders', 'sort')
