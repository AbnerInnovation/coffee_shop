"""add_staff_type_to_users

Revision ID: f14ffeff223d
Revises: add_subscription_system
Create Date: 2025-10-19 23:23:39.591406

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f14ffeff223d'
down_revision: Union[str, None] = 'add_subscription_system'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create staff_type enum
    staff_type_enum = sa.Enum('waiter', 'cashier', 'kitchen', 'general', name='staff_type')
    staff_type_enum.create(op.get_bind(), checkfirst=True)
    
    # Add staff_type column to users table
    op.add_column('users', sa.Column('staff_type', staff_type_enum, nullable=True))


def downgrade() -> None:
    # Drop staff_type column
    op.drop_column('users', 'staff_type')
    
    # Drop staff_type enum
    staff_type_enum = sa.Enum('waiter', 'cashier', 'kitchen', 'general', name='staff_type')
    staff_type_enum.drop(op.get_bind(), checkfirst=True)
