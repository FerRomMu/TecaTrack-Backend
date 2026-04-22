from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tecatrack_backend.main import app
from tecatrack_backend.models import Account, User
from tecatrack_backend.repositories import FileRepository, UserRepository
from tecatrack_backend.repositories.account_repository import AccountRepository
from tecatrack_backend.routers.receipt_router import get_receipt_service
from tecatrack_backend.schemas.ocr_schemas import OCRResponse
from tecatrack_backend.services.account_service import AccountService
from tecatrack_backend.services.receipt_service import ReceiptService


@pytest.mark.asyncio
async def test_upload_receipt_api_success(
    async_client: AsyncClient, db_session: AsyncSession
) -> None:
    """
    Integration test for POST /receipts/upload-receipt.

    Verifies that uploading a receipt:
    1. Processes the image via OCR (mocked).
    2. Identifies source and destination accounts.
    3. Updates balances in the database.
    """
    # 1. Setup Test Data
    cuil = "20111111112"
    user = User(email="receipt_test@example.com", full_name="Receipt Test", cuil=cuil)
    db_session.add(user)
    await db_session.flush()

    source_account = Account(
        bank="Banco Galicia",
        cbu="0070123420000005678912",
        balance=Decimal("5000.00"),
        user_id=user.id,
    )
    dest_account = Account(
        bank="Banco BBVA",
        cbu="0170123420000005678912",
        balance=Decimal("0.00"),
        user_id=user.id,
    )
    db_session.add_all([source_account, dest_account])
    await db_session.commit()

    # 2. Mock OCR Response
    mock_ocr_response = OCRResponse(
        amount=1500.0,
        date="2026-04-20",
        time="10:00",
        cbu="0070123420000005678912",
        alias="test.alias",
        cuil=cuil,
        receipt_number="999",
        source_bank="Banco Galicia",
        destination_bank="Banco BBVA",
    )

    async def override_get_receipt_service() -> ReceiptService:
        mock_processor = MagicMock()
        mock_processor.process_receipt.return_value = mock_ocr_response

        account_repo = AccountRepository(db_session)
        user_repo = UserRepository(db_session)
        file_repo = FileRepository(db_session)
        account_service = AccountService(account_repo, user_repo)

        return ReceiptService(mock_processor, account_service, file_repo)

    app.dependency_overrides[get_receipt_service] = override_get_receipt_service
    try:
        # 3. Execute API Call
        # dummy file since the processor is mocked
        files = {"file": ("dummy.png", b"fake-image-content", "image/png")}
        response = await async_client.post("/receipts/upload-receipt", files=files)

        # 4. Verify Response
        assert response.status_code == 200

        # 5. Verify DB State
        await db_session.refresh(source_account)
        await db_session.refresh(dest_account)

        assert source_account.balance == Decimal("3500.00")  # 5000 - 1500
        assert dest_account.balance == Decimal("1500.00")  # 0 + 1500
    finally:
        app.dependency_overrides.pop(get_receipt_service, None)
