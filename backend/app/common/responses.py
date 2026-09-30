from typing import Any

from pydantic import BaseModel

from app.common.enums import ErrorCode


class ApiResponse[T](BaseModel):
    """Single-object response envelope: `{"data": {...}}`."""

    data: T


class ErrorBody(BaseModel):
    code: ErrorCode
    message: str
    details: Any = None
    request_id: str | None = None


class ErrorResponse(BaseModel):
    error: ErrorBody


ERROR_RESPONSES: dict[int | str, dict[str, Any]] = {
    status: {"model": ErrorResponse} for status in (401, 403, 404, 409, 422, 429)
}
