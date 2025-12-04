"""add_customer_print_settings

Revision ID: add_customer_print_settings
Revises: add_allow_dine_in_without_table
Create Date: 2025-12-03 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_customer_print_settings'
down_revision: Union[str, None] = 'add_allow_dine_in_without_table'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add customer print settings to restaurants table
    op.add_column('restaurants', sa.Column('customer_print_enabled', sa.Boolean(), nullable=False, server_default=sa.text('1')))
    op.add_column('restaurants', sa.Column('customer_print_paper_width', sa.Integer(), nullable=False, server_default='80'))


def downgrade() -> None:
    # Remove customer print settings columns
    op.drop_column('restaurants', 'customer_print_paper_width')
    op.drop_column('restaurants', 'customer_print_enabled')
