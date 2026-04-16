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
    Create the test database schema before the test session and drop it afterward.

    Before tests, drops all existing tables and recreates them from Base.metadata;
    after the session, drops all tables and disposes the test engine. The
    underlying database (e.g., the PostgreSQL database named by
    TEST_DATABASE_URL) must already exist.
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
    Provide an isolated transactional AsyncSession for a single test.

    Yields:
        AsyncSession: A session bound to a connection started within a transaction;
        any database changes made through this session are rolled back after the
        test completes, ensuring test isolation without recreating the schema.
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
    Create an httpx AsyncClient for the FastAPI app with the app's `get_db`
    dependency overridden to yield the provided transactional `db_session`.

    The returned client uses ASGITransport to call the FastAPI application
    directly. Overriding `get_db` ensures request handlers use the same
    transactional session as the test so that database changes made during
    requests are visible to the test and rolled back with the test's
    transaction.

    Parameters:
        db_session (AsyncSession): Transactional session to be yielded to request
            handlers.

    Returns:
        AsyncClient: An httpx AsyncClient configured to send requests to the
            FastAPI app.
    """

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        """
        Provide the test's transactional AsyncSession to FastAPI dependencies.

        This async generator yields the AsyncSession bound to the current test
        transaction so request handlers use the same session as the test.

        Returns:
            AsyncSession: The session bound to the active test transaction.
        """
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
