from unittest.mock import AsyncMock, MagicMock

import pytest

from tecatrack_backend.infrastructure.ocr.ocr_processor import OCRProcessor
from tecatrack_backend.schemas.ocr_schemas import OCRResponse
from tecatrack_backend.services.ocr_service import OCRService


@pytest.fixture
def mock_processor() -> MagicMock:
    """Return a fully mocked OCRProcessor."""
    return MagicMock(spec=OCRProcessor)


@pytest.fixture
def ocr_service(mock_processor: MagicMock) -> OCRService:
    return OCRService(ocr_processor=mock_processor)


def _make_upload_file(content: bytes = b"dummy-image") -> MagicMock:
    """
    Build a minimal UploadFile-like mock whose .read() is an AsyncMock
    returning the provided content.
    """
    upload = MagicMock()
    upload.read = AsyncMock(return_value=content)
    return upload


@pytest.mark.asyncio
async def test_process_receipt_returns_value_from_processor(
    ocr_service: OCRService, mock_processor: MagicMock
) -> None:
    """
    OCRService.process_receipt must return exactly the OCRResponse that the
    underlying OCRProcessor produces — no transformation, no wrapping.
    """
    expected = OCRResponse(fields={"amount": "1500", "date": None})
    mock_processor.process_receipt.return_value = expected

    result = await ocr_service.process_receipt(_make_upload_file(b"image-bytes"))

    assert result is expected


@pytest.mark.asyncio
async def test_process_receipt_passes_raw_bytes_to_processor(
    ocr_service: OCRService, mock_processor: MagicMock
) -> None:
    """
    OCRService must read the file in binary mode and forward the exact raw
    bytes to OCRProcessor.process_receipt.
    """
    content = b"raw-image-data"
    mock_processor.process_receipt.return_value = OCRResponse(fields={})

    await ocr_service.process_receipt(_make_upload_file(content))

    mock_processor.process_receipt.assert_called_once_with(content)


@pytest.mark.asyncio
async def test_process_receipt_returns_ocr_response_type(
    ocr_service: OCRService, mock_processor: MagicMock
) -> None:
    """
    The return type of OCRService.process_receipt must be an OCRResponse
    instance so that FastAPI can serialise it correctly.
    """
    mock_processor.process_receipt.return_value = OCRResponse(fields={"amount": "200"})

    result = await ocr_service.process_receipt(_make_upload_file())

    assert isinstance(result, OCRResponse)


@pytest.mark.asyncio
async def test_process_receipt_with_empty_file_passes_empty_bytes(
    ocr_service: OCRService, mock_processor: MagicMock
) -> None:
    """
    OCRService must not short-circuit on empty uploads — it should still
    forward the empty bytes to the processor.
    """
    mock_processor.process_receipt.return_value = OCRResponse(fields={})

    await ocr_service.process_receipt(_make_upload_file(b""))

    mock_processor.process_receipt.assert_called_once_with(b"")
