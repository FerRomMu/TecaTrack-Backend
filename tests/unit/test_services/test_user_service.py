import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from tecatrack_backend.core.exceptions import UserAlreadyExistsError, UserNotFoundError
from tecatrack_backend.models import User
from tecatrack_backend.schemas.user_schemas import UserCreate
from tecatrack_backend.services.user_service import UserService


@pytest.fixture
def mock_repo():
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
def user_service(mock_repo):
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
async def test_create_user_already_exists(user_service, mock_repo):
    user_create = UserCreate(email="test@example.com", full_name="Test User")
    mock_repo.get_by_email.return_value = User(
        id=uuid.uuid4(), email="test@example.com"
    )

    with pytest.raises(UserAlreadyExistsError):
        await user_service.create_user(user_create)

    mock_repo.create.assert_not_called()


@pytest.mark.asyncio
async def test_get_user_not_found(user_service, mock_repo):
    user_id = uuid.uuid4()
    mock_repo.get_by_id.return_value = None

    with pytest.raises(UserNotFoundError):
        await user_service.get_user(user_id)
