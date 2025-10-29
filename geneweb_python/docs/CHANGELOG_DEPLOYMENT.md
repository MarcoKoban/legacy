# Changelog - Déploiement Fly.io

## [Version 15] - 2025-10-23

### 🚀 Déploiement Fly.io - Production Ready

#### ✨ Ajouté

**Fichiers de configuration Fly.io**
- `fly.toml` : Configuration complète de l'application Fly.io
  - Port 8080 configuré
  - Région Amsterdam (ams)
  - Health checks toutes les 10s
  - Variables d'environnement
  - Configuration des volumes

- `Dockerfile.fly` : Dockerfile optimisé pour Fly.io
  - Base Python 3.11-slim
  - Multi-stage build
  - Utilisateur non-root (appuser, uid 1000)
  - Health check intégré
  - Taille finale : ~76 MB

- `fly_start.py` : Script de démarrage personnalisé
  - Port 8080 forcé
  - Host 0.0.0.0
  - Gestion des signaux (SIGTERM, SIGINT)
  - Shutdown gracieux
  - Logging structuré

- `.dockerignore` : Exclusion des fichiers inutiles du build
  - Cache Python (__pycache__, .pytest_cache)
  - Fichiers Git
  - Environnements virtuels
  - Documentation
  - Tests

**Router de health check simplifié**
- `src/geneweb/api/routers/simple_health.py`
  - Endpoint `/` sans dépendances
  - Pas de connexion DB requise
  - Réponse immédiate `{"status": "ok"}`
  - Endpoint `/ping` pour les tests

**Documentation**
- `DEPLOYMENT_FLY.md` : Guide complet de déploiement Fly.io
  - Installation et configuration
  - Gestion de la base de données
  - Secrets et variables d'environnement
  - Monitoring et logs
  - Troubleshooting complet
  - Workflow de développement

- `FRONTEND_INTEGRATION.md` : Guide d'intégration frontend
  - Configuration Angular
  - Services HTTP
  - Gestion de l'authentification
  - Intercepteurs
  - Exemples de code
  - Tests de l'API

- `DEPLOYMENT_QUICK_START.md` : Guide rapide
  - Statut du déploiement
  - URLs importantes
  - Commandes essentielles
  - Prochaines étapes

**Secrets de sécurité**
- `generate_secrets.py` : Générateur de clés sécurisées
  - SECRET_KEY pour JWT
  - ENCRYPTION_KEY pour les données sensibles
  - Utilise `secrets.token_urlsafe()`

#### 🔧 Modifié

**Configuration de l'application**
- `src/geneweb/api/config.py`
  - Port par défaut changé de 8000 à 8080
  - Alignement avec les standards Fly.io

**Middleware de sécurité**
- `src/geneweb/api/main.py`
  - TrustedHostMiddleware : Détection automatique de Fly.io
  - `allowed_hosts=["*"]` quand `FLY_APP_NAME` est défini
  - Évite les 400 Bad Request des health checks

- `src/geneweb/api/middleware/rate_limiting.py`
  - Exclusion de `/health/` (avec slash final) du rate limiting
  - Évite les 429 Too Many Requests des health checks
  - Paths exclus : `/health`, `/health/`, `/metrics`, `/docs`, `/openapi.json`

**Router principal**
- `src/geneweb/api/main.py`
  - Ajout du router `simple_health` sur `/health`
  - Router `health` détaillé déplacé sur `/health/detailed`
  - Meilleure séparation des responsabilités

#### 🐛 Corrigé

**Problèmes de health check**
1. **400 Bad Request**
   - Cause : TrustedHostMiddleware bloquait les requêtes Fly.io
   - Fix : Détection automatique de Fly.io via variable d'environnement
   - Résultat : Health checks passent maintenant

2. **429 Too Many Requests**
   - Cause : Rate limiting appliqué aux health checks
   - Fix : Exclusion explicite de `/health/` dans le middleware
   - Résultat : Pas de limitation pour les checks Fly.io

3. **Port mismatch**
   - Cause : Application sur 8000, Fly.io attend 8080
   - Fix : Port 8080 forcé dans config.py, fly_start.py, fly.toml
   - Résultat : Application écoute correctement sur 0.0.0.0:8080

4. **Problèmes IPv6 - Région Frankfurt (cdg)**
   - Cause : Infrastructure Fly.io avec problèmes IPv6
   - Fix : Migration vers Amsterdam (ams)
   - Résultat : Stabilité améliorée

#### 🗄️ Base de données

**PostgreSQL sur Fly.io**
- Application : `geneweb-db`
- Taille : 256MB RAM, 1GB stockage
- Région : Amsterdam (ams)
- Réseau : Privé Fly.io (*.flycast)
- Connexion : Automatiquement configurée via DATABASE_URL

**Volume de stockage**
- Nom : `geneweb_data`
- Taille : 1GB
- Région : Amsterdam (ams)
- Point de montage : `/data`

#### 🔐 Sécurité

**Secrets configurés**
- `GENEWEB_SECURITY_SECRET_KEY` : Clé pour JWT
- `GENEWEB_SECURITY_ENCRYPTION_KEY` : Clé de chiffrement
- `DATABASE_URL` : Connexion PostgreSQL (auto-configuré)

