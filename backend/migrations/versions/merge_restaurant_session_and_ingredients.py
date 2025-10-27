"""merge all heads: restaurant session, ingredients, and order sort

Revision ID: merge_all_heads_2025
Revises: add_restaurant_session, merge_order_sort_2025
Create Date: 2025-01-26 17:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'merge_all_heads_2025'
down_revision = ('add_restaurant_session', 'merge_order_sort_2025')
branch_labels = None
depends_on = None


def upgrade():
    # This is a merge migration, no changes needed
    pass


def downgrade():
    # This is a merge migration, no changes needed
    pass
