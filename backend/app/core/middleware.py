import logging
import re
import uuid
from time import perf_counter

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.common.constants import REQUEST_ID_HEADER, REQUEST_ID_MAX_LENGTH
from app.core.logging import request_id_ctx

logger = logging.getLogger("app.request")
_SAFE_REQUEST_ID = re.compile(rf"^[A-Za-z0-9_-]{{1,{REQUEST_ID_MAX_LENGTH}}}$")


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Assigns a request id (or keeps a safe incoming one), returns it as a header and logs the request."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        incoming = request.headers.get(REQUEST_ID_HEADER, "")
        request_id = incoming if _SAFE_REQUEST_ID.match(incoming) else uuid.uuid4().hex
        request_id_ctx.set(request_id)
        started = perf_counter()
        response = await call_next(request)
        response.headers[REQUEST_ID_HEADER] = request_id
        logger.info(
            "request",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "duration_ms": round((perf_counter() - started) * 1000, 1),
            },
        )
        return response
