from fastapi import APIRouter, Depends, File, UploadFile, status
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from tecatrack_backend.infrastructure.ocr.image_converter import ImageConverter
from tecatrack_backend.infrastructure.ocr.ocr_processor import OCRProcessor
from tecatrack_backend.services.receipt_service import ReceiptService
from tecatrack_backend.repositories import UserRepository
from tecatrack_backend.repositories.account_repository import AccountRepository
from tecatrack_backend.services.account_service import AccountService
from tecatrack_backend.core.database import get_db

router = APIRouter(prefix="/receipts", tags=["Receipts"])

def get_receipt_service(session: Annotated[AsyncSession, Depends(get_db)]) -> ReceiptService:
    """
    Create a ReceiptService configured with an OCRProcessor and an AccountService.

    Parameters:
        session (AsyncSession): Database session to be used by the repository.

    Returns:
        ReceiptService: Service instance that uses an OCRProcessor and an AccountService.
    """
    image_converter = ImageConverter()
    ocr_processor = OCRProcessor(image_converter)
    account_repo = AccountRepository(session)
    user_repo = UserRepository(session)
    account_service = AccountService(account_repo, user_repo)
    
    return ReceiptService(ocr_processor, account_service)


@router.post("/upload-receipt", status_code=status.HTTP_200_OK)
async def upload_receipt(
    file: UploadFile = File(...),
    service: ReceiptService = Depends(get_receipt_service)
) -> None:
    """
    Upload a receipt image for processing, balance updates and storage.

    Parameters:
        file (UploadFile): Uploaded image file (binary).
        service (ReceiptService): Receipt service for handling the upload.
    """
    await service.upload_receipt(file)
