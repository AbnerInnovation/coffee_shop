"""add_advanced_printing_enabled_to_restaurants

Revision ID: c5cba3d8aaa0
Revises: c77adfa2719f
Create Date: 2025-12-19 23:45:58.563151

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c5cba3d8aaa0'
down_revision: Union[str, None] = 'c77adfa2719f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add advanced_printing_enabled column to restaurants table
    op.add_column('restaurants', sa.Column('advanced_printing_enabled', sa.Boolean(), nullable=False, server_default='0'))


def downgrade() -> None:
    # Remove advanced_printing_enabled column from restaurants table
    op.drop_column('restaurants', 'advanced_printing_enabled')
