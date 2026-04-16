import os
from dataclasses import dataclass

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass(frozen=True)
class Settings:
    """
    Application settings loaded from environment variables.
    """

    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    def __post_init__(self) -> None:
        """
        Validate that `DATABASE_URL` is present and uses PostgreSQL with `asyncpg`.
        
        Raises:
            ValueError: If `DATABASE_URL` is empty, or if it does not start with `"postgresql+asyncpg://"` indicating a PostgreSQL+asyncpg connection string.
        """
        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL must be set in the environment or .env file")
        if not self.DATABASE_URL.startswith("postgresql+asyncpg://"):
            raise ValueError(
                "DATABASE_URL must use PostgreSQL with asyncpg "
                "(postgresql+asyncpg://...)"
            )


# Global settings instance
settings = Settings()
