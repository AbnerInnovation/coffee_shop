"""add order item extras table

Revision ID: add_order_item_extras
Revises: add_visible_kitchen_001
Create Date: 2025-01-26 21:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_order_item_extras'
down_revision = 'add_visible_kitchen_001'
branch_labels = None
depends_on = None


def upgrade():
    # Create order_item_extras table
    op.create_table(
        'order_item_extras',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_item_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['order_item_id'], ['order_items.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create index on order_item_id for faster lookups
    op.create_index('ix_order_item_extras_order_item_id', 'order_item_extras', ['order_item_id'])


def downgrade():
    # Drop index first
    op.drop_index('ix_order_item_extras_order_item_id', table_name='order_item_extras')
    
    # Drop table
    op.drop_table('order_item_extras')
