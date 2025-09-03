"""update_order_status_enum

Revision ID: ad5680431456
Revises: f8aed4bfdec9
Create Date: 2025-09-03 12:10:56.915951

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ad5680431456'
down_revision: Union[str, None] = 'f8aed4bfdec9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # For MySQL, we need to modify the column definition directly
    # First update the orders table
    op.alter_column('orders', 'status',
                   existing_type=sa.Enum('PENDING', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', name='order_status'),
                   type_=sa.Enum('PENDING', 'PREPARING', 'READY', 'COMPLETED', 'CANCELLED', name='order_status'),
                   existing_nullable=False)
    
    # Then update the order_items table
    op.alter_column('order_items', 'status',
                   existing_type=sa.Enum('PENDING', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', name='order_item_status'),
                   type_=sa.Enum('PENDING', 'PREPARING', 'READY', 'COMPLETED', 'CANCELLED', name='order_status'),
                   existing_nullable=False)
    
    # No need to drop types in MySQL as they are managed per column


def downgrade() -> None:
    # Update back to the original enum values
    op.alter_column('orders', 'status',
                   existing_type=sa.Enum('PENDING', 'PREPARING', 'READY', 'COMPLETED', 'CANCELLED', name='order_status'),
                   type_=sa.Enum('PENDING', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', name='order_status'),
                   existing_nullable=False)
    
    op.alter_column('order_items', 'status',
                   existing_type=sa.Enum('PENDING', 'PREPARING', 'READY', 'COMPLETED', 'CANCELLED', name='order_status'),
                   type_=sa.Enum('PENDING', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', name='order_item_status'),
                   existing_nullable=False)
