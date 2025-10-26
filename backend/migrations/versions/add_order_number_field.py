"""add order_number field

Revision ID: add_order_number_001
Revises: add_subscription_system
Create Date: 2025-10-25 23:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_order_number_001'
down_revision = 'add_subscription_system'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if column exists before adding
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('orders')]
    
    if 'order_number' not in columns:
        # Add order_number column (nullable first for existing data)
        op.add_column('orders', sa.Column('order_number', sa.Integer(), nullable=True))
        
        # Populate order_number for existing orders
        # For each restaurant, assign consecutive numbers based on creation date
        # Using a temporary table to avoid MySQL's "can't update table in FROM clause" error
        op.execute("""
            UPDATE orders o
            JOIN (
                SELECT o1.id, 
                       (SELECT COUNT(*) 
                        FROM orders o2 
                        WHERE o2.restaurant_id = o1.restaurant_id 
                        AND o2.created_at <= o1.created_at) as row_num
                FROM orders o1
            ) as temp ON o.id = temp.id
            SET o.order_number = temp.row_num
        """)
        
        # Make order_number NOT NULL after populating
        op.alter_column('orders', 'order_number', nullable=False)
    
    # Check if index exists before creating
    indexes = [idx['name'] for idx in inspector.get_indexes('orders')]
    if 'ix_orders_order_number' not in indexes:
        op.create_index('ix_orders_order_number', 'orders', ['order_number'])


def downgrade() -> None:
    op.drop_index('ix_orders_order_number', table_name='orders')
    op.drop_column('orders', 'order_number')
