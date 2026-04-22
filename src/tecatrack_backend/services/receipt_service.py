import asyncio
from decimal import Decimal

from fastapi import UploadFile

from tecatrack_backend.infrastructure.ocr.ocr_processor import OCRProcessor
from tecatrack_backend.repositories.file_repository import FileRepository
from tecatrack_backend.schemas.file_schemas import FileCreate
from tecatrack_backend.services.account_service import AccountService


class ReceiptService:
    def __init__(
        self,
        ocr_processor: OCRProcessor,
        account_service: AccountService,
        file_repository: FileRepository,
    ) -> None:
        self._ocr_processor = ocr_processor
        self._account_service = account_service
        self._file_repository = file_repository

    async def upload_receipt(self, file: UploadFile) -> None:
        """
        Processes a receipt image, uploads it to the database and updates the balances
        of the accounts.

        Parameters:
            file (UploadFile): Uploaded image file (binary).
        """
        raw_bytes = await file.read()
        await self._upload_file(raw_bytes, file.filename, file.content_type)
        receipt_data = await asyncio.to_thread(
            self._ocr_processor.process_receipt, raw_bytes
        )
        amount = Decimal(str(receipt_data.amount))

        source_account = await self._account_service.get_account_by_bank(
            receipt_data.cuil, receipt_data.source_bank
        )
        destination_account = await self._account_service.get_account_by_bank(
            receipt_data.cuil, receipt_data.destination_bank
        )

        await self._account_service.update_balance(source_account, -amount)
        await self._account_service.update_balance(destination_account, amount)

    async def _upload_file(
        self, raw_bytes: bytes, file_name: str, content_type: str
    ) -> None:
        """
        Uploads a file to the database.

        Parameters:
            raw_bytes (bytes): Raw bytes of the file.
            file_name (str): Name of the file.
            content_type (str): Content type of the file.
        """
        file_create = FileCreate(
            filename=file_name,
            content_type=content_type,
            data=raw_bytes,
        )
        await self._file_repository.create(file_create)
