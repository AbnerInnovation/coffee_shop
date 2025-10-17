"""add ingredients and special notes

Revision ID: add_ingredients_notes
Revises: merge_heads_2024
Create Date: 2024-10-17 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_ingredients_notes'
down_revision = 'merge_heads_2024'
branch_labels = None
depends_on = None


def upgrade():
    # Add ingredients JSON column to menu_items table
    # This stores ingredient options and removable ingredients for special notes
    # Check if column exists first (in case of partial migration)
    from sqlalchemy import inspect
    conn = op.get_bind()
    inspector = inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('menu_items')]
    
    if 'ingredients' not in columns:
        op.add_column('menu_items', sa.Column('ingredients', sa.JSON(), nullable=True))
    
    # Note: MySQL doesn't support functional indexes on JSON columns in all versions
    # The JSON column will still work efficiently for queries without an index
    # If needed, specific JSON path indexes can be added later based on query patterns
    
    # Create special_note_stats table for tracking most used special notes
    # Check if table exists first (in case of partial migration)
    tables = inspector.get_table_names()
    
    if 'special_note_stats' not in tables:
        op.create_table(
            'special_note_stats',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('restaurant_id', sa.Integer(), nullable=False),
            sa.Column('note_text', sa.String(length=200), nullable=False),
            sa.Column('usage_count', sa.Integer(), nullable=False, server_default='1'),
            sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
            sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(['restaurant_id'], ['restaurants.id'], ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('restaurant_id', 'note_text', name='uq_restaurant_note')
        )
        
        # Create indexes for efficient queries
        op.create_index('ix_special_note_stats_restaurant_id', 'special_note_stats', ['restaurant_id'])
        # MySQL compatible composite index (DESC is handled by query, not index)
        op.create_index('idx_special_notes_restaurant_usage', 'special_note_stats', ['restaurant_id', 'usage_count'])


def downgrade():
    # Drop special_note_stats table and its indexes
    op.drop_index('idx_special_notes_restaurant_usage', table_name='special_note_stats')
    op.drop_index('ix_special_note_stats_restaurant_id', table_name='special_note_stats')
    op.drop_table('special_note_stats')
    
    # Remove ingredients column from menu_items (no index to drop)
    op.drop_column('menu_items', 'ingredients')
