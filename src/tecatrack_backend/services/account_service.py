from decimal import Decimal
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
        Get the account with the given UUID.
        
        Parameters:
            account_id (uuid.UUID): UUID of the account to retrieve.
        
        Returns:
            Account: The account matching the provided UUID.
        
        Raises:
            EntityNotFoundError: If no account exists with the given `account_id`.
        """
        account = await self.repository.get_by_id(account_id)
        if not account:
            raise EntityNotFoundError("Account", str(account_id))
        return account

    async def get_account_by_cbu(self, cbu: str) -> Account:
        """
        Retrieve an Account by its CBU.
        
        Parameters:
            cbu (str): CBU identifier to search for.
        
        Returns:
            Account: The matching account.
        
        Raises:
            EntityNotFoundError: If no account exists with the given CBU.
        """
        account = await self.repository.get_by_cbu(cbu)
        if not account:
            raise EntityNotFoundError("Account", cbu)
        return account

    async def get_all_accounts_by_user_id(
        self, user_id: uuid.UUID
    ) -> tuple[list[Account], Decimal]:
        """
        Fetches all accounts belonging to the specified user and computes their combined balance.
        
        Parameters:
            user_id (uuid.UUID): The UUID of the user whose accounts are requested.
        
        Returns:
            (list[Account], Decimal): A tuple where the first element is the list of the user's accounts and the second element is the sum of those accounts' balances.
        """
        accounts: list[Account] = await self.repository.get_all_by_user_id(user_id)
        total_balance = sum(account.balance for account in accounts)
        return accounts, total_balance

    async def create_account(self, account_create: AccountCreate) -> Account:
        """
        Create a new Account from the provided creation data.
        
        Parameters:
            account_create (AccountCreate): Creation payload containing at least `cbu`, `name`, and `user_id`.
        
        Returns:
            Account: The created account.
        
        Raises:
            EntityAlreadyExistsError: If an account with the same CBU already exists.
        """
        try:
            return await self.repository.create(account_create)
        except IntegrityError as e:
            raise EntityAlreadyExistsError("Account", str(account_create.cbu)) from e

