"""merge order_number and sort field branches

Revision ID: merge_order_sort_2025
Revises: add_order_number_001, c306addf573e
Create Date: 2025-10-25 23:17:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'merge_order_sort_2025'
down_revision = ('add_order_number_001', 'c306addf573e')
branch_labels = None
depends_on = None


def upgrade() -> None:
    # This is a merge migration, no changes needed
    pass


def downgrade() -> None:
    # This is a merge migration, no changes needed
    pass
