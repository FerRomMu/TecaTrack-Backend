import asyncio
from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile

from tecatrack_backend.ocr.image_converter import ImageConverter
from tecatrack_backend.ocr.ocr_processor import OCRProcessor
from tecatrack_backend.schemas.ocr_schemas import OCRResponse
from tecatrack_backend.services.ocr_service import OCRService

router = APIRouter(prefix="/ocr", tags=["OCR"])


def get_ocr_service() -> OCRService:
    """
    FastAPI dependency that constructs a fully wired :class:`OCRService`.
    """
    processor = OCRProcessor(converter=ImageConverter())
    return OCRService(ocr_processor=processor)


@router.post("/process-receipt", response_model=OCRResponse)
async def process_receipt(
    service: Annotated[OCRService, Depends(get_ocr_service)],
    file: UploadFile = File(...),
) -> OCRResponse:
    """
    Process an uploaded receipt image and return structured OCR data.

    Parameters:
        file (UploadFile): Uploaded image file (e.g., PNG, JPEG, TIFF).

    Returns:
        OCRResponse: Structured OCR results for all pages in the document.
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, service.process_receipt, file)
