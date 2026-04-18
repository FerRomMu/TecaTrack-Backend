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
