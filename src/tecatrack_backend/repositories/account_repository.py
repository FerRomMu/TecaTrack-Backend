import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tecatrack_backend.models import Account
from tecatrack_backend.schemas import AccountCreate


class AccountRepository:
    def __init__(self, session: AsyncSession):
        """
        Store the provided AsyncSession for use by the repository's database operations.
        """
        self.session = session

    async def get_by_id(self, account_id: uuid.UUID) -> Account | None:
        """
        Retrieve an account by its UUID identifier.

        Returns:
            Account | None: The matching Account instance if found, `None` otherwise.
        """
        result = await self.session.execute(
            select(Account).where(Account.id == account_id)
        )
        return result.scalar_one_or_none()

    async def get_by_cbu(self, cbu: str) -> Account | None:
        """
        Retrieve an Account by its exact CBU.

        Parameters:
                cbu (str): CBU string to match.

        Returns:
                The matching Account if found, `None` otherwise.
        """
        result = await self.session.execute(select(Account).where(Account.cbu == cbu))
        return result.scalar_one_or_none()

    async def get_all_by_user_id(self, user_id: uuid.UUID) -> list[Account]:
        """
        Fetches all accounts belonging to the specified user.

        Parameters:
                user_id (uuid.UUID): UUID of the user whose accounts should be
                retrieved.

        Returns:
                list[Account]: List of Account instances belonging to the user; empty
                list if none found.
        """
        result = await self.session.execute(
            select(Account).where(Account.user_id == user_id)
        )
        return result.scalars().all()

    async def get_by_bank(self, user_id: uuid.UUID, bank: str) -> Account | None:
        """
        Retrieve an account by its bank from the specified user.

        Parameters:
                user_id (uuid.UUID): UUID of the user whose account should be
                retrieved.
                bank (str): Bank name to match.

        Returns:
                Account | None: The matching Account instance if found, `None` otherwise.
        """
        result = await self.session.execute(
            select(Account).where(Account.user_id == user_id, Account.bank == bank)
        )
        return result.scalar_one_or_none()

    async def create(self, account_create: AccountCreate) -> Account:
        """
        Create a new Account from the provided creation schema and persist it to the
        database.

        Parameters:
            account_create (AccountCreate): Schema containing values for the new
            account.

        Returns:
            Account: The persisted Account instance with database-generated fields (for
            example, id or timestamps) populated.
        """
        db_account = Account(**account_create.model_dump())
        self.session.add(db_account)
        await self.session.flush()
        await self.session.refresh(db_account)
        return db_account
