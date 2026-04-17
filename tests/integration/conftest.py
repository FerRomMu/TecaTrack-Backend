import os
from collections.abc import AsyncGenerator

import pytest_asyncio
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from alembic import command
from tecatrack_backend.core.database import get_db
from tecatrack_backend.main import app
from tecatrack_backend.models import Base

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", None)

if TEST_DATABASE_URL is None:
    raise ValueError("TEST_DATABASE_URL environment variable is not set")

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)
test_async_session_factory = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)


def _get_alembic_config() -> Config:
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", TEST_DATABASE_URL.replace("%", "%%"))
    return alembic_cfg


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db() -> None:
    """
    Bootstrap the test schema running real Alembic migrations and tear it down
    afterward.

    This ensures that broken migrations are caught before they ship: if
    `alembic upgrade head` fails, the fixture explodes and every test fails
    immediately. After the session, all tables are dropped and the engine is
    disposed.
    """

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.execute(text("DROP TABLE IF EXISTS alembic_version"))

    def run_migrations(connection) -> None:
        alembic_cfg = _get_alembic_config()
        alembic_cfg.attributes["connection"] = connection
        command.upgrade(alembic_cfg, "head")

    async with test_engine.begin() as conn:
        await conn.run_sync(run_migrations)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.execute(text("DROP TABLE IF EXISTS alembic_version"))

    await test_engine.dispose()


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide an isolated transactional AsyncSession for a single test.

    Yields:
        AsyncSession: A session bound to a connection started within a transaction;
        any database changes made through this session are rolled back after the
        test completes, ensuring test isolation without recreating the schema.
    """
    async with test_engine.connect() as conn:
        outer_tx = await conn.begin()
        async_session = AsyncSession(
            bind=conn,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )
        try:
            yield async_session
        finally:
            await async_session.close()
            await outer_tx.rollback()


@pytest_asyncio.fixture
async def async_client(db_session: AsyncSession) -> AsyncClient:
    """
    Create an httpx AsyncClient for the FastAPI app with the app's `get_db`
    dependency overridden to yield the provided transactional `db_session`.
    """

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    previous_override = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    if previous_override is None:
        app.dependency_overrides.pop(get_db, None)
    else:
        app.dependency_overrides[get_db] = previous_override
