import asyncio

from fastapi import UploadFile

from tecatrack_backend.infrastructure.ocr.ocr_processor import OCRProcessor
from tecatrack_backend.schemas.ocr_schemas import OCRResponse


class OCRService:
    def __init__(self, ocr_processor: OCRProcessor) -> None:
        self._ocr_processor = ocr_processor

    async def process_receipt(self, file: UploadFile) -> OCRResponse:
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
