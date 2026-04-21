import re
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    cuil: str

    @field_validator("cuil", mode="before")
    @classmethod
    def normalize_cuil(cls, v: str) -> str:
        """Strip dashes and validate that the result is exactly 11 digits."""
        normalized = re.sub(r"-", "", str(v))
        if not re.fullmatch(r"\d{11}", normalized):
            raise ValueError("cuil must be exactly 11 digits (dashes optional)")
        return normalized


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    email: EmailStr = Field(default=None)
    full_name: str = Field(default=None, min_length=1)


class UserRead(UserBase):
    id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
