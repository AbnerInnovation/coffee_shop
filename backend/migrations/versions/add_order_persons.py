"""add order persons for multiple diners

Revision ID: add_order_persons
Revises: update_payment_method_lowercase
Create Date: 2025-11-07 14:37:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_order_persons'
down_revision = 'update_payment_method_lowercase'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create order_persons table
    op.create_table(
        'order_persons',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=True),
        sa.Column('position', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_order_persons_id', 'order_persons', ['id'])
    op.create_index('ix_order_persons_order_id', 'order_persons', ['order_id'])

    # Add person_id column to order_items table
    op.add_column('order_items', sa.Column('person_id', sa.Integer(), nullable=True))
    op.create_index('ix_order_items_person_id', 'order_items', ['person_id'])
    op.create_foreign_key(
        'fk_order_items_person_id',
        'order_items',
        'order_persons',
        ['person_id'],
        ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    # Remove foreign key and column from order_items
    op.drop_constraint('fk_order_items_person_id', 'order_items', type_='foreignkey')
    op.drop_index('ix_order_items_person_id', 'order_items')
    op.drop_column('order_items', 'person_id')

    # Drop order_persons table
    op.drop_index('ix_order_persons_order_id', 'order_persons')
    op.drop_index('ix_order_persons_id', 'order_persons')
    op.drop_table('order_persons')
