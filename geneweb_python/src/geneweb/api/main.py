"""
Main FastAPI application with security features
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .middleware.rate_limiting import IPWhitelistMiddleware, RateLimitMiddleware
from .middleware.security import (
    HTTPSRedirectMiddleware,
    RequestSizeMiddleware,
    SecurityHeadersMiddleware,
    TimingAttackMiddleware,
)
from .monitoring.metrics import setup_metrics
from .routers import health
from .security.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    """
    # Startup
    logger = logging.getLogger("geneweb.api")
    logger.info(
        "Starting Geneweb API",
        extra={
            "event": "startup",
            "version": settings.app_version,
            "debug": settings.debug,
        },
    )

    # Initialize database only if not already initialized (for testing)
    from .dependencies import db_manager

    # Check if database is already initialized (e.g., in tests)
    if db_manager.get_active_database_name() is None:
        try:
            db_manager.initialize()
            logger.info("Database initialized")
        except Exception as e:
            logger.warning(
                f"Failed to initialize database: {e}. "
                f"Will initialize on first request if needed."
            )
    else:
        logger.info(
            f"Database already initialized: {db_manager.get_active_database_name()}"
        )

    yield

    # Shutdown
    logger.info("Shutting down Geneweb API", extra={"event": "shutdown"})
    # Only close if we have an active database
    if db_manager.get_active_database_name() is not None:
        db_manager.close()


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application with security middlewares
    """
    # Setup structured logging first
    setup_logging()

    # Create FastAPI app
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Secure genealogy data management API",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
        lifespan=lifespan,
    )

    # Setup metrics collection (must be done before adding other middlewares)
    setup_metrics(app)

    # Configure trusted hosts (HTTPS enforcement)
    # In production environments like Fly.io, the reverse proxy handles host validation
    # so we can allow all hosts here. For self-hosted deployments, restrict this list.
    allowed_hosts = ["*"]

    app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)

    # HTTPS redirect middleware (should be first)
    app.add_middleware(HTTPSRedirectMiddleware)

    # Security headers middleware
    app.add_middleware(SecurityHeadersMiddleware)

    # Request size limiting for DDoS protection
    app.add_middleware(RequestSizeMiddleware, max_size=1024 * 1024)  # 1MB limit

    # IP whitelist middleware (before rate limiting)
    app.add_middleware(
        IPWhitelistMiddleware,
        whitelist=["127.0.0.1", "::1", "localhost"],
    )

    # Rate limiting middleware (disabled in test mode)
    import os

    if os.getenv("TESTING") != "1":
        app.add_middleware(
            RateLimitMiddleware,
            requests_per_minute=settings.security.rate_limit_per_minute,
            burst_limit=settings.security.rate_limit_burst,
        )

    # Timing attack protection
    app.add_middleware(TimingAttackMiddleware)

    # CORS middleware (configured from settings)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.security.cors_origins,
        allow_credentials=True,
        allow_methods=settings.security.cors_methods,
        allow_headers=settings.security.cors_headers,
        expose_headers=[
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-RateLimit-Reset",
        ],
    )

    # Compression middleware (should be last)
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # Exception handlers
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """
        Global exception handler that logs errors securely
        """
        logger = logging.getLogger("geneweb.api")

        # Log error without sensitive data
        logger.error(
            "Unhandled exception occurred",
            extra={
                "event": "exception",
                "exception_type": exc.__class__.__name__,
                "path": str(request.url.path),
                "method": request.method,
                "client_ip": request.client.host if request.client else "unknown",
            },
            exc_info=settings.debug,  # Only include traceback in debug mode
        )

        # Return generic error message (don't expose internal details)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "message": "An unexpected error occurred. Please try again later.",
                "request_id": id(request),  # Simple request ID for tracking
            },
        )

    # Root endpoint
    @app.get("/")
    async def root():
        """
        Root endpoint - API information
        """
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "status": "running",
            "docs": "/docs" if settings.debug else "disabled",
            "health": "/api/v1/health",
        }

    # Include routers
    app.include_router(health.router)

    # Include authentication router (CRITICAL - must be loaded first)
    try:
        from .routers import auth

        app.include_router(auth.router)
        logging.getLogger("geneweb.api").info(
            "Successfully loaded authentication router"
        )
    except ImportError as e:
        logging.getLogger("geneweb.api").warning(
            f"Could not load authentication router: {e}"
        )

    # Include database management router
    try:
        from .routers import database

        app.include_router(database.router, prefix="/api/v1/database")
        logging.getLogger("geneweb.api").info("Successfully loaded database router")
    except ImportError as e:
        logging.getLogger("geneweb.api").warning(f"Could not load database router: {e}")

    # Include person and GDPR routers
    try:
        from .routers import gdpr, persons

        app.include_router(persons.router)
        app.include_router(gdpr.router)
        logging.getLogger("geneweb.api").info(
            "Successfully loaded person and GDPR routers"
        )
    except ImportError as e:
        logging.getLogger("geneweb.api").warning(
            f"Could not load person/GDPR routers: {e}"
        )
        # Continue without these routers for now

    # Include search and genealogy routers with privacy protection
    try:
        from .routers import search

        app.include_router(search.router)
        logging.getLogger("geneweb.api").info(
            "Successfully loaded search and genealogy routers"
        )
    except ImportError as e:
        logging.getLogger("geneweb.api").warning(
            f"Could not load search/genealogy routers: {e}"
        )

    # Include family management router
    try:
        from .routers import family

        app.include_router(family.router)
        logging.getLogger("geneweb.api").info("Successfully loaded family router")
    except ImportError as e:
        logging.getLogger("geneweb.api").warning(f"Could not load family router: {e}")

    return app


# Create the application instance
app = create_app()
