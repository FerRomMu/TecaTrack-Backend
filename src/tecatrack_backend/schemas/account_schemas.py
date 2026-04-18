import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class AccountBase(BaseModel):
    bank: str
    balance: Decimal
    cbu: str


class AccountCreate(AccountBase):
    pass

class AccountRead(AccountBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AccountsResponse(BaseModel):
    accounts: list[AccountRead]
    total: int