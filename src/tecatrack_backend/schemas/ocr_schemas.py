from pydantic import BaseModel


class OCRResponse(BaseModel):
    amount: float
    date: str
    time: str
    cbu: str
    alias: str
    cuil: str
    receipt_number: str
    source_bank: str
    destination_bank: str
