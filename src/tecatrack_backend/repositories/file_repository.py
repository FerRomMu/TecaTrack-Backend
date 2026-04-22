from sqlalchemy.ext.asyncio import AsyncSession

from tecatrack_backend.models import File
from tecatrack_backend.schemas.file_schemas import FileCreate


class FileRepository:
    def __init__(self, session: AsyncSession):
        """
        Initialize the repository with an asynchronous SQLAlchemy session for
        database operations.

        Parameters:
            session (AsyncSession): Async SQLAlchemy session used by the repository
                for executing queries and persisting entities.
        """
        self.session = session

    async def create(self, file_create: FileCreate) -> File:
        """
        Create and persist a new File from the given creation schema.

        Parameters:
            file_create (FileCreate): Schema containing fields for the new file.

        Returns:
            File: The persisted File instance with database-generated fields populated.
        """
        db_file = File(**file_create.model_dump())
        self.session.add(db_file)
        await self.session.flush()
        await self.session.refresh(db_file)
        return db_file
