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

    def __post_init__(self):
        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL must be set in the environment or .env file")

# Global settings instance
settings = Settings()
