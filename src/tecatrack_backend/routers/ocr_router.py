from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from tecatrack_backend.core.database import get_db
from tecatrack_backend.infrastructure.ocr.image_converter import ImageConverter
from tecatrack_backend.infrastructure.ocr.ocr_processor import OCRProcessor
from tecatrack_backend.repositories.file_repository import FileRepository
from tecatrack_backend.schemas.ocr_schemas import OCRResponse
from tecatrack_backend.services.ocr_service import OCRService

router = APIRouter(prefix="/ocr", tags=["OCR"])


async def get_ocr_service(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> OCRService:
    """
    FastAPI dependency that constructs a fully wired :class:`OCRService`.
    """
    processor = OCRProcessor(converter=ImageConverter())
    file_repository = FileRepository(session)
    return OCRService(ocr_processor=processor, file_repository=file_repository)


@router.post("/process-receipt", response_model=OCRResponse)
async def process_receipt(
    service: Annotated[OCRService, Depends(get_ocr_service)],
    file: Annotated[UploadFile, File()],
) -> OCRResponse:
    """
    Process an uploaded receipt image and return structured OCR data.

    Parameters:
        file (UploadFile): Uploaded image file (e.g., PNG, JPEG, TIFF).

    Returns:
        OCRResponse: Structured OCR results for all pages in the document.
    """
    return await service.process_receipt(file)
