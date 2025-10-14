"""add discount price to menu items and variants

Revision ID: add_discount_price_menu
Revises: add_payment_method_tx
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_discount_price_menu'
down_revision = 'add_payment_method_tx'
branch_labels = None
depends_on = None


def upgrade():
    # Add discount_price column to menu_items table
    op.add_column('menu_items', sa.Column('discount_price', sa.Float(), nullable=True))
    
    # Add discount_price column to menu_item_variants table
    op.add_column('menu_item_variants', sa.Column('discount_price', sa.Float(), nullable=True))


def downgrade():
    # Remove discount_price column from menu_item_variants table
    op.drop_column('menu_item_variants', 'discount_price')
    
    # Remove discount_price column from menu_items table
    op.drop_column('menu_items', 'discount_price')
