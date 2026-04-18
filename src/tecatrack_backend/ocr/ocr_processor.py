import cv2
import numpy as np
import re

from tecatrack_backend.ocr.ocr_engine import OCREngine
from tecatrack_backend.ocr.image_converter import ImageConverter
from tecatrack_backend.schemas.ocr_schemas import OCRResponse
from tecatrack_backend.core.exceptions import OCRProcessingError
from tecatrack_backend.ocr.patterns import PATTERNS


class OCRProcessor:
    def __init__(self, converter: ImageConverter):
        self.converter = converter

    def process_receipt(self, raw_bytes: bytes) -> OCRResponse:
        images = self.converter.from_bytes(raw_bytes)
        
        full_text = ""
        for img in images:
            img = self._preprocess(img)
            text, _ = self._extract(img)
            text = self.normalize_ocr_text(text)
            full_text += text + "\n"
            
        fields = self._parse(full_text)
        return OCRResponse(fields=fields)
    
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

        #denoising 
        img_bgr = cv2.fastNlMeansDenoisingColored(
            img_bgr,
            None,
            h=6,
            hColor=6,
        )

        return img_bgr

    def _parse(self, text: str) -> dict[str, str | None]:
        """
        Apply all regex patterns to ``text`` and return a mapping of field
        names to their extracted values.

        Parameters:
            text (str): Plain-text output from the OCR engine (newline-joined
                lines from a single page).

        Returns:
            dict[str, str | None]: A dictionary with one key per pattern in
                :data:`PATTERNS`.  Values are stripped strings when a match is
                found, or ``None`` otherwise.
        """
        fields: dict[str, str | None] = {}

        for field, pattern in PATTERNS.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = next((g for g in match.groups() if g is not None), None)
                fields[field] = value.strip() if value else None
            else:
                fields[field] = None

        return fields

    def _extract(
        self,
        img_bgr: np.ndarray,
    ) -> tuple[str, list[dict]]:
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
        engine = OCREngine.get()

        try:
            result = engine.ocr(img_bgr)
        except Exception as exc:
            raise OCRProcessingError(
                f"PaddleOCR engine raised an error: {exc}"
            ) from exc

        if not result or not result[0]:
            return "", []

        blocks: list[dict] = []
        lines: list[str] = []
        
        res = result[0]

        # Formato PaddleOCR v3.x (PaddleX) - Diccionario
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
                
                blocks.append({
                    "bbox": bbox,
                    "text": str(text),
                    "confidence": round(confidence, 3),
                })
                lines.append(str(text))

        return "\n".join(lines), blocks

    def normalize_ocr_text(self, text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()