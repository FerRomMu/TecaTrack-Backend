from unittest.mock import MagicMock

from tecatrack_backend.core.exception_handlers import domain_exception_handler
from tecatrack_backend.core.exceptions import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
    InvalidFileFormatError,
    OCRProcessingError,
    TecaTrackError,
)

mock_request: MagicMock = MagicMock()


def test_user_not_found_returns_404() -> None:
    response = domain_exception_handler(mock_request, EntityNotFoundError("User", "1"))
    assert response.status_code == 404


def test_user_already_exists_returns_400() -> None:
    response = domain_exception_handler(
        mock_request, EntityAlreadyExistsError("User", "1")
    )
    assert response.status_code == 400


def test_unmapped_domain_error_returns_500() -> None:
    class SomeNewError(TecaTrackError):
        pass

    response = domain_exception_handler(mock_request, SomeNewError())
    assert response.status_code == 500


def test_invalid_file_format_returns_422() -> None:
    response = domain_exception_handler(mock_request, InvalidFileFormatError())
    assert response.status_code == 422


def test_ocr_processing_error_returns_500() -> None:
    response = domain_exception_handler(mock_request, OCRProcessingError())
    assert response.status_code == 500
