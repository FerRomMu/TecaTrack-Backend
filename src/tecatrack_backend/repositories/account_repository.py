import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tecatrack_backend.models import Account
from tecatrack_backend.schemas import AccountCreate


class AccountRepository:
    def __init__(self, session: AsyncSession):
        """
        Initialize the repository with an asynchronous SQLAlchemy session for
        database operations.

        Parameters:
            session (AsyncSession): Async SQLAlchemy session used by the repository
                for executing queries and persisting entities.
        """
        self.session = session

    async def get_by_id(self, account_id: uuid.UUID) -> Account | None:
        """
        Retrieve a account by its UUID identifier.

        Parameters:
            account_id (uuid.UUID): The UUID of the account to retrieve.

        Returns:
            account | None: The matching account if found, `None` otherwise.
        """
        result = await self.session.execute(
            select(Account).where(Account.id == account_id)
        )
        return result.scalar_one_or_none()

    async def get_by_cbu(self, cbu: str) -> Account | None:
        """
        Retrieve a account by exact CBU address.

        Returns:
            `account` if a matching account exists, `None` otherwise.
        """
        result = await self.session.execute(select(Account).where(Account.cbu == cbu))
        return result.scalar_one_or_none()

    async def get_all_by_user_id(self, user_id: uuid.UUID) -> list[Account]:
        """
        Retrieve all accounts from an specific user.

        Returns:
            list[Account]: List of all user's accounts.
        """
        result = await self.session.execute(
            select(Account).where(Account.user_id == user_id)
        )
        return result.scalars().all()

    async def create(self, account_create: AccountCreate) -> Account:
        """
        Create and persist a new account from the given creation schema.

        Parameters:
            account_create (accountCreate): Schema containing fields for the new 
            account.

        Returns:
            account: The persisted account instance with database-generated fields 
            populated.
        """
        db_account = Account(**account_create.model_dump())
        self.session.add(db_account)
        await self.session.flush()
        await self.session.refresh(db_account)
        return db_account