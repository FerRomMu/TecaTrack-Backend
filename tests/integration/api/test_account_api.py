import uuid
from decimal import Decimal

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tecatrack_backend.models import Account


@pytest.mark.asyncio
async def test_create_account_api_success(
    async_client: AsyncClient, db_session: AsyncSession
) -> None:
    # 1. Create a user first (Account needs user_id)
    user_data = {"email": "account_owner@example.com", "full_name": "Account Owner"}
    user_res = await async_client.post("/users/", json=user_data)
    assert user_res.status_code == 201
    user_id = user_res.json()["id"]

    # 2. Create the account
    account_data = {
        "bank": "Teca Bank",
        "balance": "100.50",
        "cbu": "1234567890123456789012",
        "user_id": user_id,
    }

    response = await async_client.post("/accounts/", json=account_data)

    # 3. Verify response
    assert response.status_code == 201
    data = response.json()
    assert data["bank"] == account_data["bank"]
    assert data["cbu"] == account_data["cbu"]
    assert data["balance"] == "100.50"
    assert "id" in data

    # 4. Verify DB
    account_uuid = uuid.UUID(data["id"])
    result = await db_session.execute(select(Account).where(Account.id == account_uuid))
    db_account = result.scalar_one_or_none()
    assert db_account is not None
    assert db_account.bank == account_data["bank"]
    assert db_account.balance == Decimal("100.50")


@pytest.mark.asyncio
async def test_create_account_duplicate_cbu_api(async_client: AsyncClient) -> None:
    # 1. Create a user
    user_data = {"email": "dup_cbu@example.com", "full_name": "Dup CBU"}
    user_res = await async_client.post("/users/", json=user_data)
    user_id = user_res.json()["id"]

    account_data = {
        "bank": "Teca Bank",
        "balance": "0.00",
        "cbu": "9999999999999999999999",
        "user_id": user_id,
    }

    # 2. Create first account
    res1 = await async_client.post("/accounts/", json=account_data)
    assert res1.status_code == 201

    # 3. Attempt duplicate CBU
    res2 = await async_client.post("/accounts/", json=account_data)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_account_api_success(async_client: AsyncClient) -> None:
    # 1. Create user and account
    user_res = await async_client.post("/users/", json={"email": "get_acc@ex.com", "full_name": "Get Acc"})
    user_id = user_res.json()["id"]
    
    acc_data = {
        "bank": "Bank Inc",
        "balance": "50.00",
        "cbu": "1111111111111111111111",
        "user_id": user_id
    }
    create_res = await async_client.post("/accounts/", json=acc_data)
    acc_id = create_res.json()["id"]

    # 2. Fetch by ID
    response = await async_client.get(f"/accounts/{acc_id}")
    assert response.status_code == 200
    assert response.json()["cbu"] == acc_data["cbu"]


@pytest.mark.asyncio
async def test_get_account_api_not_found(async_client: AsyncClient) -> None:
    fake_id = str(uuid.uuid4())
    response = await async_client.get(f"/accounts/{fake_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_account_by_cbu_api_success(async_client: AsyncClient) -> None:
    # 1. Create user and account
    user_res = await async_client.post("/users/", json={"email": "cbu_acc@ex.com", "full_name": "CBU Acc"})
    user_id = user_res.json()["id"]
    cbu = "2222222222222222222222"
    
    await async_client.post("/accounts/", json={
        "bank": "CBU Bank",
        "balance": "0.00",
        "cbu": cbu,
        "user_id": user_id
    })

    # 2. Fetch by CBU
    response = await async_client.get(f"/accounts/cbu/{cbu}")
    assert response.status_code == 200
    assert response.json()["bank"] == "CBU Bank"


@pytest.mark.asyncio
async def test_get_accounts_by_user_api_success(async_client: AsyncClient) -> None:
    # 1. Create user
    user_res = await async_client.post("/users/", json={"email": "user_accs@ex.com", "full_name": "User Accs"})
    user_id = user_res.json()["id"]
    
    # 2. Create two accounts
    await async_client.post("/accounts/", json={
        "bank": "Bank A", "balance": "100.00", "cbu": "3333333333333333333333", "user_id": user_id
    })
    await async_client.post("/accounts/", json={
        "bank": "Bank B", "balance": "200.50", "cbu": "4444444444444444444444", "user_id": user_id
    })

    # 3. Fetch all accounts for user
    response = await async_client.get(f"/accounts/user/{user_id}")
    assert response.status_code == 200
    data = response.json()
    
    assert len(data["accounts"]) == 2
    assert data["total_balance"] == "300.50"
