import os
from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

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


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    """
    Sets up the test database schema before running the test session,
    and drops it afterwards to ensure a clean state.
    Note: The PostgreSQL database itself (e.g., tecatrack_test) MUST already exist.
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await test_engine.dispose()


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provides a transactional session that rolls back after each test,
    ensuring full isolation without recreating the schema.
    """
    async with test_engine.connect() as conn:
        await conn.begin()
        async_session = AsyncSession(bind=conn, expire_on_commit=False)

        try:
            yield async_session
        finally:
            await async_session.close()
            await conn.rollback()


@pytest_asyncio.fixture
async def async_client(db_session: AsyncSession):
    """
    Provides an async HTTP client for the FastAPI app,
    with the database dependency overridden to use the same transactional
    test session — ensuring that request-side writes are visible to the
    test and get rolled back alongside everything else.
    """

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
