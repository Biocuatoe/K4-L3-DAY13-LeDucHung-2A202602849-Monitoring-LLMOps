from __future__ import annotations

import re
import secrets
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from structlog.contextvars import bind_contextvars, clear_contextvars


# Strict pattern: req- followed by exactly 8 lowercase hex characters
CORRELATION_ID_PATTERN = re.compile(r"^req-[0-9a-f]{8}$")


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Clear contextvars to avoid leakage between requests
        clear_contextvars()

        # Extract x-request-id from headers; accept only if it matches the strict contract
        header_id = request.headers.get("x-request-id", "")
        if CORRELATION_ID_PATTERN.match(header_id):
            correlation_id = header_id
        else:
            # Generate a new ID in the exact format: req-<8-hex>
            correlation_id = f"req-{secrets.token_hex(4)}"

        # Bind the correlation_id to structlog contextvars
        bind_contextvars(correlation_id=correlation_id)

        request.state.correlation_id = correlation_id

        start = time.perf_counter()
        response = await call_next(request)

        # Add the correlation_id and processing time to response headers
        response.headers["x-request-id"] = correlation_id
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        response.headers["x-response-time-ms"] = str(elapsed_ms)

        return response
