#!/usr/bin/env python3
"""Test manual du serveur API pour valider le démarrage"""

if __name__ == "__main__":
    import uvicorn

    from src.geneweb.api.config import settings
    from src.geneweb.api.main import app

    print("🚀 Démarrage du serveur API Geneweb")
    print(f"📊 Application: {settings.app_name}")
    print(f"🔧 Version: {settings.app_version}")
    print(f"🌐 Host: {settings.host}")
    print(f"🔌 Port: {settings.port}")
    print(f"🐛 Debug: {settings.debug}")
    print("")
    print("ℹ️  Endpoints disponibles:")
    print("   • http://localhost:8000/health/ - Statut de santé")
    print("   • http://localhost:8000/metrics - Métriques Prometheus")
    print("   • http://localhost:8000/docs - Documentation API (mode debug)")
    print("")
    print("🔴 Appuyez sur Ctrl+C pour arrêter")
    print("")

    try:
        # Use port 8002 for testing to avoid conflicts
        test_port = 8002
        print(f"🔌 Using test port: {test_port}")
        uvicorn.run(
            app,
            host=settings.host,
            port=test_port,
            reload=False,  # Can't use reload when passing app object directly
            log_level=settings.logging.log_level.lower(),
        )
    except KeyboardInterrupt:
        print("\n🛑 Serveur arrêté par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
