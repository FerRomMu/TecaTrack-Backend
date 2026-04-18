from fastapi import UploadFile
from tecatrack_backend.ocr.ocr_processor import OCRProcessor
from tecatrack_backend.schemas.ocr_schemas import OCRResponse


class OCRService:

    def __init__(self,ocr_processor: OCRProcessor) -> None:
        self._ocr_processor = ocr_processor

    def process_receipt(self, file: UploadFile) -> OCRResponse:
        """
        Process an uploaded receipt image and return structured OCR data.

        Parameters:
            file (UploadFile): Uploaded image file (binary).

        Returns:
            OCRResponse: A response with one :class:`OCRPage` per document
                page, each containing raw text, detection blocks, and
                extracted receipt fields.
        """
        raw_bytes = file.file.read()
        return self._ocr_processor.process_receipt(raw_bytes)
