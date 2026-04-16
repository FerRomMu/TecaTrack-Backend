import asyncio
import os
from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
from tecatrack_backend.models import Base

# Load .env file
load_dotenv()

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Database URL from env
db_url = os.getenv("DATABASE_URL")
if not db_url:
    raise RuntimeError("DATABASE_URL is not set in .env")

# Replace % with %% for Alembic URL parsing
config.set_main_option("sqlalchemy.url", db_url.replace("%", "%%"))

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run Alembic migrations using a URL-only configuration (offline mode).

    Configures the Alembic context with the configured `sqlalchemy.url`,
    `target_metadata`, `literal_binds=True`, and
    `dialect_opts={'paramstyle': 'named'}`, then runs migrations inside a
    transaction.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """
    Configure the Alembic migration context with the provided database connection
    and run pending migrations inside a transaction.

    Parameters:
        connection: A SQLAlchemy connection or connection-like object to which the
            Alembic context will be bound for executing migrations.
    """
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """
    Run migrations in "online" mode using an async SQLAlchemy engine.

    Creates an async engine from the Alembic configuration, opens an asynchronous
    connection to run migrations within a transactional context, and disposes
    the engine when complete.
    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
