from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.api.calculate import router as calculate_router
from app.api.history import router as history_router
from app.api.responses import error_response
from app.config import get_cors_origins
from app.database import get_history_repository


@asynccontextmanager
async def lifespan(_: FastAPI):
    get_history_repository().initialize()
    yield


app = FastAPI(title="Calculator Backend", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type"],
)
app.include_router(calculate_router)
app.include_router(history_router)


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(
    _: Request,
    __: RequestValidationError,
):
    return error_response(
        status.HTTP_422_UNPROCESSABLE_CONTENT,
        "INVALID_REQUEST",
        "The request data is invalid",
    )


@app.exception_handler(Exception)
async def unexpected_exception_handler(_: Request, __: Exception):
    return error_response(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "INTERNAL_ERROR",
        "An internal server error occurred",
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
