import os
import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config, pool
from alembic import context

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Import the SQLAlchemy Base and settings
from app.db.base import Base
from app.config import settings  # Your FastAPI settings

# Alembic Config object
config = context.config

# Override the sqlalchemy.url from alembic.ini with your FastAPI settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URI)

# Set up Python logging from the config file
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import all models so Alembic can detect schema changes
import app.models.menu
import app.models.order
import app.models.table
import app.models.user

# Metadata object for Alembic
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()

# Decide offline vs online mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
