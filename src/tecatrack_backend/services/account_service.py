import uuid
from decimal import Decimal

from sqlalchemy.exc import IntegrityError

from tecatrack_backend.core.exceptions import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
    InvalidEntityError,
)
from tecatrack_backend.models import Account
from tecatrack_backend.repositories import AccountRepository, UserRepository
from tecatrack_backend.schemas.account_schemas import AccountCreate


class AccountService:
    def __init__(
        self, repository: AccountRepository, user_repository: UserRepository
    ) -> None:
        """
        Initialize the AccountService with a AccountRepository.

        The provided repository is used to perform persistence operations for
        account-related actions.
        """
        self.user_repository = user_repository
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
        Fetches all accounts belonging to the specified user and computes their combined
        balance.

        Parameters:
            user_id (uuid.UUID): The UUID of the user whose accounts are requested.

        Returns:
            tuple[list[Account], Decimal]: A tuple where the first element is the list
            of the user's accounts and the second element is the sum of those
            accounts' balances.
        """
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise EntityNotFoundError("User", str(user_id))
        accounts: list[Account] = await self.repository.get_all_by_user_id(user_id)
        total_balance = sum((account.balance for account in accounts), Decimal("0"))
        return accounts, total_balance

    async def create_account(self, account_create: AccountCreate) -> Account:
        """
        Create a new Account from the provided creation data.

        Parameters:
            account_create (AccountCreate): Creation payload containing at least `cbu`,
            `bank`, and `user_id`.

        Returns:
            Account: The created account.

        Raises:
            EntityAlreadyExistsError: If an account with the same CBU already exists.
        """
        try:
            return await self.repository.create(account_create)
        except IntegrityError as e:
            # Get the underlying asyncpg error code
            # sqlalchemy wraps the original error in .orig
            pg_code = getattr(e.orig, "sqlstate", None)

            # 23505 = Unique Violation
            if pg_code == "23505":
                if "cbu" in str(e.orig).lower():
                    raise EntityAlreadyExistsError(
                        "Account", str(account_create.cbu)
                    ) from e

            # 23503 = Foreign Key Violation
            elif pg_code == "23503":
                raise EntityNotFoundError("User", str(account_create.user_id)) from e

            # 23514 = Check Violation
            elif pg_code == "23514":
                if "cbu" in str(e.orig).lower():
                    raise InvalidEntityError("Account", "cbu") from e

            raise e

    async def get_account_by_bank(self, cuil: str, bank: str) -> Account:
        """
        Retrieve an Account by the user's CUIL and the bank name.

        Parameters:
            cuil (str): CUIL identifier of the user.
            bank (str): Bank name to search for.

        Returns:
            Account: The matching account.

        Raises:
            EntityNotFoundError: If no account exists with the given CUIL and bank.
        """
        user = await self.user_repository.get_by_cuil(cuil)
        if not user:
            raise EntityNotFoundError("User", str(cuil))
        account = await self.repository.get_by_bank(user.id, bank)
        if not account:
            raise EntityNotFoundError("Account", bank)
        return account

    async def update_balance(self, account: Account, amount: Decimal) -> None:
        """
        Update the balance of an account.

        Parameters:
            account (Account): The account to update.
            amount (Decimal): The amount to add to the account balance.

        Raises:
            EntityNotFoundError: If the account does not exist.
        """
        if not account:
            raise EntityNotFoundError("Account", str(account.id))
        account.balance += amount
        await self.repository.update(account)

    
