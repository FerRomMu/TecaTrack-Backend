from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from tecatrack_backend.core.exceptions import (
    TecaTrackError,
    UserAlreadyExistsError,
    UserNotFoundError,
)

EXCEPTION_MAP: dict[type[Exception], tuple[int, str]] = {
    UserNotFoundError: (404, "User not found"),
    UserAlreadyExistsError: (400, "User already exists"),
}


def domain_exception_handler(request: Request, exc: TecaTrackError) -> JSONResponse:
    status_code, msg = EXCEPTION_MAP.get(type(exc), (500, "Internal domain error"))
    return JSONResponse(status_code=status_code, content={"detail": msg})


def setup_exception_handlers(app: FastAPI):
    app.add_exception_handler(TecaTrackError, domain_exception_handler)
