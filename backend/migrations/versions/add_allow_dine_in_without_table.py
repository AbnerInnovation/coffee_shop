"""add_allow_dine_in_without_table

Revision ID: add_allow_dine_in_without_table
Revises: 9a6f610ba1a3
Create Date: 2025-11-28 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_allow_dine_in_without_table'
down_revision: Union[str, None] = '9a6f610ba1a3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add allow_dine_in_without_table setting to restaurants table
    op.add_column('restaurants', sa.Column('allow_dine_in_without_table', sa.Boolean(), nullable=False, server_default=sa.text('0')))


def downgrade() -> None:
    # Remove allow_dine_in_without_table column
    op.drop_column('restaurants', 'allow_dine_in_without_table')
