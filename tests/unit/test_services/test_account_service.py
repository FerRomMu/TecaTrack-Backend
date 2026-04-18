import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from tecatrack_backend.core.exceptions import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
)
from tecatrack_backend.schemas.account_schemas import AccountCreate
from tecatrack_backend.services.account_service import AccountService


@pytest.fixture
def mock_repo() -> MagicMock:
    """
    Create a mocked repository configured with asynchronous account-related methods.

    The returned MagicMock has coroutine-compatible attributes `get_by_cbu`,
    `get_by_id`, and `create` (each an AsyncMock) suitable for injecting into
    services in async tests.

    Returns:
        MagicMock: A repository mock with `get_by_cbu`, `get_by_id`, and `create`
            implemented as AsyncMock.
    """
    repo = MagicMock()
    repo.get_by_cbu = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.create = AsyncMock()
    repo.get_all_by_user_id = AsyncMock()
    return repo


@pytest.fixture
def account_service(mock_repo: MagicMock) -> AccountService:
    """
    Constructs an AccountService configured to use the provided mocked repository.

    Parameters:
        mock_repo (MagicMock): Mock repository expected to provide coroutine-compatible
        async methods `get_by_cbu`, `get_by_id`, `create`, and `get_all_by_user_id`.

    Returns:
        AccountService: An AccountService instance wired to the provided repository
        mock.
    """
    return AccountService(mock_repo)


@pytest.mark.asyncio
async def test_create_account_already_exists(
    account_service: AccountService, mock_repo: MagicMock
) -> None:
    account_create = AccountCreate(
        cbu="1234567890123456789012",
        user_id=uuid.uuid4(),
        bank="Test Bank",
        balance=0.0,
    )
    mock_repo.create.side_effect = IntegrityError(None, None, None)

    with pytest.raises(EntityAlreadyExistsError):
        await account_service.create_account(account_create)


@pytest.mark.asyncio
async def test_get_account_not_found(
    account_service: AccountService, mock_repo: MagicMock
) -> None:
    account_id = uuid.uuid4()
    mock_repo.get_by_id.return_value = None

    with pytest.raises(EntityNotFoundError):
        await account_service.get_account(account_id)


@pytest.mark.asyncio
async def test_get_account_by_cbu_not_found(
    account_service: AccountService, mock_repo: MagicMock
) -> None:
    cbu = "1234567890123456789012"
    mock_repo.get_by_cbu.return_value = None

    with pytest.raises(EntityNotFoundError):
        await account_service.get_account_by_cbu(cbu)


@pytest.mark.asyncio
async def test_get_all_accounts_by_user_id_success(
    account_service: AccountService, mock_repo: MagicMock
) -> None:
    user_id = uuid.uuid4()
    from decimal import Decimal

    mock_account_1 = MagicMock(balance=Decimal("100.50"))
    mock_account_2 = MagicMock(balance=Decimal("50.00"))
    mock_repo.get_all_by_user_id.return_value = [mock_account_1, mock_account_2]

    accounts, total_balance = await account_service.get_all_accounts_by_user_id(user_id)

    assert len(accounts) == 2
    assert total_balance == Decimal("150.50")
    mock_repo.get_all_by_user_id.assert_awaited_once_with(user_id)
