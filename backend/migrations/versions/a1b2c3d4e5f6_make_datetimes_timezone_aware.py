"""
Make datetime columns timezone-aware (UTC) across key tables.

Revision ID: a1b2c3d4e5f6
Revises: 9ec8b365ef74
Create Date: 2025-10-13
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine import Connection

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '9ec8b365ef74'
branch_labels = None
depends_on = None


TABLES_WITH_SOFT_DELETE = [
    'users',
    'restaurants',
    'categories',
    'menu_items',
    'menu_item_variants',
    'orders',
    'order_items',
    'tables',
    'cash_register_sessions',
    'cash_transactions',
    'cash_register_reports',
]

# Columns common via BaseModel
BASEMODEL_DT_COLS = ['created_at', 'updated_at', 'deleted_at']

# Cash register specific non-basemodel cols
CASH_REGISTER_DT_COLS = {
    'cash_register_sessions': ['opened_at', 'closed_at'],
    'cash_register_reports': ['generated_at'],
}


def _is_postgres(conn: Connection) -> bool:
    return conn.dialect.name == 'postgresql'


def upgrade():
    conn = op.get_bind()

    if not _is_postgres(conn):
        # SQLite/MySQL: skip type alteration (SQLite lacks native timezone types).
        return

    # For Postgres: convert to timestamptz assuming existing naive values are UTC
    for table in TABLES_WITH_SOFT_DELETE:
        for col in BASEMODEL_DT_COLS:
            # Only attempt if column exists
            try:
                op.execute(
                    sa.text(
                        f"""
                        DO $$
                        BEGIN
                            IF EXISTS (
                                SELECT 1 FROM information_schema.columns
                                WHERE table_name = :table AND column_name = :col
                            ) THEN
                                ALTER TABLE {table}
                                ALTER COLUMN {col} TYPE TIMESTAMPTZ USING (
                                    CASE WHEN {col} IS NULL THEN NULL ELSE {col} AT TIME ZONE 'UTC' END
                                );
                            END IF;
                        END$$;
                        """
                    ).bindparams(table=table, col=col)
                )
            except Exception:
                # Be resilient if table/column does not exist in current head
                pass

        # Cash register specific columns
        if table in CASH_REGISTER_DT_COLS:
            for col in CASH_REGISTER_DT_COLS[table]:
                try:
                    op.execute(
                        sa.text(
                            f"""
                            DO $$
                            BEGIN
                                IF EXISTS (
                                    SELECT 1 FROM information_schema.columns
                                    WHERE table_name = :table AND column_name = :col
                                ) THEN
                                    ALTER TABLE {table}
                                    ALTER COLUMN {col} TYPE TIMESTAMPTZ USING (
                                        CASE WHEN {col} IS NULL THEN NULL ELSE {col} AT TIME ZONE 'UTC' END
                                    );
                                END IF;
                            END$$;
                            """
                        ).bindparams(table=table, col=col)
                    )
                except Exception:
                    pass


def downgrade():
    conn = op.get_bind()

    if not _is_postgres(conn):
        return

    # Convert timestamptz back to timestamp without time zone (loses tz info)
    for table in TABLES_WITH_SOFT_DELETE:
        for col in BASEMODEL_DT_COLS:
            try:
                op.execute(
                    sa.text(
                        f"""
                        DO $$
                        BEGIN
                            IF EXISTS (
                                SELECT 1 FROM information_schema.columns
                                WHERE table_name = :table AND column_name = :col
                            ) THEN
                                ALTER TABLE {table}
                                ALTER COLUMN {col} TYPE TIMESTAMP USING (
                                    CASE WHEN {col} IS NULL THEN NULL ELSE ({col} AT TIME ZONE 'UTC') END
                                );
                            END IF;
                        END$$;
                        """
                    ).bindparams(table=table, col=col)
                )
            except Exception:
                pass

        if table in CASH_REGISTER_DT_COLS:
            for col in CASH_REGISTER_DT_COLS[table]:
                try:
                    op.execute(
                        sa.text(
                            f"""
                            DO $$
                            BEGIN
                                IF EXISTS (
                                    SELECT 1 FROM information_schema.columns
                                    WHERE table_name = :table AND column_name = :col
                                ) THEN
                                    ALTER TABLE {table}
                                    ALTER COLUMN {col} TYPE TIMESTAMP USING (
                                        CASE WHEN {col} IS NULL THEN NULL ELSE ({col} AT TIME ZONE 'UTC') END
                                    );
                                END IF;
                            END IF;
                        END$$;
                            """
                        ).bindparams(table=table, col=col)
                    )
                except Exception:
                    pass
