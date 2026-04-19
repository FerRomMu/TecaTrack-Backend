from paddleocr import PaddleOCR


class OCREngine:
    """
    Lazy singleton that holds the shared PaddleOCR instance.

    The underlying model is downloaded and loaded only on the first call to
    :meth:`get`, keeping application startup time unaffected.  Subsequent calls
    return the cached instance immediately.
    """

    _instance: PaddleOCR | None = None

    @classmethod
    def get(cls) -> PaddleOCR:
        """
        Return the shared PaddleOCR instance, creating it if necessary.

        Returns:
            PaddleOCR: The initialized OCR engine configured for Spanish
                (Latin) text with textline orientation detection enabled.
        """
        if cls._instance is None:
            cls._instance = PaddleOCR(
                use_textline_orientation=True,
                lang="es",
                enable_mkldnn=False,
            )
        return cls._instance
