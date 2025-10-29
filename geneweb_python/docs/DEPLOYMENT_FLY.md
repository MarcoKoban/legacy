# Déploiement sur Fly.io

Ce document décrit le processus de déploiement de l'API Geneweb sur Fly.io.

## 📋 Table des matières

- [Vue d'ensemble](#vue-densemble)
- [Prérequis](#prérequis)
- [Installation et Configuration](#installation-et-configuration)
- [Structure des fichiers](#structure-des-fichiers)
- [Déploiement](#déploiement)
- [Gestion de la base de données](#gestion-de-la-base-de-données)
- [Secrets et Variables d'environnement](#secrets-et-variables-denvironnement)
- [Monitoring et Logs](#monitoring-et-logs)
- [Commandes utiles](#commandes-utiles)
- [Dépannage](#dépannage)

## 🎯 Vue d'ensemble

L'application est déployée sur **Fly.io** avec les caractéristiques suivantes :

- **Nom de l'application** : `geneweb-api`
- **URL publique** : https://geneweb-api.fly.dev
- **Région** : Amsterdam (ams)
- **Base de données** : PostgreSQL sur Fly.io (`geneweb-db`)
- **Port interne** : 8080
- **Runtime** : Python 3.11 (Uvicorn/FastAPI)

## 📦 Prérequis

### 1. Installation de Fly.io CLI

```bash
curl -L https://fly.io/install.sh | sh
```

Ajouter Fly.io au PATH (ajouter à `~/.bashrc` ou `~/.zshrc`) :

```bash
export FLYCTL_INSTALL="$HOME/.fly"
export PATH="$FLYCTL_INSTALL/bin:$PATH"
```

### 2. Authentification

```bash
flyctl auth login
```

## 🔧 Installation et Configuration

### Étape 1 : Créer l'application

```bash
cd geneweb_python
flyctl launch --no-deploy
```

Répondre aux questions :
- App name: `geneweb-api`
- Region: `ams` (Amsterdam)
- PostgreSQL: Non (on la créera manuellement)
- Deploy now: Non

### Étape 2 : Créer la base de données PostgreSQL

```bash
# Créer la base de données
flyctl postgres create --name geneweb-db --region ams --initial-cluster-size 1

# Attacher la base de données à l'application
flyctl postgres attach geneweb-db --app geneweb-api
```

Cela configure automatiquement la variable d'environnement `DATABASE_URL`.

### Étape 3 : Créer le volume de stockage

```bash
flyctl volumes create geneweb_data --region ams --size 1 --app geneweb-api
```

### Étape 4 : Configurer les secrets

```bash
# Générer les clés de sécurité
python generate_secrets.py

# Définir les secrets (remplacer par les valeurs générées)
flyctl secrets set \
  GENEWEB_SECURITY_SECRET_KEY="votre_secret_key" \
  GENEWEB_SECURITY_ENCRYPTION_KEY="votre_encryption_key" \
  --app geneweb-api
```

## 📁 Structure des fichiers

### `fly.toml`

Configuration principale de l'application Fly.io :

```toml
app = 'geneweb-api'
primary_region = 'ams'

[build]
  dockerfile = "Dockerfile.fly"

[env]
  GENEWEB_API_PORT = '8080'
  GENEWEB_API_HOST = '0.0.0.0'
  GENEWEB_DEBUG = 'false'
  GENEWEB_SECURITY_FORCE_HTTPS = 'true'

[mounts]
  source = "geneweb_data"
  destination = "/data"

[[services]]
  protocol = "tcp"
  internal_port = 8080

  [[services.ports]]
    port = 80
    handlers = ["http"]
    force_https = true

  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]

  [[services.http_checks]]
    interval = "10s"
    timeout = "2s"
    grace_period = "5s"
    method = "GET"
    path = "/health/"
```

### `Dockerfile.fly`

Dockerfile optimisé pour Fly.io :

- Base : Python 3.11-slim
- Multi-stage build
- Utilisateur non-root (appuser)
- Health check intégré
- Taille finale : ~76 MB

### `fly_start.py`

Script de démarrage personnalisé :

- Configuration du port 8080
- Gestion des signaux (SIGTERM, SIGINT)
- Initialisation de la base de données
- Logging structuré

### `.dockerignore`

Exclut les fichiers inutiles du build Docker :
- `__pycache__`, `.pytest_cache`
- `.git`, `.env`
- Documentation et tests
- Fichiers de développement

## 🚀 Déploiement

### Déploiement initial

```bash
flyctl deploy
```

### Déploiements suivants

```bash
# Déploiement standard
flyctl deploy

# Voir les logs pendant le déploiement
flyctl deploy --verbose
```

### Vérifier l'état

```bash
flyctl status
```

Résultat attendu :
```
Machines
PROCESS ID              VERSION REGION  STATE   CHECKS
app     xxxxx           X       ams     started 2 total, 2 passing
```

## 💾 Gestion de la base de données

### Connexion à la base de données

```bash
# Se connecter via psql
flyctl postgres connect --app geneweb-db

# Voir les informations de connexion
flyctl postgres db list --app geneweb-db
```

### Configuration de connexion

La variable `DATABASE_URL` est automatiquement configurée au format :
```
postgres://user:password@host:5432/database
```

Elle est accessible dans l'application via :
```python
from geneweb.api.config import settings
db_url = settings.database_url
```

### Sauvegardes

```bash
# Créer une sauvegarde manuelle
flyctl postgres backup create --app geneweb-db

# Lister les sauvegardes
flyctl postgres backup list --app geneweb-db
```

## 🔐 Secrets et Variables d'environnement

### Variables d'environnement publiques (dans `fly.toml`)

```toml
[env]
  GENEWEB_API_PORT = '8080'
  GENEWEB_API_HOST = '0.0.0.0'
  GENEWEB_DEBUG = 'false'
  GENEWEB_SECURITY_FORCE_HTTPS = 'true'
```

### Secrets (confidentiels)

```bash
# Définir un secret
flyctl secrets set KEY=value --app geneweb-api

# Lister les secrets (pas les valeurs)
flyctl secrets list --app geneweb-api

# Supprimer un secret
flyctl secrets unset KEY --app geneweb-api
```

### Secrets requis

- `GENEWEB_SECURITY_SECRET_KEY` : Clé pour les tokens JWT
- `GENEWEB_SECURITY_ENCRYPTION_KEY` : Clé pour le chiffrement des données
- `DATABASE_URL` : Configuré automatiquement par Fly.io

## 📊 Monitoring et Logs

### Logs en temps réel

```bash
# Tous les logs
flyctl logs --app geneweb-api

# Suivre les logs en continu
flyctl logs --app geneweb-api --tail
```

### Dashboard de monitoring

```bash
# Ouvrir le dashboard web
flyctl dashboard --app geneweb-api
```

URL directe : https://fly.io/apps/geneweb-api/monitoring

### Health checks

L'application expose plusieurs endpoints de santé :

- `/health/` : Health check simple (utilisé par Fly.io)
- `/health/detailed` : Health check détaillé avec état de la DB
- `/metrics` : Métriques Prometheus (si activées)

## 🛠️ Commandes utiles

### Gestion de l'application

```bash
# Voir l'état de l'application
flyctl status --app geneweb-api

# Redémarrer l'application
flyctl apps restart geneweb-api

# Suspendre l'application (économie de coûts)
flyctl scale count 0 --app geneweb-api

# Réactiver l'application
flyctl scale count 1 --app geneweb-api --region ams
```

### Gestion des machines

```bash
# Lister les machines
flyctl machines list --app geneweb-api

# SSH dans une machine
flyctl ssh console --app geneweb-api

# Exécuter une commande dans une machine
flyctl ssh console --app geneweb-api -C "python -c 'import sys; print(sys.version)'"
```

### Scaling

```bash
# Scaler horizontalement (nombre d'instances)
flyctl scale count 2 --app geneweb-api

# Scaler verticalement (taille des machines)
flyctl scale vm shared-cpu-2x --app geneweb-api

# Voir la configuration actuelle
flyctl scale show --app geneweb-api
```

### Volumes

```bash
# Lister les volumes
flyctl volumes list --app geneweb-api

# Voir les détails d'un volume
flyctl volumes show vol_xxxxx

# Créer un snapshot
flyctl volumes snapshots create vol_xxxxx
```

## 🐛 Dépannage

### L'application ne démarre pas

1. Vérifier les logs :
```bash
flyctl logs --app geneweb-api
```

2. Vérifier que le port est correct (8080) :
```bash
flyctl ssh console --app geneweb-api -C "netstat -tuln | grep 8080"
```

3. Vérifier les variables d'environnement :
```bash
flyctl ssh console --app geneweb-api -C "env | grep GENEWEB"
```

### Health check échoue (400 Bad Request)

**Cause** : Le `TrustedHostMiddleware` bloquait les requêtes de Fly.io.

**Solution** : Le code détecte automatiquement Fly.io via `FLY_APP_NAME` et désactive la restriction :

```python
import os
if os.getenv("FLY_APP_NAME"):
    allowed_hosts = ["*"]
```

### Health check échoue (429 Too Many Requests)

**Cause** : Le rate limiting était appliqué aux health checks.

**Solution** : Le middleware exclut maintenant `/health/` :

```python
if request.url.path in ["/health", "/health/", "/metrics", "/docs", "/openapi.json"]:
    return await call_next(request)
```

### Erreur de connexion à la base de données

1. Vérifier que la DB est attachée :
```bash
flyctl postgres db list --app geneweb-db
```

2. Vérifier la variable DATABASE_URL :
```bash
flyctl ssh console --app geneweb-api -C "echo \$DATABASE_URL"
```

3. Tester la connexion :
```bash
flyctl postgres connect --app geneweb-db
```

### L'application ne répond pas sur 0.0.0.0:8080

**Symptôme** : Warning "The app is not listening on the expected address"

**Causes possibles** :
- Port mal configuré dans le code
- Host configuré sur 127.0.0.1 au lieu de 0.0.0.0

**Solution** : Vérifier `fly_start.py` :
```python
port = 8080  # Port fixe
host = "0.0.0.0"  # Écouter sur toutes les interfaces
uvicorn.run(app, host=host, port=port)
```

### Déploiement lent

Fly.io utilise des layers Docker en cache. Si un layer change :

1. Les fichiers source (`src/`) changent souvent → placés en fin de Dockerfile
2. `requirements.txt` change rarement → en début de Dockerfile
3. Résultat : builds de ~2 secondes quand seul le code change

### Région Frankfurt (cdg) - Problèmes IPv6

**Problème** : Fly.io avait des problèmes d'infrastructure IPv6 à Frankfurt.

**Solution** : Changé pour Amsterdam (ams) :
```bash
flyctl scale count 0
# Modifier fly.toml : primary_region = 'ams'
flyctl volumes create geneweb_data --region ams --size 1
flyctl deploy
```

## 📚 Ressources

- [Documentation Fly.io](https://fly.io/docs/)
- [Fly.io Python Guide](https://fly.io/docs/languages-and-frameworks/python/)
- [Fly.io PostgreSQL](https://fly.io/docs/postgres/)
- [Dashboard Fly.io](https://fly.io/dashboard)
- [Status Fly.io](https://status.flyio.net/)

## 🔄 Workflow de développement

### 1. Développement local

```bash
# Activer l'environnement virtuel
source .venv/bin/activate  # ou votre venv

# Lancer l'API en local
python -m uvicorn geneweb.api.main:app --reload --port 8000
```

### 2. Tests avant déploiement

```bash
# Tests unitaires
pytest

# Vérifier le build Docker
docker build -f Dockerfile.fly -t geneweb-test .
docker run -p 8080:8080 geneweb-test
```

### 3. Déploiement

```bash
# Déployer sur Fly.io
flyctl deploy

# Vérifier le déploiement
flyctl status
curl https://geneweb-api.fly.dev/health/
```

### 4. Rollback en cas de problème

```bash
# Lister les versions
flyctl releases --app geneweb-api

# Revenir à une version précédente
flyctl releases rollback <version> --app geneweb-api
```

## 💰 Coûts

Fly.io offre un tier gratuit généreux :

- **Compute** : 3 machines partagées 256MB RAM
- **Storage** : 3GB de volumes persistants
- **PostgreSQL** : 1 DB avec 256MB RAM, 1GB stockage
- **Bandwidth** : 160GB/mois

Notre configuration actuelle :
- 1 machine shared-cpu-1x (256MB) → Gratuit
- 1 volume 1GB → Gratuit
- 1 PostgreSQL → Gratuit

**Total : 0€/mois dans le tier gratuit**

Pour scaler au-delà :
- Machines supplémentaires : ~$2/mois par machine
- RAM supplémentaire : ~$3/mois par GB
- Stockage : ~$0.15/GB/mois

## 🎓 Notes importantes

1. **Fly.io n'utilise pas GitHub** : Le déploiement se fait depuis votre machine locale via `flyctl deploy`

2. **Les secrets ne sont pas versionnés** : Ils sont stockés dans Fly.io, pas dans le repo Git

3. **Le port doit être 8080** : C'est le standard Fly.io pour les applications web

4. **Health checks obligatoires** : Sans health check fonctionnel, l'app ne recevra pas de trafic

5. **Volumes régionaux** : Un volume est attaché à une région spécifique (ams dans notre cas)

6. **Base de données partagée** : La DB Postgres est sur un réseau privé Fly.io (*.flycast)

## ✅ Checklist de déploiement

- [x] Fly.io CLI installé et configuré
- [x] Application créée (`geneweb-api`)
- [x] Base de données PostgreSQL créée et attachée
- [x] Volume de stockage créé
- [x] Secrets de sécurité configurés
- [x] Dockerfile.fly optimisé
- [x] fly.toml configuré
- [x] Health check fonctionnel
- [x] Tests de déploiement réussis
- [x] API accessible publiquement
- [ ] Frontend configuré pour utiliser l'URL de production
- [ ] Documentation mise à jour
- [ ] Monitoring configuré (optionnel)

---

**Dernière mise à jour** : 23 octobre 2025  
**Version de l'application** : 15  
**Région de déploiement** : Amsterdam (ams)
