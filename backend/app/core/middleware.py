"""Custom middleware for tenant context, request logging, and correlation IDs."""

import time
import uuid

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

logger = structlog.get_logger(__name__)

_SKIP_LOG_PATHS = {"/docs", "/redoc", "/openapi.json", "/health", "/ready"}


class TenantMiddleware(BaseHTTPMiddleware):
    """Extract tenant context from the authenticated user or request header.

    The primary tenant_id comes from the JWT (via get_current_user in dependencies).
    This middleware provides a fallback from the X-Tenant-ID header for
    unauthenticated endpoints and attaches it to request.state.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        tenant_id = request.headers.get("X-Tenant-ID")
        request.state.tenant_id = tenant_id
        response = await call_next(request)
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log every request with timing, correlation ID, and tenant context."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path in _SKIP_LOG_PATHS:
            return await call_next(request)

        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        request.state.correlation_id = correlation_id

        start_time = time.perf_counter()

        bind_vars: dict[str, str] = {
            "correlation_id": correlation_id,
            "method": request.method,
            "path": request.url.path,
        }
        tenant_id = getattr(request.state, "tenant_id", None)
        if tenant_id:
            bind_vars["tenant_id"] = tenant_id

        structlog.contextvars.bind_contextvars(**bind_vars)

        logger.info("request_started", client=request.client.host if request.client else "unknown")

        response = await call_next(request)

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.info(
            "request_completed",
            status_code=response.status_code,
            duration_ms=duration_ms,
        )

        response.headers["X-Correlation-ID"] = correlation_id
        structlog.contextvars.unbind_contextvars(
            "correlation_id", "method", "path", "tenant_id"
        )

        return response
