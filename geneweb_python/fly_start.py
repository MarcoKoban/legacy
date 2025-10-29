#!/usr/bin/env python3
"""
Startup script optimized for Fly.io deployment
"""

import sys
from pathlib import Path

import uvicorn

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import after path modification
try:
    from geneweb.api.config import settings
    from geneweb.api.main import app
    from geneweb.api.security.logging import get_api_logger, setup_logging
except ImportError as e:
    print(f"❌ Failed to import modules: {e}")
    print("Make sure you're running from the correct directory")
    sys.exit(1)


def main():
    """
    Main startup function for Fly.io deployment
    """
    # Setup logging
    setup_logging()
    logger = get_api_logger()

    # Get port from environment (Fly.io internal port is 8080)
    # Must match the internal_port in fly.toml
    port = 8080

    logger.info(
        "🚀 Starting Geneweb API on Fly.io",
        extra={
            "event": "startup",
            "app_name": settings.app_name,
            "version": settings.app_version,
            "port": port,
            "debug": settings.debug,
            "environment": "production" if not settings.debug else "development",
        },
    )

    print("=" * 60)
    print("🚀 Geneweb API - Fly.io Deployment")
    print("=" * 60)
    print(f"📊 Application: {settings.app_name}")
    print(f"🔧 Version: {settings.app_version}")
    print(f"🌐 Host: {settings.host}")
    print(f"🔌 Port: {port}")
    print(f"🐛 Debug: {settings.debug}")
    print("")
    print("ℹ️  Endpoints disponibles:")
    print("   • https://geneweb-api.fly.dev/health - Statut de santé")
    print("   • https://geneweb-api.fly.dev/metrics - Métriques Prometheus")
    print("   • https://geneweb-api.fly.dev/docs - Documentation API")
    print("")
    print("✅ HTTPS géré automatiquement par Fly.io")
    print("🔥 Service toujours actif (pas de sleep mode)")
    print("=" * 60)
    print("")

    try:
        # Uvicorn configuration optimized for Fly.io
        uvicorn.run(
            app,
            host="0.0.0.0",  # Must listen on all interfaces for Fly.io
            port=port,
            log_level=settings.logging.log_level.lower(),
            access_log=True,
            # Production settings
            workers=1,  # Use 1 worker for 512MB RAM
            loop="asyncio",
            # No SSL - handled by Fly.io's proxy
            ssl_keyfile=None,
            ssl_certfile=None,
            # Headers for proxy
            proxy_headers=True,
            forwarded_allow_ips="*",  # Trust Fly.io's proxy
        )
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
        print("\n🛑 Serveur arrêté")
    except Exception as e:
        logger.error(f"❌ Server error: {e}", exc_info=True)
        print(f"\n❌ Erreur: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
