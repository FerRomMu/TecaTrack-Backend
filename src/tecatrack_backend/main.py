import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel

from tecatrack_backend.core.exception_handlers import setup_exception_handlers
from tecatrack_backend.infrastructure.ocr.ocr_engine import OCREngine
from tecatrack_backend.routers.account_router import router as account_router
from tecatrack_backend.routers.ocr_router import router as ocr_router
from tecatrack_backend.routers.user_router import router as user_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.

    On startup: warms up the OCR engine so that models are downloaded and
    loaded into memory before the first request arrives.
    On shutdown: no explicit teardown is required.
    """
    logger.info("Loading OCR engine")
    OCREngine.get()
    logger.info("OCR engine loaded.")
    yield


app = FastAPI(
    title="TecaTrack Backend API",
    description="Backend API for TecaTrack",
    version="0.1.0",
    lifespan=lifespan,
)

# Setup exception handlers
setup_exception_handlers(app)

# Include routers
app.include_router(user_router)
app.include_router(ocr_router)
app.include_router(account_router)


class HealthResponse(BaseModel):
    status: str


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """
    Health check endpoint to verify that the service is up and running.
    """
    return HealthResponse(status="ok")
