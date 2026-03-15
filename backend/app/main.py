"""FastAPI application factory with lifespan, CORS, Socket.IO, and router includes."""

from contextlib import asynccontextmanager

import socketio
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.middleware import RequestLoggingMiddleware, TenantMiddleware
from app.api.router import api_router
from app.realtime.socket_manager import sio

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    logger.info("salesiq_starting", env=settings.APP_ENV)
    yield
    logger.info("salesiq_shutting_down")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    application = FastAPI(
        title="SalesIQ API",
        description="Real-Time AI Sales & Lead Intelligence Engine",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Custom middleware
    application.add_middleware(RequestLoggingMiddleware)
    application.add_middleware(TenantMiddleware)

    # Exception handlers
    register_exception_handlers(application)

    # API routes
    application.include_router(api_router, prefix="/api")

    # Mount Socket.IO
    sio_app = socketio.ASGIApp(sio, other_app=application)

    return application


app = create_app()
