from typing import Annotated

from pydantic import BaseModel, Field


class FileCreate(BaseModel):
    filename: str | None = None
    content_type: Annotated[str, Field(pattern=r"^image/(jpeg|png|webp)$")]
    data: Annotated[bytes, Field(min_length=1, max_length=5 * 1024 * 1024)]
