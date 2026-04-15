import uuid
from unittest.mock import MagicMock, AsyncMock

import pytest

from tecatrack_backend.exceptions import UserAlreadyExistsError, UserNotFoundError
from tecatrack_backend.models import User
from tecatrack_backend.schemas.user import UserCreate
from tecatrack_backend.services.user_service import UserService


@pytest.fixture
def mock_repo():
    repo = MagicMock()
    repo.get_by_email = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.create = AsyncMock()
    return repo


@pytest.fixture
def user_service(mock_repo):
    return UserService(mock_repo)


@pytest.mark.asyncio
async def test_create_user_already_exists(user_service, mock_repo):
    user_create = UserCreate(email="test@example.com", full_name="Test User")
    mock_repo.get_by_email.return_value = User(id=uuid.uuid4(), email="test@example.com")

    with pytest.raises(UserAlreadyExistsError):
        await user_service.create_user(user_create)

    mock_repo.create.assert_not_called()


@pytest.mark.asyncio
async def test_get_user_not_found(user_service, mock_repo):
    user_id = uuid.uuid4()
    mock_repo.get_by_id.return_value = None

    with pytest.raises(UserNotFoundError):
        await user_service.get_user(user_id)