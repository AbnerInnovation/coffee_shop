"""add subscription system

Revision ID: add_subscription_system
Revises: merge_heads_2024
Create Date: 2024-10-17 21:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'add_subscription_system'
down_revision = 'merge_heads_ingredients'
branch_labels = None
depends_on = None


def upgrade():
    # Create subscription_plans table
    op.create_table(
        'subscription_plans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('tier', sa.Enum('trial', 'starter', 'basic', 'pro', 'business', 'enterprise', name='plan_tier'), nullable=False),
        sa.Column('display_name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('monthly_price', sa.Float(), nullable=False),
        sa.Column('annual_price', sa.Float(), nullable=True),
        sa.Column('max_admin_users', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('max_waiter_users', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('max_cashier_users', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_kitchen_users', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_owner_users', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_tables', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('max_menu_items', sa.Integer(), nullable=False, server_default='50'),
        sa.Column('max_categories', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('has_kitchen_module', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('has_ingredients_module', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('has_inventory_module', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('has_advanced_reports', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('has_multi_branch', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('has_priority_support', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('report_retention_days', sa.Integer(), nullable=False, server_default='7'),
        sa.Column('support_hours_monthly', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('is_trial', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('trial_duration_days', sa.Integer(), nullable=False, server_default='14'),
        sa.Column('is_popular', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('features', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_subscription_plans_tier'), 'subscription_plans', ['tier'], unique=False)
    
    # Create subscription_addons table
    op.create_table(
        'subscription_addons',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('display_name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('addon_type', sa.Enum('module', 'resource', 'service', name='addon_type'), nullable=False),
        sa.Column('category', sa.Enum('inventory', 'reports', 'kitchen', 'users', 'tables', 'products', 'training', 'setup', 'design', name='addon_category'), nullable=False),
        sa.Column('monthly_price', sa.Float(), nullable=False),
        sa.Column('is_recurring', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('is_quantifiable', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('min_quantity', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('max_quantity', sa.Integer(), nullable=True),
        sa.Column('provides_users', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('provides_tables', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('provides_menu_items', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('enables_inventory', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('enables_advanced_reports', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('enables_kitchen', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('available_for_plans', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('is_featured', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('addon_metadata', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_subscription_addons_code'), 'subscription_addons', ['code'], unique=False)
    op.create_index(op.f('ix_subscription_addons_category'), 'subscription_addons', ['category'], unique=False)
    
    # Create restaurant_subscriptions table
    op.create_table(
        'restaurant_subscriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('restaurant_id', sa.Integer(), nullable=False),
        sa.Column('plan_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('trial', 'active', 'past_due', 'cancelled', 'expired', name='subscription_status'), nullable=False, server_default='trial'),
        sa.Column('billing_cycle', sa.Enum('monthly', 'annual', name='billing_cycle'), nullable=False, server_default='monthly'),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('trial_end_date', sa.DateTime(), nullable=True),
        sa.Column('current_period_start', sa.DateTime(), nullable=False),
        sa.Column('current_period_end', sa.DateTime(), nullable=False),
        sa.Column('cancelled_at', sa.DateTime(), nullable=True),
        sa.Column('base_price', sa.Float(), nullable=False),
        sa.Column('total_price', sa.Float(), nullable=False),
        sa.Column('discount_percentage', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('discount_amount', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('discount_code', sa.String(length=50), nullable=True),
        sa.Column('auto_renew', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('subscription_metadata', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['plan_id'], ['subscription_plans.id'], ),
        sa.ForeignKeyConstraint(['restaurant_id'], ['restaurants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_restaurant_subscriptions_restaurant_id'), 'restaurant_subscriptions', ['restaurant_id'], unique=False)
    op.create_index(op.f('ix_restaurant_subscriptions_plan_id'), 'restaurant_subscriptions', ['plan_id'], unique=False)
    op.create_index(op.f('ix_restaurant_subscriptions_status'), 'restaurant_subscriptions', ['status'], unique=False)
    
    # Create restaurant_addons table
    op.create_table(
        'restaurant_addons',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('subscription_id', sa.Integer(), nullable=False),
        sa.Column('addon_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('unit_price', sa.Float(), nullable=False),
        sa.Column('total_price', sa.Float(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('addon_metadata', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['addon_id'], ['subscription_addons.id'], ),
        sa.ForeignKeyConstraint(['subscription_id'], ['restaurant_subscriptions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_restaurant_addons_subscription_id'), 'restaurant_addons', ['subscription_id'], unique=False)
    op.create_index(op.f('ix_restaurant_addons_addon_id'), 'restaurant_addons', ['addon_id'], unique=False)


def downgrade():
    # Drop tables in reverse order
    op.drop_index(op.f('ix_restaurant_addons_addon_id'), table_name='restaurant_addons')
    op.drop_index(op.f('ix_restaurant_addons_subscription_id'), table_name='restaurant_addons')
    op.drop_table('restaurant_addons')
    
    op.drop_index(op.f('ix_restaurant_subscriptions_status'), table_name='restaurant_subscriptions')
    op.drop_index(op.f('ix_restaurant_subscriptions_plan_id'), table_name='restaurant_subscriptions')
    op.drop_index(op.f('ix_restaurant_subscriptions_restaurant_id'), table_name='restaurant_subscriptions')
    op.drop_table('restaurant_subscriptions')
    
    op.drop_index(op.f('ix_subscription_addons_category'), table_name='subscription_addons')
    op.drop_index(op.f('ix_subscription_addons_code'), table_name='subscription_addons')
    op.drop_table('subscription_addons')
    
    op.drop_index(op.f('ix_subscription_plans_tier'), table_name='subscription_plans')
    op.drop_table('subscription_plans')
    
    # Drop enums (MySQL doesn't use separate enum types, but keeping for compatibility)
    # If using PostgreSQL, uncomment these:
    # op.execute('DROP TYPE IF EXISTS plan_tier')
    # op.execute('DROP TYPE IF EXISTS addon_type')
    # op.execute('DROP TYPE IF EXISTS addon_category')
    # op.execute('DROP TYPE IF EXISTS subscription_status')
    # op.execute('DROP TYPE IF EXISTS billing_cycle')
