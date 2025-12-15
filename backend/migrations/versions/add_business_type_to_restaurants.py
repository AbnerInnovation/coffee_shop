"""add business_type to restaurants

Revision ID: add_business_type
Revises: add_operation_mode_system
Create Date: 2025-12-15 10:54:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_business_type'
down_revision = 'add_operation_mode_system'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add business_type column with default value
    op.add_column('restaurants', sa.Column('business_type', sa.String(length=50), nullable=False, server_default='restaurant'))


def downgrade() -> None:
    # Remove business_type column
    op.drop_column('restaurants', 'business_type')
