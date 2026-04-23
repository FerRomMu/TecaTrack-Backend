import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from tecatrack_backend.core.exceptions import (
    EntityNotFoundError,
    ReceiptValidationError,
)
from tecatrack_backend.schemas.ocr_schemas import OCRResponse
from tecatrack_backend.services.receipt_service import ReceiptService


@pytest.fixture
def mock_ocr_processor() -> MagicMock:
    """Return a mocked OCRProcessor."""
    processor = MagicMock()
    # process_receipt is called via asyncio.to_thread, so it should be a regular mock
    processor.process_receipt = MagicMock()
    return processor


@pytest.fixture
def mock_account_service() -> MagicMock:
    """Return a mocked AccountService with async methods."""
    service = MagicMock()
    service.get_account_by_bank = AsyncMock()
    service.update_balance = AsyncMock()
    return service


@pytest.fixture
def mock_file_repository() -> MagicMock:
    """Return a mocked FileRepository with async methods."""
    repo = MagicMock()
    repo.create = AsyncMock()
    return repo


@pytest.fixture
def receipt_service(
    mock_ocr_processor: MagicMock,
    mock_account_service: MagicMock,
    mock_file_repository: MagicMock,
) -> ReceiptService:
    return ReceiptService(
        ocr_processor=mock_ocr_processor,
        account_service=mock_account_service,
        file_repository=mock_file_repository,
    )


def _make_upload_file(content: bytes = b"dummy-image") -> MagicMock:
    upload = MagicMock()
    upload.read = AsyncMock(return_value=content)
    upload.filename = "test_receipt.png"
    upload.content_type = "image/png"
    return upload


@pytest.mark.asyncio
async def test_upload_receipt_success(
    receipt_service: ReceiptService,
    mock_ocr_processor: MagicMock,
    mock_account_service: MagicMock,
) -> None:
    # 1. Setup OCR Data
    ocr_data = OCRResponse(
        amount=1500.50,
        date="2026-04-20",
        time="10:00",
        cbu="1234567890123456789012",
        alias="test.alias",
        cuil="12345678901",
        receipt_number="123",
        source_bank="Bank A",
        destination_bank="Bank B",
    )
    mock_ocr_processor.process_receipt.return_value = ocr_data

    # 2. Setup Account Data
    mock_source_account = MagicMock(id=uuid.uuid4())
    mock_dest_account = MagicMock(id=uuid.uuid4())

    mock_account_service.get_account_by_bank.side_effect = [
        mock_source_account,
        mock_dest_account,
    ]

    # 3. Execute
    await receipt_service.upload_receipt(_make_upload_file())

    # 4. Verify
    mock_ocr_processor.process_receipt.assert_called_once()
    assert mock_account_service.get_account_by_bank.call_count == 2

    # Check balance updates
    # Source account should be decreased
    mock_account_service.update_balance.assert_any_call(
        mock_source_account, Decimal("-1500.50")
    )
    # Destination account should be increased
    mock_account_service.update_balance.assert_any_call(
        mock_dest_account, Decimal("1500.50")
    )


@pytest.mark.asyncio
async def test_upload_receipt_source_account_not_found(
    receipt_service: ReceiptService,
    mock_ocr_processor: MagicMock,
    mock_account_service: MagicMock,
) -> None:
    ocr_data = OCRResponse(
        amount=100.0,
        date="2026-04-20",
        time="10:00",
        cbu="1",
        alias="a",
        cuil="123",
        receipt_number="1",
        source_bank="Missing Bank",
        destination_bank="Dest Bank",
    )
    mock_ocr_processor.process_receipt.return_value = ocr_data
    mock_account_service.get_account_by_bank.side_effect = EntityNotFoundError(
        "Account", "Missing Bank"
    )

    with pytest.raises(EntityNotFoundError):
        await receipt_service.upload_receipt(_make_upload_file())

    mock_account_service.update_balance.assert_not_called()


@pytest.mark.asyncio
async def test_upload_receipt_destination_account_not_found(
    receipt_service: ReceiptService,
    mock_ocr_processor: MagicMock,
    mock_account_service: MagicMock,
) -> None:
    ocr_data = OCRResponse(
        amount=100.0,
        date="2026-04-20",
        time="10:00",
        cbu="1",
        alias="a",
        cuil="123",
        receipt_number="1",
        source_bank="Source Bank",
        destination_bank="Missing Bank",
    )
    mock_ocr_processor.process_receipt.return_value = ocr_data

    mock_source_account = MagicMock(id=uuid.uuid4())
    mock_account_service.get_account_by_bank.side_effect = [
        mock_source_account,
        EntityNotFoundError("Account", "Missing Bank"),
    ]

    with pytest.raises(EntityNotFoundError):
        await receipt_service.upload_receipt(_make_upload_file())

    mock_account_service.update_balance.assert_not_called()


@pytest.mark.asyncio
async def test_upload_receipt_invalid_amount_zero(
    receipt_service: ReceiptService,
    mock_ocr_processor: MagicMock,
) -> None:
    ocr_data = OCRResponse(
        amount=0.0,
        date="2026-04-20",
        time="10:00",
        cbu="1234567890123456789012",
        alias="a",
        cuil="123",
        receipt_number="1",
        source_bank="Bank A",
        destination_bank="Bank B",
    )
    mock_ocr_processor.process_receipt.return_value = ocr_data

    with pytest.raises(ReceiptValidationError) as exc_info:
        await receipt_service.upload_receipt(_make_upload_file())

    assert "Invalid amount detected" in str(exc_info.value)


@pytest.mark.asyncio
async def test_upload_receipt_missing_cuil(
    receipt_service: ReceiptService,
    mock_ocr_processor: MagicMock,
) -> None:
    ocr_data = OCRResponse(
        amount=100.0,
        date="2026-04-20",
        time="10:00",
        cbu="1234567890123456789012",
        alias="a",
        cuil="",  # Empty CUIL
        receipt_number="1",
        source_bank="Bank A",
        destination_bank="Bank B",
    )
    mock_ocr_processor.process_receipt.return_value = ocr_data

    with pytest.raises(ReceiptValidationError) as exc_info:
        await receipt_service.upload_receipt(_make_upload_file())

    assert "CUIL not found" in str(exc_info.value)


@pytest.mark.asyncio
async def test_upload_receipt_missing_bank(
    receipt_service: ReceiptService,
    mock_ocr_processor: MagicMock,
) -> None:
    ocr_data = OCRResponse(
        amount=100.0,
        date="2026-04-20",
        time="10:00",
        cbu="1234567890123456789012",
        alias="a",
        cuil="123",
        receipt_number="1",
        source_bank="",  # Empty bank
        destination_bank="Bank B",
    )
    mock_ocr_processor.process_receipt.return_value = ocr_data

    with pytest.raises(ReceiptValidationError) as exc_info:
        await receipt_service.upload_receipt(_make_upload_file())

    assert "Source bank not found" in str(exc_info.value)
