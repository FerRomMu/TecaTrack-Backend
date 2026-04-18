class TecaTrackError(Exception):
    """Base exception for all domain errors."""

    pass


class UserNotFoundError(TecaTrackError):
    """Raised when a user is not found."""

    pass


class UserAlreadyExistsError(TecaTrackError):
    """Raised when a user with the same email already exists."""

    pass

class OCRProcessingError(TecaTrackError):
    """Raised when OCR processing fails."""

    pass

class InvalidFileFormatError(TecaTrackError):
    """Raised when the file format is invalid."""

    pass