"""add restaurant and session number to cash register

Revision ID: add_restaurant_session
Revises: merge_heads_2024
Create Date: 2025-01-26 17:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_restaurant_session'
down_revision = 'merge_heads_2024'
branch_labels = None
depends_on = None


def upgrade():
    from sqlalchemy import orm, inspect
    from sqlalchemy.ext.declarative import declarative_base
    
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [col['name'] for col in inspector.get_columns('cash_register_sessions')]
    
    # Add restaurant_id column if it doesn't exist
    if 'restaurant_id' not in columns:
        op.add_column('cash_register_sessions', 
                      sa.Column('restaurant_id', sa.Integer(), nullable=True))
    
    # Add session_number column if it doesn't exist
    if 'session_number' not in columns:
        op.add_column('cash_register_sessions', 
                      sa.Column('session_number', sa.Integer(), nullable=True))
    
    # Store foreign_keys list for later use
    foreign_keys = [fk['name'] for fk in inspector.get_foreign_keys('cash_register_sessions')]
    
    # Update restaurant_id from opened_by_user's restaurant_id
    op.execute("""
        UPDATE cash_register_sessions crs
        INNER JOIN users u ON crs.opened_by_user_id = u.id
        SET crs.restaurant_id = u.restaurant_id
        WHERE crs.restaurant_id IS NULL
    """)
    
    # Handle orphaned sessions (where user doesn't exist or user has no restaurant_id)
    # Delete sessions that can't be associated with a restaurant
    bind = op.get_bind()
    orphaned = bind.execute(sa.text("""
        SELECT COUNT(*) as count
        FROM cash_register_sessions 
        WHERE restaurant_id IS NULL
    """)).fetchone()
    
    if orphaned and orphaned[0] > 0:
        print(f"WARNING: Found {orphaned[0]} orphaned cash register sessions with no restaurant_id")
        print("These sessions will be deleted as they cannot be migrated.")
        op.execute("""
            DELETE FROM cash_register_sessions 
            WHERE restaurant_id IS NULL
        """)
    
    # Verify all restaurant_ids exist in restaurants table
    invalid = bind.execute(sa.text("""
        SELECT COUNT(*) as count
        FROM cash_register_sessions crs
        LEFT JOIN restaurants r ON crs.restaurant_id = r.id
        WHERE crs.restaurant_id IS NOT NULL AND r.id IS NULL
    """)).fetchone()
    
    if invalid and invalid[0] > 0:
        print(f"WARNING: Found {invalid[0]} sessions with invalid restaurant_id references")
        print("These sessions will be deleted as they reference non-existent restaurants.")
        op.execute("""
            DELETE FROM cash_register_sessions 
            WHERE restaurant_id NOT IN (SELECT id FROM restaurants)
        """)
    
    # Calculate session_number for existing sessions per restaurant using Python
    bind = op.get_bind()
    
    # Get all sessions ordered by restaurant and opened_at
    sessions = bind.execute(sa.text("""
        SELECT id, restaurant_id 
        FROM cash_register_sessions 
        ORDER BY restaurant_id, opened_at
    """)).fetchall()
    
    # Calculate session numbers per restaurant
    restaurant_counters = {}
    for session_id, restaurant_id in sessions:
        if restaurant_id not in restaurant_counters:
            restaurant_counters[restaurant_id] = 1
        else:
            restaurant_counters[restaurant_id] += 1
        
        # Update the session with its number
        bind.execute(sa.text("""
            UPDATE cash_register_sessions 
            SET session_number = :session_number 
            WHERE id = :session_id
        """), {"session_number": restaurant_counters[restaurant_id], "session_id": session_id})
    
    # For MySQL: Must drop foreign key before altering column, then recreate it
    # Drop the foreign key constraint temporarily
    if 'fk_cash_register_sessions_restaurant_id' in foreign_keys:
        op.drop_constraint('fk_cash_register_sessions_restaurant_id', 
                          'cash_register_sessions', 
                          type_='foreignkey')
    
    # Now make the columns NOT NULL (MySQL requires specifying the type)
    op.alter_column('cash_register_sessions', 'restaurant_id', 
                    existing_type=sa.Integer(), 
                    nullable=False)
    op.alter_column('cash_register_sessions', 'session_number', 
                    existing_type=sa.Integer(), 
                    nullable=False)
    
    # Recreate the foreign key constraint (only if it doesn't exist)
    # Re-check foreign keys after potential drop
    current_foreign_keys = [fk['name'] for fk in inspector.get_foreign_keys('cash_register_sessions')]
    if 'fk_cash_register_sessions_restaurant_id' not in current_foreign_keys:
        op.create_foreign_key(
            'fk_cash_register_sessions_restaurant_id',
            'cash_register_sessions', 
            'restaurants',
            ['restaurant_id'], 
            ['id']
        )
    
    # Create index for faster queries by restaurant if it doesn't exist
    indexes = [idx['name'] for idx in inspector.get_indexes('cash_register_sessions')]
    if 'idx_cash_register_sessions_restaurant_id' not in indexes:
        op.create_index('idx_cash_register_sessions_restaurant_id', 
                        'cash_register_sessions', 
                        ['restaurant_id'])
    
    # Create unique constraint to ensure session_number is unique per restaurant if it doesn't exist
    if 'idx_cash_register_sessions_restaurant_session' not in indexes:
        op.create_index('idx_cash_register_sessions_restaurant_session', 
                        'cash_register_sessions', 
                        ['restaurant_id', 'session_number'], 
                        unique=True)


def downgrade():
    # Drop indexes
    op.drop_index('idx_cash_register_sessions_restaurant_session', 
                  table_name='cash_register_sessions')
    op.drop_index('idx_cash_register_sessions_restaurant_id', 
                  table_name='cash_register_sessions')
    
    # Drop foreign key constraint
    op.drop_constraint('fk_cash_register_sessions_restaurant_id', 
                       'cash_register_sessions', 
                       type_='foreignkey')
    
    # Drop columns
    op.drop_column('cash_register_sessions', 'session_number')
    op.drop_column('cash_register_sessions', 'restaurant_id')
