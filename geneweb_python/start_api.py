#!/usr/bin/env python3
"""
Secure startup script for Geneweb API
Handles SSL configuration, security checks, and monitoring setup
"""

import argparse
import os
import ssl
import sys
from pathlib import Path

import uvicorn

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import after path modification
try:
    from geneweb.api.config import settings
    from geneweb.api.security.logging import get_api_logger, setup_logging
except ImportError as e:
    print(f"Failed to import modules: {e}")
    print("Make sure you're running from the correct directory")
    sys.exit(1)


def check_security_requirements():
    """
    Check security requirements before starting
    """
    logger = get_api_logger()
    errors = []
    warnings = []

    # Check HTTPS configuration
    # Note: In production environments like Fly.io, SSL is handled by the reverse proxy
    # SSL files are only required if explicitly
    # configured (both certfile and keyfile set)
    if not settings.debug:
        # Only warn if SSL is partially configured (one file set but not the other)
        if (settings.ssl_certfile and not settings.ssl_keyfile) or (
            settings.ssl_keyfile and not settings.ssl_certfile
        ):
            errors.append(
                "Both SSL certificate and key files must be provided together"
            )

        if not settings.security.force_https:
            warnings.append("HTTPS enforcement is disabled")

    # Check secret keys
    if len(settings.security.secret_key) < 32:
        errors.append("Secret key must be at least 32 characters long")

    if len(settings.security.encryption_key) < 32:
        errors.append("Encryption key must be at least 32 characters long")

    # Check CORS configuration
    if not settings.security.cors_origins:
        warnings.append(
            "CORS origins not configured - API will be accessible from any domain"
        )

    # Check rate limiting
    if settings.security.rate_limit_per_minute > 1000:
        warnings.append(
            "Rate limit is very high - consider lowering for better security"
        )

    # Log findings
    if errors:
        for error in errors:
            logger.error("Security check failed", error=error)
        return False

    if warnings:
        for warning in warnings:
            logger.warning("Security warning", warning=warning)

    logger.info("Security checks passed")
    return True


def setup_ssl_context():
    """
    Setup SSL context for HTTPS
    """
    if not settings.ssl_certfile or not settings.ssl_keyfile:
        return None

    # Verify certificate files exist
    if not os.path.exists(settings.ssl_certfile):
        raise FileNotFoundError(
            f"SSL certificate file not found: {settings.ssl_certfile}"
        )

    if not os.path.exists(settings.ssl_keyfile):
        raise FileNotFoundError(f"SSL key file not found: {settings.ssl_keyfile}")

    # Create SSL context
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

    # Load certificate and key
    ssl_context.load_cert_chain(
        certfile=settings.ssl_certfile, keyfile=settings.ssl_keyfile
    )

    # Load CA certificates if provided
    if settings.ssl_ca_certs and os.path.exists(settings.ssl_ca_certs):
        ssl_context.load_verify_locations(cafile=settings.ssl_ca_certs)

    # Security configurations
    ssl_context.set_ciphers(
        "ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS"
    )
    ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
    ssl_context.maximum_version = ssl.TLSVersion.TLSv1_3

    return ssl_context


def create_log_directory():
    """
    Create log directory if it doesn't exist
    """
    if settings.logging.log_file:
        log_dir = Path(settings.logging.log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)


def main():
    """
    Main startup function
    """
    parser = argparse.ArgumentParser(description="Start Geneweb API securely")
    parser.add_argument("--dev", action="store_true", help="Run in development mode")
    parser.add_argument("--host", default=settings.host, help="Host to bind to")
    parser.add_argument(
        "--port", type=int, default=settings.port, help="Port to bind to"
    )
    parser.add_argument(
        "--workers", type=int, default=settings.workers, help="Number of workers"
    )
    parser.add_argument(
        "--reload", action="store_true", help="Enable auto-reload (dev only)"
    )
    parser.add_argument(
        "--check-only", action="store_true", help="Only run security checks"
    )

    args = parser.parse_args()

    # Override debug mode if --dev is specified
    if args.dev:
        settings.debug = True
        settings.security.force_https = False

    # Setup logging first
    setup_logging()
    logger = get_api_logger()

    # Create log directory
    create_log_directory()

    logger.info(
        "Starting Geneweb API",
        version=settings.app_version,
        debug=settings.debug,
        host=args.host,
        port=args.port,
    )

    # Run security checks
    if not check_security_requirements():
        logger.error("Security checks failed - aborting startup")
        sys.exit(1)

    if args.check_only:
        logger.info("Security checks completed successfully")
        sys.exit(0)

    # Setup SSL context
    ssl_context = None
    if not args.dev and not settings.debug:
        try:
            ssl_context = setup_ssl_context()
            logger.info("SSL context configured")
        except Exception as e:
            logger.error("Failed to setup SSL context", error=str(e))
            sys.exit(1)

    # Configure uvicorn
    uvicorn_config = {
        "app": "geneweb.api.main:app",
        "host": args.host,
        "port": args.port,
        "workers": 1 if args.reload else args.workers,
        "reload": args.reload and args.dev,
        "ssl_context": ssl_context,
        "log_level": settings.logging.log_level.lower(),
        "access_log": True,
        "server_header": False,  # Don't expose server version
        "date_header": False,  # Don't expose server time
    }

    # Remove None values
    uvicorn_config = {k: v for k, v in uvicorn_config.items() if v is not None}

    try:
        logger.info("Starting uvicorn server", config=uvicorn_config)
        uvicorn.run(**uvicorn_config)
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error("Server failed to start", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
