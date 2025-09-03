"""merge heads

Revision ID: 460ffadd5e78
Revises: ad5680431456, add_deleted_at_column
Create Date: 2025-09-03 16:04:53.818567

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '460ffadd5e78'
down_revision: Union[str, None] = ('ad5680431456', 'add_deleted_at_column')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
