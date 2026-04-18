from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from tecatrack_backend.core.config import settings

# Create the async engine
# echo=True can be useful for debugging SQL queries during development
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
)

# Create a session factory
# expire_on_commit=False is important for async to prevent unintentional lazy-loading
async_session_factory = async_sessionmaker(
    engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide an asynchronous SQLAlchemy session scoped to a single request.

    Yields an AsyncSession started inside a transactional scope; the session and
    transaction are finalized when the generator exits.

    Returns:
        session (AsyncSession): Active transactional session for use by callers.
    """
    async with async_session_factory() as session:
        async with session.begin():
            yield session
