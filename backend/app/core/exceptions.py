"""Custom exception classes and FastAPI exception handlers."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class SalesIQException(Exception):
    """Base exception for SalesIQ application."""

    def __init__(self, detail: str = "An error occurred") -> None:
        self.detail = detail
        super().__init__(self.detail)


class NotFoundError(SalesIQException):
    """Resource not found (404)."""

    def __init__(self, resource: str = "Resource", identifier: str = "") -> None:
        detail = f"{resource} not found"
        if identifier:
            detail = f"{resource} with id '{identifier}' not found"
        super().__init__(detail=detail)


class UnauthorizedError(SalesIQException):
    """Authentication required or invalid credentials (401)."""

    def __init__(self, detail: str = "Invalid authentication credentials") -> None:
        super().__init__(detail=detail)


class ForbiddenError(SalesIQException):
    """Insufficient permissions (403)."""

    def __init__(self, detail: str = "Insufficient permissions") -> None:
        super().__init__(detail=detail)


class ConflictError(SalesIQException):
    """Resource conflict, e.g. duplicate entry (409)."""

    def __init__(self, detail: str = "Resource already exists") -> None:
        super().__init__(detail=detail)


class ValidationError(SalesIQException):
    """Business logic validation error (422)."""

    def __init__(self, detail: str = "Validation error") -> None:
        super().__init__(detail=detail)


def register_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers on the FastAPI app."""

    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": exc.detail})

    @app.exception_handler(UnauthorizedError)
    async def unauthorized_handler(request: Request, exc: UnauthorizedError) -> JSONResponse:
        return JSONResponse(status_code=401, content={"detail": exc.detail})

    @app.exception_handler(ForbiddenError)
    async def forbidden_handler(request: Request, exc: ForbiddenError) -> JSONResponse:
        return JSONResponse(status_code=403, content={"detail": exc.detail})

    @app.exception_handler(ConflictError)
    async def conflict_handler(request: Request, exc: ConflictError) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": exc.detail})

    @app.exception_handler(ValidationError)
    async def validation_handler(request: Request, exc: ValidationError) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": exc.detail})
