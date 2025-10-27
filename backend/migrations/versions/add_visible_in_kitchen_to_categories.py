"""add visible_in_kitchen to categories

Revision ID: add_visible_kitchen_001
Revises: merge_all_heads_2025
Create Date: 2025-10-26 17:55:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_visible_kitchen_001'
down_revision = 'merge_all_heads_2025'
branch_labels = None
depends_on = None


def upgrade():
    # Add visible_in_kitchen column with default True
    op.add_column('categories', 
                  sa.Column('visible_in_kitchen', sa.Boolean(), nullable=False, server_default='1'))


def downgrade():
    # Drop visible_in_kitchen column
    op.drop_column('categories', 'visible_in_kitchen')
