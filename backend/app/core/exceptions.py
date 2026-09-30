"""Domain errors raised by services. Handlers map them to the JSON error envelope; services never
raise HTTPException, so they stay independent of the web layer."""

from typing import Any

from app.common.enums import ErrorCode


class AppError(Exception):
    status_code = 500
    code = ErrorCode.INTERNAL_ERROR

    def __init__(self, message: str, details: Any = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details


class NotFoundError(AppError):
    status_code = 404
    code = ErrorCode.NOT_FOUND


class ValidationFailedError(AppError):
    status_code = 422
    code = ErrorCode.VALIDATION_ERROR


class UnauthorizedError(AppError):
    status_code = 401
    code = ErrorCode.UNAUTHORIZED


class ForbiddenError(AppError):
    status_code = 403
    code = ErrorCode.FORBIDDEN


class ConflictError(AppError):
    status_code = 409
    code = ErrorCode.CONFLICT


class RateLimitedError(AppError):
    status_code = 429
    code = ErrorCode.RATE_LIMITED

    def __init__(self, message: str, retry_after_seconds: int) -> None:
        super().__init__(message, details={"retry_after_seconds": retry_after_seconds})
        self.retry_after_seconds = retry_after_seconds
