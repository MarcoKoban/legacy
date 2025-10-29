"""Simple API for testing configuration."""

from fastapi import FastAPI

from src.geneweb.api.config import settings

# Create simple API
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Secure genealogy API with environment configuration",
)


@app.get("/")
async def root():
    """Root endpoint showing configuration."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "debug": settings.debug,
        "cors_origins": settings.security.cors_origins,
        "rate_limit": settings.security.rate_limit_per_minute,
    }


@app.get("/health")
async def health():
    """Health check."""
    return {"status": "healthy", "version": settings.app_version}


@app.get("/config")
async def show_config():
    """Show current configuration (debug endpoint)."""
    return {
        "app": {
            "name": settings.app_name,
            "version": settings.app_version,
            "debug": settings.debug,
            "host": settings.host,
            "port": settings.port,
        },
        "security": {
            "rate_limit_per_minute": settings.security.rate_limit_per_minute,
            "rate_limit_burst": settings.security.rate_limit_burst,
            "cors_origins": settings.security.cors_origins,
            "force_https": settings.security.force_https,
        },
        "logging": {
            "log_level": settings.logging.log_level,
            "log_format": settings.logging.log_format,
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
