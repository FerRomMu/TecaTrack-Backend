import cv2
import fitz
import numpy as np

from tecatrack_backend.core.exceptions import InvalidFileFormatError


PDF_MAGIC = b"%PDF"
SUPPORTED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp"}

class ImageConverter:
    """
    Converts raw file data into OpenCV BGR image arrays.

    Supported inputs:
    - Raw bytes of a PDF document (multi-page supported).
    - Raw bytes of a raster image (PNG, JPEG, TIFF, BMP, WEBP).
    """

    def from_bytes(self, raw_bytes: bytes) -> list[np.ndarray]:
        """
        Convert raw file bytes into one or more BGR images.

        Parameters:
            raw_bytes (bytes): Raw file content.
        Returns:
            list[np.ndarray]: One BGR image per page (PDF) or a single-item
                list for raster images.
        Raises:
            InvalidFileFormatError: If the bytes cannot be interpreted
                as a PDF or supported image format.
        """
        if raw_bytes[:4] == PDF_MAGIC:
            return self.pdf_bytes_to_images(raw_bytes)

        return [self._bytes_to_bgr(raw_bytes)]

    def pdf_bytes_to_images(self, pdf_bytes: bytes) -> list[np.ndarray]:
        """
        Rasterise every page of a PDF document at 300 DPI.

        Parameters:
            pdf_bytes (bytes): Raw bytes of a PDF file.

        Returns:
            list[np.ndarray]: One BGR image per PDF page, in page order.
        """
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        images: list[np.ndarray] = []

        for page in doc:
            pix = page.get_pixmap(dpi=300)
            img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
                pix.height, pix.width, pix.n
            )

            if pix.n == 4:  # RGBA → BGR
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            else:  # RGB → BGR
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

            images.append(img)

        doc.close()
        return images

    def _bytes_to_bgr(self, raw_bytes: bytes) -> np.ndarray:
        """
        Decode raw image bytes into a BGR NumPy array via OpenCV.

        Parameters:
            raw_bytes (bytes): Raw bytes of a supported raster image.

        Returns:
            np.ndarray: Decoded BGR image.

        Raises:
            InvalidFileFormatError: If OpenCV cannot decode the bytes.
        """
        arr = np.frombuffer(raw_bytes, dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)

        if img is None:
            raise InvalidFileFormatError(
                "Could not decode image bytes. "
                "Supported formats: PNG, JPEG, TIFF, BMP, WEBP, PDF."
            )

        return img
