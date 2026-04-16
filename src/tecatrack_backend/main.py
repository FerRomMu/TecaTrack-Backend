from fastapi import FastAPI
from pydantic import BaseModel

from tecatrack_backend.core.exception_handlers import setup_exception_handlers

app = FastAPI(
    title="TecaTrack Backend API",
    description="Backend API for TecaTrack",
    version="0.1.0",
)

setup_exception_handlers(app)


class HealthResponse(BaseModel):
    status: str


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """
    Health check endpoint to verify that the service is up and running.
    """
    return HealthResponse(status="ok")
