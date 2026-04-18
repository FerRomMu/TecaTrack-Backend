import uuid


class TecaTrackError(Exception):
    """Base exception for all domain errors."""

    pass


class EntityNotFoundError(TecaTrackError):
    def __init__(self, entity_name: str, identifier: str):
        self.entity_name = entity_name
        self.identifier = identifier
        super().__init__(f"{entity_name} with identifier {identifier} not found.")

class EntityAlreadyExistsError(TecaTrackError):
    def __init__(self, entity_name: str, identifier: uuid):
        super().__init__(f"{entity_name} with identifier {identifier} already exists.")