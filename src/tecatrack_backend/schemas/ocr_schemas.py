from pydantic import BaseModel


class OCRResponse(BaseModel):
    fields: dict[str, str | None]
