from pydantic import BaseModel


class FileCreate(BaseModel):
    filename: str | None = None
    content_type: str
    data: bytes
