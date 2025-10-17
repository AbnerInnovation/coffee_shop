"""merge sysadmin and performance indexes

Revision ID: merge_heads_2024
Revises: add_sysadmin_role, f1a2b3c4d5e6
Create Date: 2024-10-17 00:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'merge_heads_2024'
down_revision = ('add_sysadmin_role', 'f1a2b3c4d5e6')
branch_labels = None
depends_on = None


def upgrade():
    # This is a merge migration, no changes needed
    pass


def downgrade():
    # This is a merge migration, no changes needed
    pass
