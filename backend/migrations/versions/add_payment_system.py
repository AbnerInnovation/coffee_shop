"""add payment system for subscriptions

Revision ID: add_payment_system
Revises: add_order_item_extras
Create Date: 2025-01-27 01:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'add_payment_system'
down_revision = 'add_order_item_extras'
branch_labels = None
depends_on = None


def upgrade():
    # Create subscription_payments table
    op.create_table(
        'subscription_payments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('restaurant_id', sa.Integer(), nullable=False),
        sa.Column('subscription_id', sa.Integer(), nullable=False),
        sa.Column('plan_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('billing_cycle', sa.String(length=20), nullable=False),
        sa.Column('payment_method', sa.Enum('transfer', 'cash', 'card', 'stripe', 'paypal', 'other', name='payment_method'), nullable=False),
        sa.Column('reference_number', sa.String(length=100), nullable=True),
        sa.Column('payment_date', sa.DateTime(), nullable=True),
        sa.Column('proof_image_url', sa.String(length=500), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('stripe_payment_id', sa.String(length=100), nullable=True),
        sa.Column('stripe_customer_id', sa.String(length=100), nullable=True),
        sa.Column('card_last4', sa.String(length=4), nullable=True),
        sa.Column('card_brand', sa.String(length=20), nullable=True),
        sa.Column('auto_approved', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('status', sa.Enum('pending', 'approved', 'rejected', 'failed', name='payment_status'), nullable=False, server_default='pending'),
        sa.Column('reviewed_by', sa.Integer(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('next_retry_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['restaurant_id'], ['restaurants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['subscription_id'], ['restaurant_subscriptions.id'], ),
        sa.ForeignKeyConstraint(['plan_id'], ['subscription_plans.id'], ),
        sa.ForeignKeyConstraint(['reviewed_by'], ['users.id'], ),
    )
    op.create_index('ix_subscription_payments_restaurant_id', 'subscription_payments', ['restaurant_id'])
    op.create_index('ix_subscription_payments_reference_number', 'subscription_payments', ['reference_number'], unique=True)
    op.create_index('ix_subscription_payments_status', 'subscription_payments', ['status'])
    op.create_index('ix_subscription_payments_stripe_payment_id', 'subscription_payments', ['stripe_payment_id'])
    
    # Create subscription_alerts table
    op.create_table(
        'subscription_alerts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('restaurant_id', sa.Integer(), nullable=False),
        sa.Column('subscription_id', sa.Integer(), nullable=False),
        sa.Column('alert_type', sa.Enum('expiring_soon', 'grace_period', 'suspended', 'payment_approved', 'payment_rejected', name='alert_type'), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('read_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['restaurant_id'], ['restaurants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['subscription_id'], ['restaurant_subscriptions.id'], ),
    )
    op.create_index('ix_subscription_alerts_restaurant_id', 'subscription_alerts', ['restaurant_id'])
    op.create_index('ix_subscription_alerts_alert_type', 'subscription_alerts', ['alert_type'])
    op.create_index('ix_subscription_alerts_is_read', 'subscription_alerts', ['is_read'])
    
    # Add new columns to restaurant_subscriptions table
    op.add_column('restaurant_subscriptions', sa.Column('grace_period_end', sa.DateTime(), nullable=True))
    op.add_column('restaurant_subscriptions', sa.Column('pending_payment_id', sa.Integer(), nullable=True))
    op.add_column('restaurant_subscriptions', sa.Column('payment_method_id', sa.String(length=100), nullable=True))
    
    # Update subscription_status enum to include new statuses
    # Note: This requires recreating the enum in MySQL/PostgreSQL
    # For SQLite, this is a no-op as it doesn't have native enums
    with op.batch_alter_table('restaurant_subscriptions') as batch_op:
        batch_op.alter_column('status',
                              existing_type=sa.Enum('trial', 'active', 'past_due', 'cancelled', 'expired', name='subscription_status'),
                              type_=sa.Enum('trial', 'active', 'past_due', 'pending_payment', 'cancelled', 'expired', name='subscription_status'),
                              existing_nullable=False)


def downgrade():
    # Remove new columns from restaurant_subscriptions
    op.drop_column('restaurant_subscriptions', 'payment_method_id')
    op.drop_column('restaurant_subscriptions', 'pending_payment_id')
    op.drop_column('restaurant_subscriptions', 'grace_period_end')
    
    # Drop subscription_alerts table
    op.drop_index('ix_subscription_alerts_is_read', 'subscription_alerts')
    op.drop_index('ix_subscription_alerts_alert_type', 'subscription_alerts')
    op.drop_index('ix_subscription_alerts_restaurant_id', 'subscription_alerts')
    op.drop_table('subscription_alerts')
    
    # Drop subscription_payments table
    op.drop_index('ix_subscription_payments_stripe_payment_id', 'subscription_payments')
    op.drop_index('ix_subscription_payments_status', 'subscription_payments')
    op.drop_index('ix_subscription_payments_reference_number', 'subscription_payments')
    op.drop_index('ix_subscription_payments_restaurant_id', 'subscription_payments')
    op.drop_table('subscription_payments')
    
    # Revert subscription_status enum
    with op.batch_alter_table('restaurant_subscriptions') as batch_op:
        batch_op.alter_column('status',
                              existing_type=sa.Enum('trial', 'active', 'past_due', 'pending_payment', 'cancelled', 'expired', name='subscription_status'),
                              type_=sa.Enum('trial', 'active', 'past_due', 'cancelled', 'expired', name='subscription_status'),
                              existing_nullable=False)
