"""merge heads: c5f8ae061bff + add_multi_restaurant

Revision ID: 9ec8b365ef74
Revises: c5f8ae061bff, add_multi_restaurant
Create Date: 2025-10-11 13:23:27.508944

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9ec8b365ef74'
down_revision: Union[str, None] = ('c5f8ae061bff', 'add_multi_restaurant')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
