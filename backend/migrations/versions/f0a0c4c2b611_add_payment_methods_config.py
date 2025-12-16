"""add_payment_methods_config

Revision ID: f0a0c4c2b611
Revises: add_business_type
Create Date: 2025-12-15 23:34:31.991284

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f0a0c4c2b611'
down_revision: Union[str, None] = 'add_business_type'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add payment_methods_config JSON column to restaurants table
    # MySQL doesn't support default values for JSON columns, so we use a two-step approach:
    # 1. Add column as nullable
    # 2. Update existing rows with default value
    # 3. Make column NOT NULL
    
    # Step 1: Add nullable column
    op.add_column('restaurants', 
        sa.Column('payment_methods_config', 
                  sa.JSON(), 
                  nullable=True
        )
    )
    
    # Step 2: Update existing rows with default value
    op.execute("""
        UPDATE restaurants 
        SET payment_methods_config = '{"cash": true, "card": false, "digital": true, "other": false}'
        WHERE payment_methods_config IS NULL
    """)
    
    # Step 3: Make column NOT NULL
    op.alter_column('restaurants', 'payment_methods_config',
                    existing_type=sa.JSON(),
                    nullable=False)


def downgrade() -> None:
    # Remove payment_methods_config column
    op.drop_column('restaurants', 'payment_methods_config')
