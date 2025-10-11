"""add multi-restaurant support

Revision ID: add_multi_restaurant
Revises: 01e6bf410b36
Create Date: 2025-01-10 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'add_multi_restaurant'
down_revision = '01e6bf410b36'
branch_labels = None
depends_on = None


def upgrade():
    # Create restaurants table (skip if already exists)
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table('restaurants'):
        op.create_table(
            'restaurants',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.Column('subdomain', sa.String(length=50), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('address', sa.String(length=255), nullable=True),
            sa.Column('phone', sa.String(length=20), nullable=True),
            sa.Column('email', sa.String(length=100), nullable=True),
            sa.Column('logo_url', sa.String(length=500), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
            sa.Column('timezone', sa.String(length=50), nullable=False, server_default='America/Los_Angeles'),
            sa.Column('currency', sa.String(length=3), nullable=False, server_default='USD'),
            sa.Column('tax_rate', sa.Float(), nullable=True, server_default='0.0'),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.Column('deleted_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('subdomain')
        )
        op.create_index(op.f('ix_restaurants_subdomain'), 'restaurants', ['subdomain'], unique=True)
    
    # Ensure a default restaurant exists for existing data (idempotent)
    op.execute("""
        INSERT INTO restaurants (name, subdomain, description, is_active, timezone, currency, tax_rate, created_at, updated_at)
        VALUES ('Default Restaurant', 'default', 'Default restaurant for existing data', 1, 'America/Los_Angeles', 'USD', 0.0, NOW(), NOW())
        ON DUPLICATE KEY UPDATE subdomain = VALUES(subdomain)
    """)
    
    # Add restaurant_id to users table (idempotent)
    user_cols = [c['name'] for c in inspector.get_columns('users')]
    if 'restaurant_id' not in user_cols:
        op.add_column('users', sa.Column('restaurant_id', sa.Integer(), nullable=True))
    # Create index if missing
    user_indexes = {idx['name'] for idx in inspector.get_indexes('users')}
    users_rest_idx = op.f('ix_users_restaurant_id')
    if users_rest_idx not in user_indexes:
        op.create_index(users_rest_idx, 'users', ['restaurant_id'], unique=False)
    # Create FK if missing
    user_fks = {fk['name'] for fk in inspector.get_foreign_keys('users') if fk.get('name')}
    if 'fk_users_restaurant_id' not in user_fks:
        op.create_foreign_key('fk_users_restaurant_id', 'users', 'restaurants', ['restaurant_id'], ['id'])
    
    # Set default restaurant for existing users (safe even if column already existed)
    op.execute("UPDATE users SET restaurant_id = (SELECT id FROM restaurants WHERE subdomain = 'default' LIMIT 1)")
    
    # Add restaurant_id to categories table (idempotent)
    cat_cols = [c['name'] for c in inspector.get_columns('categories')]
    if 'restaurant_id' not in cat_cols:
        op.add_column('categories', sa.Column('restaurant_id', sa.Integer(), nullable=True))
    cat_indexes = {idx['name'] for idx in inspector.get_indexes('categories')}
    cat_rest_idx = op.f('ix_categories_restaurant_id')
    if cat_rest_idx not in cat_indexes:
        op.create_index(cat_rest_idx, 'categories', ['restaurant_id'], unique=False)
    cat_fks = {fk['name'] for fk in inspector.get_foreign_keys('categories') if fk.get('name')}
    if 'fk_categories_restaurant_id' not in cat_fks:
        op.create_foreign_key('fk_categories_restaurant_id', 'categories', 'restaurants', ['restaurant_id'], ['id'])
    
    # Set default restaurant for existing categories
    op.execute("UPDATE categories SET restaurant_id = (SELECT id FROM restaurants WHERE subdomain = 'default' LIMIT 1)")
    
    # Make restaurant_id NOT NULL for categories if currently nullable
    cat_cols_detail = {c['name']: c for c in inspector.get_columns('categories')}
    if 'restaurant_id' in cat_cols_detail and cat_cols_detail['restaurant_id'].get('nullable', True):
        op.alter_column('categories', 'restaurant_id', nullable=False, existing_type=sa.Integer())
    
    # Remove unique constraint on category name (now unique per restaurant)
    op.drop_index(op.f('ix_categories_name'), table_name='categories')
    
    # Add restaurant_id to menu_items table (idempotent)
    mi_cols = [c['name'] for c in inspector.get_columns('menu_items')]
    if 'restaurant_id' not in mi_cols:
        op.add_column('menu_items', sa.Column('restaurant_id', sa.Integer(), nullable=True))
    mi_indexes = {idx['name'] for idx in inspector.get_indexes('menu_items')}
    mi_rest_idx = op.f('ix_menu_items_restaurant_id')
    if mi_rest_idx not in mi_indexes:
        op.create_index(mi_rest_idx, 'menu_items', ['restaurant_id'], unique=False)
    mi_fks = {fk['name'] for fk in inspector.get_foreign_keys('menu_items') if fk.get('name')}
    if 'fk_menu_items_restaurant_id' not in mi_fks:
        op.create_foreign_key('fk_menu_items_restaurant_id', 'menu_items', 'restaurants', ['restaurant_id'], ['id'])
    
    # Set default restaurant for existing menu items
    op.execute("UPDATE menu_items SET restaurant_id = (SELECT id FROM restaurants WHERE subdomain = 'default' LIMIT 1)")
    
    # Make restaurant_id NOT NULL for menu_items if currently nullable
    mi_cols_detail = {c['name']: c for c in inspector.get_columns('menu_items')}
    if 'restaurant_id' in mi_cols_detail and mi_cols_detail['restaurant_id'].get('nullable', True):
        op.alter_column('menu_items', 'restaurant_id', nullable=False, existing_type=sa.Integer())
    
    # Add restaurant_id to tables table (idempotent)
    tbl_cols = [c['name'] for c in inspector.get_columns('tables')]
    if 'restaurant_id' not in tbl_cols:
        op.add_column('tables', sa.Column('restaurant_id', sa.Integer(), nullable=True))
    tbl_indexes = {idx['name'] for idx in inspector.get_indexes('tables')}
    tbl_rest_idx = op.f('ix_tables_restaurant_id')
    if tbl_rest_idx not in tbl_indexes:
        op.create_index(tbl_rest_idx, 'tables', ['restaurant_id'], unique=False)
    tbl_fks = {fk['name'] for fk in inspector.get_foreign_keys('tables') if fk.get('name')}
    if 'fk_tables_restaurant_id' not in tbl_fks:
        op.create_foreign_key('fk_tables_restaurant_id', 'tables', 'restaurants', ['restaurant_id'], ['id'])
    
    # Set default restaurant for existing tables
    op.execute("UPDATE tables SET restaurant_id = (SELECT id FROM restaurants WHERE subdomain = 'default' LIMIT 1)")
    
    # Make restaurant_id NOT NULL for tables if currently nullable
    tbl_cols_detail = {c['name']: c for c in inspector.get_columns('tables')}
    if 'restaurant_id' in tbl_cols_detail and tbl_cols_detail['restaurant_id'].get('nullable', True):
        op.alter_column('tables', 'restaurant_id', nullable=False, existing_type=sa.Integer())
    
    # Remove unique constraint on table number (now unique per restaurant).
    # Find any unique index on ['number'] and drop it by discovered name.
    existing_tbl_indexes = inspector.get_indexes('tables')
    for idx in existing_tbl_indexes:
        if idx.get('unique') and idx.get('column_names') == ['number']:
            op.drop_index(idx['name'], table_name='tables')
            break
    
    # Add restaurant_id to orders table (idempotent)
    ord_cols = [c['name'] for c in inspector.get_columns('orders')]
    if 'restaurant_id' not in ord_cols:
        op.add_column('orders', sa.Column('restaurant_id', sa.Integer(), nullable=True))
    ord_indexes = {idx['name'] for idx in inspector.get_indexes('orders')}
    ord_rest_idx = op.f('ix_orders_restaurant_id')
    if ord_rest_idx not in ord_indexes:
        op.create_index(ord_rest_idx, 'orders', ['restaurant_id'], unique=False)
    ord_fks = {fk['name'] for fk in inspector.get_foreign_keys('orders') if fk.get('name')}
    if 'fk_orders_restaurant_id' not in ord_fks:
        op.create_foreign_key('fk_orders_restaurant_id', 'orders', 'restaurants', ['restaurant_id'], ['id'])
    
    # Set default restaurant for existing orders
    op.execute("UPDATE orders SET restaurant_id = (SELECT id FROM restaurants WHERE subdomain = 'default' LIMIT 1)")
    
    # Make restaurant_id NOT NULL for orders if currently nullable
    ord_cols_detail = {c['name']: c for c in inspector.get_columns('orders')}
    if 'restaurant_id' in ord_cols_detail and ord_cols_detail['restaurant_id'].get('nullable', True):
        op.alter_column('orders', 'restaurant_id', nullable=False, existing_type=sa.Integer())


def downgrade():
    # Remove restaurant_id from orders
    op.drop_constraint('fk_orders_restaurant_id', 'orders', type_='foreignkey')
    op.drop_index(op.f('ix_orders_restaurant_id'), table_name='orders')
    op.drop_column('orders', 'restaurant_id')
    
    # Restore unique constraint on table number
    op.create_index('number', 'tables', ['number'], unique=True)
    
    # Remove restaurant_id from tables
    op.drop_constraint('fk_tables_restaurant_id', 'tables', type_='foreignkey')
    op.drop_index(op.f('ix_tables_restaurant_id'), table_name='tables')
    op.drop_column('tables', 'restaurant_id')
    
    # Remove restaurant_id from menu_items
    op.drop_constraint('fk_menu_items_restaurant_id', 'menu_items', type_='foreignkey')
    op.drop_index(op.f('ix_menu_items_restaurant_id'), table_name='menu_items')
    op.drop_column('menu_items', 'restaurant_id')
    
    # Restore unique constraint on category name
    op.create_index('name', 'categories', ['name'], unique=True)
    
    # Remove restaurant_id from categories
    op.drop_constraint('fk_categories_restaurant_id', 'categories', type_='foreignkey')
    op.drop_index(op.f('ix_categories_restaurant_id'), table_name='categories')
    op.drop_column('categories', 'restaurant_id')
    
    # Remove restaurant_id from users
    op.drop_constraint('fk_users_restaurant_id', 'users', type_='foreignkey')
    op.drop_index(op.f('ix_users_restaurant_id'), table_name='users')
    op.drop_column('users', 'restaurant_id')
    
    # Drop restaurants table
    op.drop_index(op.f('ix_restaurants_subdomain'), table_name='restaurants')
    op.drop_table('restaurants')
