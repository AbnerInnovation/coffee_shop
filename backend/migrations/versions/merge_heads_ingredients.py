"""merge heads for ingredients migration

Revision ID: merge_heads_ingredients
Revises: add_ingredients_notes, add_discount_price_menu
Create Date: 2024-10-17 11:50:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'merge_heads_ingredients'
down_revision = ('add_ingredients_notes', 'add_discount_price_menu')
branch_labels = None
depends_on = None


def upgrade():
    """Merge multiple heads - no changes needed."""
    pass


def downgrade():
    """Downgrade merge - no changes needed."""
    pass
