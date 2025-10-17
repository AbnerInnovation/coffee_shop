"""add sysadmin role

Revision ID: add_sysadmin_role
Revises: add_expense_type
Create Date: 2024-10-17 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_sysadmin_role'
down_revision = 'add_expense_type'
branch_labels = None
depends_on = None


def upgrade():
    # For MySQL: Modify the ENUM column to include 'sysadmin'
    op.execute("""
        ALTER TABLE users 
        MODIFY COLUMN role 
        ENUM('sysadmin', 'admin', 'staff', 'customer') 
        NOT NULL 
        DEFAULT 'staff'
    """)


def downgrade():
    # Remove 'sysadmin' from the enum
    # Note: This will fail if any users have the sysadmin role
    op.execute("""
        ALTER TABLE users 
        MODIFY COLUMN role 
        ENUM('admin', 'staff', 'customer') 
        NOT NULL 
        DEFAULT 'staff'
    """)
