import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from redis.exceptions import RedisError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.common.enums import ErrorCode
from app.common.responses import ErrorBody, ErrorResponse
from app.core.exceptions import AppError, RateLimitedError
from app.core.logging import request_id_ctx

logger = logging.getLogger(__name__)

_HTTP_STATUS_CODES = {
    401: ErrorCode.UNAUTHORIZED,
    403: ErrorCode.FORBIDDEN,
    404: ErrorCode.NOT_FOUND,
    405: ErrorCode.NOT_FOUND,
    409: ErrorCode.CONFLICT,
    429: ErrorCode.RATE_LIMITED,
}


def error_response(
    status_code: int,
    code: ErrorCode,
    message: str,
    details: Any = None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    body = ErrorResponse(
        error=ErrorBody(code=code, message=message, details=details, request_id=request_id_ctx.get())
    )
    return JSONResponse(jsonable_encoder(body), status_code=status_code, headers=headers)


async def handle_app_error(_: Request, error: Exception) -> JSONResponse:
    if not isinstance(error, AppError):  # registered for AppError only
        raise error
    headers = {"Retry-After": str(error.retry_after_seconds)} if isinstance(error, RateLimitedError) else None
    return error_response(error.status_code, error.code, error.message, error.details, headers)


async def handle_validation_error(_: Request, error: Exception) -> JSONResponse:
    if not isinstance(error, RequestValidationError):
        raise error
    details = [
        {"field": ".".join(str(part) for part in item["loc"][1:]), "message": item["msg"]}
        for item in error.errors()
    ]
    return error_response(422, ErrorCode.VALIDATION_ERROR, "Request validation failed", details)


async def handle_http_error(_: Request, error: Exception) -> JSONResponse:
    if not isinstance(error, StarletteHTTPException):
        raise error
    code = _HTTP_STATUS_CODES.get(error.status_code, ErrorCode.INTERNAL_ERROR)
    return error_response(error.status_code, code, str(error.detail))


async def handle_redis_error(_: Request, error: Exception) -> JSONResponse:
    logger.error("redis unavailable", exc_info=error)
    return error_response(
        503, ErrorCode.SERVICE_UNAVAILABLE, "A dependency is unavailable, try again shortly"
    )


async def handle_unexpected_error(_: Request, error: Exception) -> JSONResponse:
    logger.exception("unhandled error", exc_info=error)
    return error_response(500, ErrorCode.INTERNAL_ERROR, "Internal server error")


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, handle_app_error)
    app.add_exception_handler(RequestValidationError, handle_validation_error)
    app.add_exception_handler(StarletteHTTPException, handle_http_error)
    app.add_exception_handler(RedisError, handle_redis_error)
    app.add_exception_handler(Exception, handle_unexpected_error)
