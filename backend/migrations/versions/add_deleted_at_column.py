"""add deleted_at column

Revision ID: add_deleted_at_column
Revises: 19e2a2a8c746
Create Date: 2025-09-03 22:55:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'add_deleted_at_column'
down_revision = '19e2a2a8c746'
branch_labels = None
depends_on = None

def upgrade():
    # Get all tables
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()
    
    # Skip these system tables
    skip_tables = ['alembic_version', 'spatial_ref_sys']
    
    # Add deleted_at column to each table if it doesn't exist
    for table_name in tables:
        if table_name in skip_tables:
            continue
            
        # Check if column already exists
        columns = [col['name'] for col in inspector.get_columns(table_name)]
        if 'deleted_at' not in columns:
            op.add_column(
                table_name,
                sa.Column('deleted_at', sa.DateTime(), nullable=True, index=True)
            )
            print(f"Added deleted_at column to {table_name}")

def downgrade():
    # Get all tables
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()
    
    # Skip these system tables
    skip_tables = ['alembic_version', 'spatial_ref_sys']
    
    # Remove deleted_at column from each table if it exists
    for table_name in tables:
        if table_name in skip_tables:
            continue
            
        # Check if column exists
        columns = [col['name'] for col in inspector.get_columns(table_name)]
        if 'deleted_at' in columns:
            op.drop_column(table_name, 'deleted_at')
            print(f"Dropped deleted_at column from {table_name}")
