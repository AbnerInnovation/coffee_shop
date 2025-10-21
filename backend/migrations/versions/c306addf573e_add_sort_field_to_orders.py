"""add_sort_field_to_orders

Revision ID: c306addf573e
Revises: 257282c9b4a4
Create Date: 2025-10-21 09:02:22.506431

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c306addf573e'
down_revision: Union[str, None] = '257282c9b4a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
