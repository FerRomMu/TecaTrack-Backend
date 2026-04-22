import uuid
from decimal import Decimal
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
    repo.get_by_bank = AsyncMock()
    return repo


@pytest.fixture
def mock_user_repo() -> MagicMock:
    """
    Create a mocked repository configured with asynchronous user-related methods.

    Returns:
        MagicMock: A repository mock with `get_by_id` and `get_by_cuil`
            implemented as AsyncMock.
    """
    repo = MagicMock()
    repo.get_by_id = AsyncMock()
    repo.get_by_cuil = AsyncMock()
    return repo


@pytest.fixture
def account_service(mock_repo: MagicMock, mock_user_repo: MagicMock) -> AccountService:
    """
    Constructs an AccountService configured to use the provided mocked repositories.

    Parameters:
        mock_repo (MagicMock): Mock repository expected to provide coroutine-compatible
        async methods `get_by_cbu`, `get_by_id`, `create`, and `get_all_by_user_id`.
        mock_user_repo (MagicMock): Mock repository expected to provide
        coroutine-compatible async methods `get_by_id`.

    Returns:
        AccountService: An AccountService instance wired to the provided repository
        mock.
    """
    return AccountService(mock_repo, mock_user_repo)


@pytest.mark.asyncio
async def test_create_account_already_exists(
    account_service: AccountService, mock_repo: MagicMock
) -> None:
    # 1. Setup data
    account_create = AccountCreate(
        cbu="1234567890123456789012",
        user_id=uuid.uuid4(),
        bank="Test Bank",
        balance=0.0,
    )

    # 2. Create a mock for the 'orig' exception that SQLAlchemy wraps
    # We give it a .sqlstate so the Service logic can identify it
    mock_orig = MagicMock()
    mock_orig.sqlstate = "23505"
    mock_orig.__str__.return_value = (
        'duplicate key value violates unique constraint "uq_accounts_cbu"'
    )

    # 3. Inject the error into the mock repository
    mock_repo.create.side_effect = IntegrityError(
        statement="INSERT...", params={}, orig=mock_orig
    )

    # 4. Assert that the Service translates it to the Domain Exception
    with pytest.raises(EntityAlreadyExistsError) as exc_info:
        await account_service.create_account(account_create)

    assert "Account" in str(exc_info.value)
    assert "1234567890123456789012" in str(exc_info.value)


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

    mock_account_1 = MagicMock(balance=Decimal("100.50"))
    mock_account_2 = MagicMock(balance=Decimal("50.00"))
    mock_repo.get_all_by_user_id.return_value = [mock_account_1, mock_account_2]

    accounts, total_balance = await account_service.get_all_accounts_by_user_id(user_id)

    assert len(accounts) == 2
    assert total_balance == Decimal("150.50")
    mock_repo.get_all_by_user_id.assert_awaited_once_with(user_id)


@pytest.mark.asyncio
async def test_get_all_accounts_by_user_id_empty(
    account_service: AccountService, mock_repo: MagicMock
) -> None:
    user_id = uuid.uuid4()
    mock_repo.get_all_by_user_id.return_value = []

    accounts, total_balance = await account_service.get_all_accounts_by_user_id(user_id)

    assert len(accounts) == 0
    assert total_balance == Decimal("0")
    mock_repo.get_all_by_user_id.assert_awaited_once_with(user_id)


@pytest.mark.asyncio
async def test_get_account_by_bank_not_found(
    account_service: AccountService, mock_repo: MagicMock, mock_user_repo: MagicMock
) -> None:
    cuil = "12345678901"
    bank = "Test Bank"

    mock_user_repo.get_by_cuil.return_value = MagicMock(id=uuid.uuid4())
    mock_repo.get_by_bank.return_value = None

    with pytest.raises(EntityNotFoundError):
        await account_service.get_account_by_bank(cuil, bank)


@pytest.mark.asyncio
async def test_get_account_by_bank_success(
    account_service: AccountService, mock_repo: MagicMock, mock_user_repo: MagicMock
) -> None:
    cuil = "12345678901"
    bank = "Test Bank"
    user_id = uuid.uuid4()
    mock_user_repo.get_by_cuil.return_value = MagicMock(id=user_id)
    mock_account = MagicMock(balance=Decimal("100.50"))
    mock_repo.get_by_bank.return_value = mock_account

    account = await account_service.get_account_by_bank(cuil, bank)

    assert account == mock_account
    mock_user_repo.get_by_cuil.assert_awaited_once_with(cuil)
    mock_repo.get_by_bank.assert_awaited_once_with(user_id, bank)
