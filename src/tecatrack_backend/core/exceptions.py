import uuid


class TecaTrackError(Exception):
    """Base exception for all domain errors."""

    pass


class EntityNotFoundError(TecaTrackError):
    def __init__(self, entity_name: str, identifier: str):
        """
        Initialize an EntityNotFoundError for a missing entity.

        Parameters:
            entity_name (str): The name of the entity type (e.g., "User", "Order").
            identifier (str): The identifier of the missing entity; stored on the
            exception instance and included in the exception message.
        """
        self.entity_name = entity_name
        self.identifier = identifier
        super().__init__(f"{entity_name} with identifier {identifier} not found.")


class EntityAlreadyExistsError(TecaTrackError):
    def __init__(self, entity_name: str, identifier: uuid):
        """
        Initialize an exception indicating that an entity with the given identifier
        already exists.

        Parameters:
            entity_name (str): Name of the entity type (e.g., "User").
            identifier (uuid.UUID): The unique identifier of the existing entity.

        Details:
            Stores `entity_name` and `identifier` as instance attributes and sets the
            exception message to "<entity_name> with identifier <identifier> already
            exists."
        """
        super().__init__(f"{entity_name} with identifier {identifier} already exists.")


class InvalidEntityError(TecaTrackError):
    def __init__(self, entity_name: str, field_name: str):
        """
        Initialize an exception indicating that an entity with the given identifier
        already exists.

        Parameters:
            entity_name (str): Name of the entity type (e.g., "User").
            field_name (str): The field name of the existing entity.

        Details:
            Stores `entity_name` and `field_name` as instance attributes and sets the
            exception message to "<entity_name> with invalid {field_name}".
        """
        super().__init__(f"{entity_name} with invalid {field_name}")


class OCRProcessingError(TecaTrackError):
    """Raised when OCR processing fails."""

    pass


class DuplicateEntityError(TecaTrackError):
    def __init__(self, entity_name: str, identifier: str):
        """
        Initialize a DuplicateEntityError for multiple entities found.

        Parameters:
            entity_name (str): The name of the entity type (e.g., "Account").
            identifier (str): The identifier that returned multiple results.
        """
        self.entity_name = entity_name
        self.identifier = identifier
        super().__init__(
            f"Multiple {entity_name} entities found with identifier {identifier}."
        )


class DuplicateAccountError(DuplicateEntityError):
    def __init__(self, bank_name: str):
        """
        Initialize a DuplicateAccountError for multiple accounts in the same bank.

        Parameters:
            bank_name (str): The name of the bank.
        """
        super().__init__("Account", bank_name)


class InvalidFileFormatError(TecaTrackError):
    """Raised when the file format is invalid."""

    pass


class ReceiptValidationError(TecaTrackError):
    def __init__(self, message: str):
        """
        Initialize a ReceiptValidationError for invalid OCR data.

        Parameters:
            message (str): Descriptive error message.
        """
        super().__init__(message)
