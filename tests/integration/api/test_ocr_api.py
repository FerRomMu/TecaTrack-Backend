import pytest
from httpx import AsyncClient
from pathlib import Path

@pytest.mark.asyncio
async def test_process_receipt_api_integration(async_client: AsyncClient):
    """
    Test the OCR endpoint /ocr/process-receipt using a real multipart file upload.
    This test verifies that the full flow (API -> Service -> Processor -> OCR Engine)
    works and returns the expected structured data for a specific test image.
    """
    receipt_path = Path("tests/integration/fixtures/receipts/comprobante.png")

    with open(receipt_path, "rb") as f:
        files = {
            "file": ("comprobante.png", f, "image/png")
        }
        response = await async_client.post("/ocr/process-receipt", files=files)

    assert response.status_code == 200
    data = response.json()
    
    expected_fields = {
        "amount": "8.300,00",
        "date": "24 de febrero de 2026",
        "time": "09:58",
        "cbu_cvu": "0170123420000005678912",
        "alias": None,
        "cuit_cuil": "20-12345678-9",
        "receipt_number": None,
        "destination_bank": "BBVA",
        "source_bank": "Brubank"
    }
    
    # Validación de la estructura y contenido de los campos extraídos
    assert "fields" in data
    assert data["fields"] == expected_fields
