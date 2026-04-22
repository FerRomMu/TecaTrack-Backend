import re
from typing import TypedDict

import cv2
import numpy as np

from tecatrack_backend.core.exceptions import OCRProcessingError
from tecatrack_backend.infrastructure.ocr.image_converter import ImageConverter
from tecatrack_backend.infrastructure.ocr.ocr_engine import OCREngine
from tecatrack_backend.infrastructure.ocr.patterns import PATTERNS
from tecatrack_backend.schemas.ocr_schemas import OCRResponse


class OCRBlock(TypedDict):
    bbox: list[list[float | int]]
    text: str
    confidence: float


class OCRProcessor:
    def __init__(self, converter: ImageConverter):
        self.converter = converter

    def process_receipt(self, raw_bytes: bytes) -> OCRResponse:
        images = self.converter.from_bytes(raw_bytes)

        full_text = ""
        for img in images:
            img = self._preprocess(img)
            text, _ = self._extract(img)
            text = self._normalize_ocr_text(text)
            full_text += text + "\n"

        return self._parse(full_text)

    def _preprocess(self, img_bgr: np.ndarray, min_width: int = 1000) -> np.ndarray:
        """
        Pre-process a BGR image for OCR.

        Parameters:
            img_bgr (np.ndarray): Input image in BGR colour space (as returned
                by OpenCV or :class:`ImageConverter`).
            min_width (int): Minimum pixel width below which the image is
                upscaled. Defaults to 1000.

        Returns:
            np.ndarray: Pre-processed BGR image ready to be passed to the OCR
                engine.
        """
        h, w = img_bgr.shape[:2]

        # upscale
        if w < min_width:
            scale = min_width / w
            img_bgr = cv2.resize(
                img_bgr,
                None,
                fx=scale,
                fy=scale,
                interpolation=cv2.INTER_CUBIC,
            )

        # denoising
        img_bgr = cv2.fastNlMeansDenoisingColored(
            img_bgr,
            None,
            h=6,
            hColor=6,
        )

        return img_bgr

    def _parse(self, text: str) -> OCRResponse:
        """
        Apply all regex patterns to ``text`` and return a mapping of field
        names to their extracted values.

        Parameters:
            text (str): Plain-text output from the OCR engine (newline-joined
                lines from a single page).

        Returns:
            OCRResponse: A response with one :class:`OCRResponse` with
                all the data extracted from the receipt.
        """
        data = {
            "amount": 0.0,
            "date": "",
            "time": "",
            "cbu": "",
            "alias": "",
            "cuil": "",
            "receipt_number": "",
            "source_bank": "",
            "destination_bank": "",
        }

        for field, pattern in PATTERNS.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = next((g for g in match.groups() if g is not None), None)
                if value is not None:
                    value = value.strip()
                    value = self._deduplicate_words(value)

                    if field == "amount":
                        data[field] = self._parse_amount(value)
                    elif field == "cuil":
                        data[field] = self._parse_cuil(value)
                    else:
                        data[field] = value

        return OCRResponse(**data)

    def _parse_amount(self, amount_str: str) -> float:
        """
        Clean amount string and convert to float.
        Handles common formats like 1.500,00 or 1500.00.
        """
        try:
            clean = re.sub(r"[^\d.,]", "", amount_str)

            if not clean:
                return 0.0

            # Case Dot as thousand, comma as decimal
            if "," in clean and "." in clean:
                if clean.find(".") < clean.find(","):
                    # Remove thousand separator, swap decimal
                    clean = clean.replace(".", "").replace(",", ".")
                else:
                    # Case: Comma as thousand, dot as decimal
                    clean = clean.replace(",", "")

            # Case: only comma present (could be decimal or thousand separator)
            elif "," in clean:
                left, right = clean.rsplit(",", 1)
                clean = (
                    clean.replace(",", "")
                    if len(right) == 3
                    else f"{left.replace('.', '')}.{right}"
                )

            # Case: only dot present (could be decimal or thousand separator)
            elif "." in clean:
                left, right = clean.rsplit(".", 1)
                clean = (
                    clean.replace(".", "")
                    if len(right) == 3
                    else f"{left.replace(',', '')}.{right}"
                )

            return float(clean)
        except (ValueError, TypeError):
            return 0.0

    def _parse_cuil(self, cuil_str: str) -> str:
        """
        Takes away the dots and hyphens from the cuil string.
        """
        try:
            clean = re.sub(r"[^\d]", "", cuil_str)

            if not clean:
                return ""

            return clean
        except (ValueError, TypeError):
            return ""

    def _extract(
        self,
        img_bgr: np.ndarray,
    ) -> tuple[str, list[OCRBlock]]:
        """
        Run OCR on ``img_bgr`` and return plain text plus structured blocks.

        Parameters:
            img_bgr (np.ndarray): Input image in BGR colour space.

        Returns:
            tuple[str, list[dict]]:
                - ``text`` (str): All accepted detections joined by newlines,
                  in top-to-bottom reading order.
                - ``blocks`` (list[dict]): Each item has the keys ``bbox``
                  (list of four [x, y] points), ``text`` (str), and
                  ``confidence`` (float rounded to 3 decimal places).

        Raises:
            OCRProcessingError: If PaddleOCR returns an unexpected result
                structure.
        """
        try:
            engine = OCREngine.get()
            result = engine.ocr(img_bgr)
        except Exception as exc:
            raise OCRProcessingError(
                f"PaddleOCR engine raised an error: {exc}"
            ) from exc

        if not result or not result[0]:
            return "", []

        blocks: list[OCRBlock] = []
        lines: list[str] = []

        res = result[0]

        if isinstance(res, dict) and "rec_texts" in res:
            texts = res.get("rec_texts", [])
            scores = res.get("rec_scores", [])
            polys = res.get("dt_polys", res.get("rec_polys", []))

            for i in range(len(texts)):
                text = texts[i]
                if not text:
                    continue

                confidence = float(scores[i]) if i < len(scores) else 0.0
                poly = polys[i] if i < len(polys) else []
                bbox = poly.tolist() if getattr(poly, "tolist", None) else list(poly)

                blocks.append(
                    {
                        "bbox": bbox,
                        "text": str(text),
                        "confidence": round(confidence, 3),
                    }
                )
                lines.append(str(text))
        else:
            raise OCRProcessingError(
                f"Unexpected OCR result structure: {type(res).__name__}"
            )

        return "\n".join(lines), blocks

    def _normalize_ocr_text(self, text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()

    def _deduplicate_words(self, text: str) -> str:
        return re.sub(r"\b(\w+)\s+\1\b", r"\1", text, flags=re.IGNORECASE)
