"""add_printers_system

Revision ID: c77adfa2719f
Revises: f0a0c4c2b611
Create Date: 2025-12-18 22:44:10.285515

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision: str = 'c77adfa2719f'
down_revision: Union[str, None] = 'f0a0c4c2b611'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create printers table with MySQL ENUM
    op.create_table(
        'printers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('restaurant_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('printer_type', mysql.ENUM('kitchen', 'bar', 'cashier'), nullable=False),
        sa.Column('connection_type', sa.String(length=20), nullable=False, server_default='network'),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('port', sa.Integer(), nullable=True, server_default='9100'),
        sa.Column('device_path', sa.String(length=255), nullable=True),
        sa.Column('paper_width', sa.Integer(), nullable=False, server_default='80'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('auto_print', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('print_copies', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['restaurant_id'], ['restaurants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_printers_id'), 'printers', ['id'], unique=False)
    op.create_index(op.f('ix_printers_restaurant_id'), 'printers', ['restaurant_id'], unique=False)
    op.create_index(op.f('ix_printers_printer_type'), 'printers', ['printer_type'], unique=False)
    
    # Create category_printer association table
    op.create_table(
        'category_printer',
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('printer_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['printer_id'], ['printers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('category_id', 'printer_id')
    )


def downgrade() -> None:
    # Drop association table first
    op.drop_table('category_printer')
    
    # Drop indexes
    op.drop_index(op.f('ix_printers_printer_type'), table_name='printers')
    op.drop_index(op.f('ix_printers_restaurant_id'), table_name='printers')
    op.drop_index(op.f('ix_printers_id'), table_name='printers')
    
    # Drop printers table
    op.drop_table('printers')
    
    # Drop enum type (MySQL doesn't need this, but keeping for consistency)
    # op.execute("DROP TYPE IF EXISTS printertype")
