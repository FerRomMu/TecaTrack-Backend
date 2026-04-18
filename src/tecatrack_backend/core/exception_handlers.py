import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from tecatrack_backend.core.exceptions import (
    TecaTrackError,
    UserAlreadyExistsError,
    UserNotFoundError,
    OCRProcessingError,
    InvalidFileFormatError,
)

logger = logging.getLogger(__name__)

EXCEPTION_MAP: dict[type[TecaTrackError], tuple[int, str]] = {
    UserNotFoundError: (404, "User not found"),
    UserAlreadyExistsError: (400, "User already exists"),
    InvalidFileFormatError: (422, "Unsupported file format"),
    OCRProcessingError: (500, "OCR processing failed"),
}


def domain_exception_handler(request: Request, exc: TecaTrackError) -> JSONResponse:
    """
    Map a TecaTrackError to an HTTP JSONResponse using the module's EXCEPTION_MAP.

    If the exception type is present in EXCEPTION_MAP, the corresponding
    (status_code, message) pair is used; otherwise the handler returns a 500 status
    with the message "Internal domain error".

    Parameters:
        exc (TecaTrackError): Domain exception instance to convert into an HTTP
            response.

    Returns:
        JSONResponse: Response with `status_code` set to the mapped HTTP code and
            body `{"detail": <message>}`.
    """
    status_code, msg = EXCEPTION_MAP.get(type(exc), (500, "Internal domain error"))
    if status_code == 500:
        logger.exception("Unhandled domain error: %s", exc)
    else:
        logger.warning("Domain error [%s]: %s", exc.__class__.__name__, exc)
    return JSONResponse(status_code=status_code, content={"detail": msg})


def setup_exception_handlers(app: FastAPI) -> None:
    """
    Register the application's exception handler for domain errors.

    Adds an exception handler that converts any `TecaTrackError` raised during
    request handling into a JSON response with an appropriate HTTP status code and
    message.
    """
    app.add_exception_handler(TecaTrackError, domain_exception_handler)
