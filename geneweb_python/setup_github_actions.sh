#!/bin/bash
# Script pour obtenir le token Fly.io pour GitHub Actions

set -e

echo "🔐 Configuration du token Fly.io pour GitHub Actions"
echo "=================================================="
echo ""

# Vérifier que flyctl est installé
if ! command -v flyctl &> /dev/null; then
    echo "❌ flyctl n'est pas installé"
    echo "Installer avec: curl -L https://fly.io/install.sh | sh"
    exit 1
fi

echo "✅ flyctl est installé"
echo ""

# Vérifier l'authentification
if ! flyctl auth whoami &> /dev/null; then
    echo "⚠️  Vous n'êtes pas authentifié sur Fly.io"
    echo "Authentification en cours..."
    flyctl auth login
fi

echo "✅ Authentifié sur Fly.io"
echo ""

# Générer le token
echo "🔑 Génération du token d'accès..."
TOKEN=$(flyctl auth token)

if [ -z "$TOKEN" ]; then
    echo "❌ Erreur lors de la génération du token"
    exit 1
fi

echo "✅ Token généré avec succès!"
echo ""
echo "=================================================="
echo "📋 Token Fly.io:"
echo ""
echo "$TOKEN"
echo ""
echo "=================================================="
echo ""
echo "📝 Étapes suivantes:"
echo ""
echo "1. Copier le token ci-dessus"
echo ""
echo "2. Aller sur GitHub:"
echo "   https://github.com/EpitechPGE45-2025/G-ING-900-PAR-9-1-legacy-22/settings/secrets/actions"
echo ""
echo "3. Cliquer sur 'New repository secret'"
echo ""
echo "4. Configurer:"
echo "   Name: FLY_API_TOKEN"
echo "   Secret: [Coller le token]"
echo ""
echo "5. Cliquer sur 'Add secret'"
echo ""
echo "✅ Une fois configuré, les déploiements automatiques fonctionneront!"
echo ""

# Optionnel : copier dans le presse-papier si disponible
if command -v xclip &> /dev/null; then
    echo "$TOKEN" | xclip -selection clipboard
    echo "📋 Token copié dans le presse-papier!"
elif command -v pbcopy &> /dev/null; then
    echo "$TOKEN" | pbcopy
    echo "📋 Token copié dans le presse-papier!"
fi
