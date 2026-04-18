import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from tecatrack_backend.core.database import get_db
from tecatrack_backend.repositories.account_repository import AccountRepository
from tecatrack_backend.schemas.account_schemas import AccountCreate, AccountRead, AccountsResponse
from tecatrack_backend.services.account_service import AccountService

router = APIRouter(prefix="/accounts", tags=["Accounts"])


async def get_account_service(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> AccountService:
    """
    Constructs a AccountService backed by a AccountRepository using the provided
    database session.

    Returns:
        AccountService: A service instance configured with a AccountRepository that uses
            the given AsyncSession.
    """
    repository = AccountRepository(session)
    return AccountService(repository)


@router.post("/", response_model=AccountRead, status_code=status.HTTP_201_CREATED)
async def create_account(
    account_create: AccountCreate,
    service: Annotated[AccountService, Depends(get_account_service)],
) -> AccountRead:
    """
    Create a new account from the provided payload.

    Parameters:
        account_create (AccountCreate): Data required to create the account.

    Returns:
        AccountRead: The created account representation.
    """
    return await service.create_account(account_create)


@router.get("/{account_id}", response_model=AccountRead)
async def get_account(
    account_id: uuid.UUID,
    service: Annotated[AccountService, Depends(get_account_service)],
) -> AccountRead:
    """
    Retrieve a account by UUID.

    Returns:
        AccountRead: The account's data as a `AccountRead` model.
    """
    return await service.get_account(account_id)


@router.get("/cbu/{cbu}", response_model=AccountRead)
async def get_account_by_cbu(
    cbu: str,
    service: Annotated[AccountService, Depends(get_account_service)],
) -> AccountRead:
    """
    Retrieve a account by their CBU.

    Parameters:
        cbu (str): CBU of the account to retrieve.

    Returns:
        AccountRead: The account matching the given CBU.
    """
    return await service.get_account_by_cbu(cbu)

@router.get("/user/{user_id}", response_model=AccountsResponse)
async def get_account_by_user_id(
    user_id: uuid.UUID,
    service: Annotated[AccountService, Depends(get_account_service)],
) -> AccountRead:
    """
    Retrieve a account by their user ID.

    Parameters:
        user_id (uuid.UUID): User ID of the account to retrieve.

    Returns:
        AccountRead: The account matching the given user ID.
    """
    return await service.get_all_accounts_by_owner_id(user_id)