**Variables d'environnement**
- `GENEWEB_API_PORT=8080`
- `GENEWEB_API_HOST=0.0.0.0`
- `GENEWEB_DEBUG=false`
- `GENEWEB_SECURITY_FORCE_HTTPS=true`
- `FLY_APP_NAME=geneweb-api` (auto par Fly.io)

#### 📊 Performances

**Optimisations Docker**
- Layers en cache pour builds rapides (~2s quand seul le code change)
- Requirements.txt copié avant le code source
- Multi-stage build pour réduire la taille
- Image finale : 76 MB (vs ~200MB sans optimisation)

**Health checks**
- Intervalle : 10 secondes
- Timeout : 2 secondes
- Grace period : 5 secondes
- Status actuel : ✅ 2/2 passing

#### 🌍 Déploiement

**Infrastructure**
- Plateforme : Fly.io
- Application : geneweb-api
- URL : https://geneweb-api.fly.dev
- Région : Amsterdam (ams)
- Machine : shared-cpu-1x (256MB RAM)
- Coût : 0€/mois (tier gratuit)

**Statut**
- Version : 15
- État : Started
- Health checks : 2 total, 2 passing
- Dernière mise à jour : 2025-10-23T20:31:30Z

#### 📝 Documentation

**Guides créés**
1. Guide complet de déploiement (95KB de doc)
2. Guide d'intégration frontend
3. Guide de démarrage rapide
4. Troubleshooting détaillé

**Exemples de code**
- Services Angular pour consommer l'API
- Intercepteurs HTTP
- Gestion de l'authentification
- Tests avec curl et Postman

#### 🎯 Workflow

**Développement → Production**
1. Développement local sur port 8000
2. Tests unitaires avec pytest
3. Build Docker local pour validation
4. Déploiement Fly.io via `flyctl deploy`
5. Health checks automatiques
6. Rollback possible si problème

#### ⚠️ Breaking Changes

**Port changé de 8000 à 8080**
- Impact : Le frontend doit être mis à jour
- Action requise : Modifier environment.prod.ts avec la nouvelle URL
- Développement local : Reste sur 8000 (pas d'impact)

**Nouveaux endpoints health check**
- `/health/` : Simple check (utilisé par Fly.io)
- `/health/detailed` : Check détaillé avec infos DB
- Ancien endpoint `/health` : Redirige vers `/health/`

#### 🔄 Migration depuis Render.com

**Fichiers Render.com à supprimer** (optionnel)
- `render.yaml`
- `render_start.py`
- `DEPLOYMENT_RENDER.md`
- `.env.render.example`

**Raison de la migration**
- Render.com bloqué : Permissions organisation GitHub
- Railway.app : Même problème
- Fly.io : Déploiement depuis la machine locale (pas de GitHub requis)

#### ✅ Tests effectués

**Endpoints testés**
- ✅ `GET /health/` → 200 OK, `{"status":"ok"}`
- ✅ `GET /docs` → Documentation Swagger accessible
- ✅ Health checks Fly.io → 2/2 passing
- ✅ Connexion base de données → Opérationnelle
- ✅ Application publiquement accessible

**Performance**
- ✅ Build Docker : ~2s (avec cache)
- ✅ Déploiement complet : ~2 minutes
- ✅ Health check response time : <100ms
- ✅ Taille image : 76 MB

#### 📚 Ressources

**Liens utiles**
- Dashboard : https://fly.io/apps/geneweb-api/monitoring
- Documentation : https://fly.io/docs/
- Status : https://status.flyio.net/
- API Docs : https://geneweb-api.fly.dev/docs

#### 🎓 Leçons apprises

1. **Plateforme deployment** : Fly.io plus flexible que Render pour les projets GitHub partagés
2. **Health checks** : Doivent être ultra-simples, sans dépendances
3. **Middleware** : Attention aux restrictions qui peuvent bloquer les health checks
4. **Port standardisation** : 8080 est le standard pour les apps web sur Fly.io
5. **Documentation** : Essentielle pour le troubleshooting et l'onboarding

#### 🚀 Prochaines étapes

**Immédiat**
- [ ] Mettre à jour le frontend avec la nouvelle URL
- [ ] Tester l'intégration complète
- [ ] Commit et push des changements

**Court terme**
- [ ] Restreindre CORS aux domaines autorisés
- [ ] Configurer des sauvegardes DB automatiques
- [ ] Mettre en place des alertes de monitoring
- [ ] Optimiser les coûts si nécessaire

**Long terme**
- [ ] Scaling horizontal si besoin
- [ ] CDN pour les assets statiques
- [ ] Cache Redis pour les performances
- [ ] CI/CD automatisé

---

## [Versions précédentes]

### [Version 14 et antérieures]
- Développement local
- Tests et implémentation des features
- Configuration initiale pour Render.com (abandonnée)

---

**Auteur** : Équipe Geneweb  
**Date** : 23 octobre 2025  
**Status** : ✅ Production Ready
