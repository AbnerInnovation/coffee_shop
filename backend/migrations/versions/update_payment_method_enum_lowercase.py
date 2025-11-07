"""update payment method enum to lowercase

Revision ID: update_payment_method_lowercase
Revises: add_payment_system
Create Date: 2025-11-06 17:10:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'update_payment_method_lowercase'
down_revision = 'add_payment_system'
branch_labels = None
depends_on = None


def upgrade():
    # Convertir payment_method de ENUM a VARCHAR para evitar conflictos
    op.execute("ALTER TABLE subscription_payments MODIFY COLUMN payment_method VARCHAR(20) NOT NULL")
    op.execute("UPDATE subscription_payments SET payment_method = LOWER(payment_method) WHERE payment_method IS NOT NULL")
    
    # Convertir status de ENUM a VARCHAR para evitar conflictos
    op.execute("ALTER TABLE subscription_payments MODIFY COLUMN status VARCHAR(20) NOT NULL DEFAULT 'pending'")
    op.execute("UPDATE subscription_payments SET status = LOWER(status) WHERE status IS NOT NULL")


def downgrade():
    # Revertir a VARCHAR
    op.execute("ALTER TABLE subscription_payments MODIFY COLUMN payment_method VARCHAR(20) NOT NULL")
    
    # Actualizar valores a mayúsculas
    op.execute("UPDATE subscription_payments SET payment_method = UPPER(payment_method)")
    
    # Cambiar de vuelta a ENUM con valores en mayúsculas
    op.execute("""
        ALTER TABLE subscription_payments 
        MODIFY COLUMN payment_method 
        ENUM('TRANSFER', 'CASH', 'CARD', 'STRIPE', 'PAYPAL', 'OTHER') 
        NOT NULL
    """)
