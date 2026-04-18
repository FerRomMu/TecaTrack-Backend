from unittest.mock import MagicMock

from tecatrack_backend.core.exception_handlers import domain_exception_handler
from tecatrack_backend.core.exceptions import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
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
