#!/usr/bin/env python3
"""
Script pour générer les clés secrètes nécessaires au déploiement
Utilisation : python generate_secrets.py
"""

import secrets


def generate_secret_key(length: int = 32) -> str:
    """
    Génère une clé secrète sécurisée

    Args:
        length: Longueur de la clé en bytes (32 par défaut = 256 bits)

    Returns:
        Clé secrète URL-safe en base64
    """
    return secrets.token_urlsafe(length)


def main():
    """
    Génère et affiche les clés nécessaires pour le déploiement
    """
    print("=" * 70)
    print("🔐 GÉNÉRATION DES CLÉS SECRÈTES POUR RENDER.COM")
    print("=" * 70)
    print()
    print("⚠️  IMPORTANT : Ces clés sont SENSIBLES et ne doivent JAMAIS être commitées")
    print("   Copiez-les directement dans l'interface Render.com")
    print()
    print("=" * 70)
    print()

    # Générer les clés
    secret_key = generate_secret_key(32)
    encryption_key = generate_secret_key(32)
    master_key = generate_secret_key(32)

    print("📋 Clés générées :")
    print()
    print("-" * 70)
    print("1️⃣  GENEWEB_SECURITY_SECRET_KEY")
    print("-" * 70)
    print(secret_key)
    print()

    print("-" * 70)
    print("2️⃣  GENEWEB_SECURITY_ENCRYPTION_KEY")
    print("-" * 70)
    print(encryption_key)
    print()

    print("-" * 70)
    print("3️⃣  GENEWEB_MASTER_KEY (optionnel pour GDPR)")
    print("-" * 70)
    print(master_key)
    print()

    print("=" * 70)
    print("📝 INSTRUCTIONS :")
    print("=" * 70)
    print()
    print("1. Allez sur Render.com → Dashboard → geneweb-api")
    print("2. Cliquez sur 'Environment' dans le menu de gauche")
    print("3. Ajoutez ces 3 variables avec les valeurs ci-dessus")
    print("4. Cliquez sur 'Save Changes'")
    print("5. Render redéploiera automatiquement")
    print()
    print("💡 Alternative : Utilisez le bouton 'Generate' dans Render")
    print()
    print("=" * 70)
    print()
    print("✅ Clés générées avec succès !")
    print()


if __name__ == "__main__":
    main()
