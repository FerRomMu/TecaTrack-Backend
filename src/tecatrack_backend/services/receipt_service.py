import asyncio

from fastapi import UploadFile

from tecatrack_backend.infrastructure.ocr.ocr_processor import OCRProcessor
from tecatrack_backend.services.account_service import AccountService
from tecatrack_backend.schemas.ocr_schemas import OCRResponse
from decimal import Decimal


class ReceiptService:
    def __init__(self, ocr_processor: OCRProcessor, account_service: AccountService) -> None:
        self._ocr_processor = ocr_processor
        self._account_service = account_service

    async def upload_receipt(self, file: UploadFile) -> None:
        """
        Processes a receipt image and uploads it to the database.

        Parameters:
            file (UploadFile): Uploaded image file (binary).

        Returns:
            OCRResponse: A response with one :class:`OCRResponse`. with
            all the data extracted from the receipt.
        """
        receipt_data = await self._process_receipt(file)
        amount = Decimal(str(receipt_data.amount))
        
        source_account = await self._account_service.get_account_by_bank(receipt_data.cuil, receipt_data.source_bank)
        destination_account = await self._account_service.get_account_by_bank(receipt_data.cuil, receipt_data.destination_bank)
        
        await self._account_service.update_balance(source_account, -amount)
        await self._account_service.update_balance(destination_account, amount)

    async def _process_receipt(self, file: UploadFile) -> OCRResponse:
        """
        Process an uploaded receipt image and return structured OCR data.

        Parameters:
            file (UploadFile): Uploaded image file (binary).

        Returns:
            OCRResponse: A response with one :class:`OCRResponse`. with
            all the data extracted from the receipt.
        """
        raw_bytes = await file.read()
        return await asyncio.to_thread(self._ocr_processor.process_receipt, raw_bytes)
