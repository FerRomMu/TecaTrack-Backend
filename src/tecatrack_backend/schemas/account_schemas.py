import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_validator


class AccountBase(BaseModel):
    bank: str
    balance: Decimal
    cbu: str
    user_id: uuid.UUID


class AccountCreate(AccountBase):
    pass


class AccountRead(AccountBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AccountsResponse(BaseModel):
    accounts: list[AccountRead]
    total_balance: Decimal

    @field_validator("total_balance", mode="before")
    @classmethod
    def format_balance(cls, v):
        return f"{float(v):.2f}"