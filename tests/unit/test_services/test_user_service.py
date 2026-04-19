import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from tecatrack_backend.core.exceptions import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
)
from tecatrack_backend.schemas.user_schemas import UserCreate
from tecatrack_backend.services.user_service import UserService


@pytest.fixture
def mock_repo() -> MagicMock:
    """
    Create a mocked repository configured with asynchronous user-related methods.

    The returned MagicMock has coroutine-compatible attributes `get_by_email`,
    `get_by_id`, and `create` (each an AsyncMock) suitable for injecting into
    services in async tests.

    Returns:
        MagicMock: A repository mock with `get_by_email`, `get_by_id`, and `create`
            implemented as AsyncMock.
    """
    repo = MagicMock()
    repo.get_by_email = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.create = AsyncMock()
    return repo


@pytest.fixture
def user_service(mock_repo: MagicMock) -> UserService:
    """
    Create a UserService instance configured to use the provided mocked repository.

    Parameters:
        mock_repo (MagicMock): Mocked repository object expected to expose async methods
            `get_by_email`, `get_by_id`, and `create`.

    Returns:
        UserService: A UserService instance wired to the provided repository mock.
    """
    return UserService(mock_repo)


@pytest.mark.asyncio
async def test_create_user_already_exists(
    user_service: UserService, mock_repo: MagicMock
) -> None:
    user_create = UserCreate(email="test@example.com", full_name="Test User")
    mock_repo.create.side_effect = IntegrityError(None, None, None)

    with pytest.raises(EntityAlreadyExistsError):
        await user_service.create_user(user_create)


@pytest.mark.asyncio
async def test_get_user_not_found(
    user_service: UserService, mock_repo: MagicMock
) -> None:
    user_id = uuid.uuid4()
    mock_repo.get_by_id.return_value = None

    with pytest.raises(EntityNotFoundError):
        await user_service.get_user(user_id)
