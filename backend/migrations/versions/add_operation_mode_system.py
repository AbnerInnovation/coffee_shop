"""add operation mode system

Revision ID: add_operation_mode_system
Revises: add_customer_print_settings
Create Date: 2024-12-12

This migration adds:
1. operation_mode enum and column to subscription_plans
2. order_type enum (replacing string) to orders
3. ticket_number column to orders for POS mode
4. pos_basic tier to plan_tier enum
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision = 'add_operation_mode_system'
down_revision = 'add_customer_print_settings'
branch_labels = None
depends_on = None


def upgrade():
    # MySQL: Add operation_mode column to subscription_plans using VARCHAR with ENUM constraint
    op.add_column('subscription_plans',
        sa.Column('operation_mode', 
            mysql.ENUM('full_restaurant', 'pos_only', 'cafe_mode', 'food_truck', 'quick_service'),
            nullable=False, 
            server_default='full_restaurant'
        )
    )
    
    # MySQL: Add ticket_number column to orders
    op.add_column('orders',
        sa.Column('ticket_number', sa.String(20), nullable=True)
    )
    
    # Create index on ticket_number for fast lookups
    op.create_index('idx_orders_ticket_number', 'orders', ['ticket_number', 'restaurant_id'])
    
    # MySQL: Modify order_type column from VARCHAR to ENUM with new values
    # Step 1: Update existing values to ensure compatibility
    op.execute("""
        UPDATE orders
        SET order_type = CASE
            WHEN order_type NOT IN ('dine_in', 'takeaway', 'delivery') THEN 'dine_in'
            ELSE order_type
        END
    """)
    
    # Step 2: Change column to ENUM with all values (MySQL allows direct conversion)
    op.execute("""
        ALTER TABLE orders 
        MODIFY COLUMN order_type ENUM('dine_in', 'takeaway', 'delivery', 'pos_sale', 'quick_service') 
        NOT NULL DEFAULT 'dine_in'
    """)
    
    # MySQL: Modify plan_tier enum to add 'pos_basic'
    # This requires recreating the column in MySQL
    op.execute("""
        ALTER TABLE subscription_plans 
        MODIFY COLUMN tier ENUM(
            'trial', 'starter', 'basic', 'pro', 'business', 'enterprise', 'pos_basic'
        ) NOT NULL
    """)
    
    # Create index on operation_mode for faster queries
    op.create_index('idx_subscription_plans_operation_mode', 'subscription_plans', ['operation_mode'])


def downgrade():
    # Drop indexes
    op.drop_index('idx_subscription_plans_operation_mode', 'subscription_plans')
    op.drop_index('idx_orders_ticket_number', 'orders')
    
    # MySQL: Revert order_type to VARCHAR
    op.execute("""
        ALTER TABLE orders 
        MODIFY COLUMN order_type VARCHAR(50) 
        NOT NULL DEFAULT 'dine_in'
    """)
    
    # Drop ticket_number column
    op.drop_column('orders', 'ticket_number')
    
    # Drop operation_mode column
    op.drop_column('subscription_plans', 'operation_mode')
    
    # MySQL: Revert plan_tier enum (remove 'pos_basic')
    # Note: This requires recreating the column
    op.execute("""
        ALTER TABLE subscription_plans 
        MODIFY COLUMN tier ENUM(
            'trial', 'starter', 'basic', 'pro', 'business', 'enterprise'
        ) NOT NULL
    """)
