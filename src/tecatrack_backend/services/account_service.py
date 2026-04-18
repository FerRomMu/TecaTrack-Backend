import uuid

from sqlalchemy.exc import IntegrityError

from tecatrack_backend.core.exceptions import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
)
from tecatrack_backend.models import Account
from tecatrack_backend.repositories.account_repository import AccountRepository
from tecatrack_backend.schemas.account_schemas import AccountCreate


class AccountService:
    def __init__(self, repository: AccountRepository):
        """
        Initialize the AccountService with a AccountRepository.

        The provided repository is used to perform persistence operations for
        account-related actions.
        """
        self.repository = repository

    async def get_account(self, account_id: uuid.UUID) -> Account:
        """
        Retrieve an account by their UUID.

        Parameters:
            account_id (uuid.UUID): The UUID of the account to retrieve.

        Returns:
            account: The account matching the provided UUID.

        Raises:
            accountNotFoundError: If no account exists with the given `account_id`.
        """
        account = await self.repository.get_by_id(account_id)
        if not account:
            raise EntityNotFoundError("Account", str(account_id))
        return account

    async def get_account_by_cbu(self, cbu: str) -> Account:
        """
        Retrieve an account by their CBU.

        Parameters:
            cbu (str): The CBU of the account to look up.

        Returns:
            account (account): The matching account object.

        Raises:
            accountNotFoundError: If no account exists with the given cbu.
        """
        account = await self.repository.get_by_cbu(cbu)
        if not account:
            raise EntityNotFoundError("Account", cbu)
        return account

    async def create_account(self, account_create: AccountCreate) -> Account:
        """
        Create a new account from the provided creation data.

        Parameters:
            account_create (AccountCreate): Data required to create the account,
                including cbu, name, and owner_id.

        Returns:
            account: The newly created account.

        Raises:
            EntityAlreadyExistsError: If an account with the same cbu already exists.
        """
        try:
            return await self.repository.create(account_create)
        except IntegrityError as e:
            raise EntityAlreadyExistsError("Account", str(account_create.cbu)) from e

