# Documentation API Geneweb

## Vue d'ensemble

L'API Geneweb est une interface REST sécurisée construite avec FastAPI pour la gestion de données généalogiques. Elle implémente des mesures de sécurité avancées et suit les meilleures pratiques de l'industrie.

## Table des matières

1. [Architecture](#architecture)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Authentification](#authentification)
5. [Endpoints](#endpoints)
6. [Sécurité](#sécurité)
7. [Monitoring](#monitoring)
8. [Déploiement](#déploiement)
9. [Développement](#développement)
10. [Exemples](#exemples)

> **🆕 Nouveau :** Système d'authentification JWT complet disponible !  
> Voir [AUTHENTICATION_GUIDE.md](../AUTHENTICATION_GUIDE.md) pour la documentation complète.

## Architecture

### Structure du projet

```
src/geneweb/api/
├── __init__.py                 # Module principal
├── main.py                     # Application FastAPI
├── config.py                   # Configuration sécurisée
├── middleware/                 # Middlewares de sécurité
│   ├── __init__.py
│   ├── security.py             # Headers de sécurité, HTTPS
│   └── rate_limiting.py        # Protection DDoS
├── security/                   # Modules de sécurité
│   ├── __init__.py
│   ├── logging.py              # Logging sécurisé
│   ├── secrets.py              # Gestion des secrets
│   └── validation.py           # Validation des entrées
├── monitoring/                 # Monitoring et métriques
│   ├── __init__.py
│   └── metrics.py              # Intégration Prometheus
└── routers/                    # Endpoints API
    ├── __init__.py
    └── health.py               # Health checks
```

### Technologies utilisées

- **FastAPI** : Framework web moderne et performant
- **Uvicorn** : Serveur ASGI pour production
- **Pydantic** : Validation des données et sérialisation
- **Prometheus** : Métriques et monitoring
- **Structlog** : Logging structuré
- **Cryptography** : Chiffrement et sécurité

## Installation

### Prérequis

- Python 3.9+
- pip ou poetry
- Certificats SSL (pour la production)

### Installation locale

```bash
# Cloner le repository
git clone <repository-url>
cd geneweb_python

# Installer les dépendances
pip install -r requirements.txt

# Copier la configuration
cp .env.example .env

# Éditer la configuration
nano .env
```

### Installation avec Docker

```bash
# Construire l'image
docker build -t geneweb-api .

# Ou utiliser docker-compose
docker-compose up -d
```

## Configuration

### Variables d'environnement

#### Configuration de base

```bash
# Application
GENEWEB_API_APP_NAME=Geneweb API
GENEWEB_API_APP_VERSION=0.1.0
GENEWEB_API_DEBUG=false
GENEWEB_API_HOST=0.0.0.0
GENEWEB_API_PORT=8000
GENEWEB_API_WORKERS=4
```

#### Configuration SSL/TLS

```bash
# Certificats SSL (OBLIGATOIRE en production)
GENEWEB_API_SSL_CERTFILE=/path/to/cert.pem
GENEWEB_API_SSL_KEYFILE=/path/to/key.pem
GENEWEB_API_SSL_CA_CERTS=/path/to/ca-certs.pem
```

#### Configuration de sécurité

```bash
# HTTPS et HSTS
GENEWEB_SECURITY_FORCE_HTTPS=true
GENEWEB_SECURITY_HSTS_MAX_AGE=31536000
GENEWEB_SECURITY_HSTS_INCLUDE_SUBDOMAINS=true

# CORS (limiter aux domaines frontend)
GENEWEB_SECURITY_CORS_ORIGINS=["https://app.example.com"]

# Rate limiting
GENEWEB_SECURITY_RATE_LIMIT_PER_MINUTE=100
GENEWEB_SECURITY_RATE_LIMIT_BURST=200

# Secrets (générer des valeurs sécurisées)
GENEWEB_SECURITY_SECRET_KEY=your-secret-key-min-32-chars
GENEWEB_SECURITY_ENCRYPTION_KEY=your-encryption-key-min-32-chars
```

#### Configuration de la base de données

```bash
# Base de données
GENEWEB_DB_DATABASE_URL=postgresql://user:pass@localhost:5432/geneweb
GENEWEB_DB_DATABASE_ECHO=false
```

#### Configuration du logging

```bash
# Logging
GENEWEB_LOG_LOG_LEVEL=INFO
GENEWEB_LOG_LOG_FORMAT=json
GENEWEB_LOG_LOG_FILE=/var/log/geneweb/api.log
```

#### Configuration du monitoring

```bash
# Monitoring
GENEWEB_MONITORING_ENABLE_METRICS=true
GENEWEB_MONITORING_METRICS_PATH=/metrics
GENEWEB_MONITORING_HEALTH_CHECK_PATH=/health
```

## Authentification

### 🔒 Système d'authentification moderne avec JWT

L'API Geneweb utilise un système d'authentification basé sur **JWT (JSON Web Tokens)** avec les fonctionnalités suivantes :

- ✅ **Tokens JWT** avec JTI pour révocation
- ✅ **Refresh tokens** avec rotation automatique
- ✅ **Stockage sécurisé** des mots de passe (bcrypt, cost=12)
- ✅ **Blacklist** pour invalidation des tokens
- ✅ **Historique** des mots de passe (empêche réutilisation)
- ✅ **Sessions utilisateur** traçables
- ✅ **Audit complet** de tous les événements d'authentification
- ✅ **Rate limiting** (100 req/min, burst 20)

> 📖 **Documentation complète** : [AUTHENTICATION_GUIDE.md](../AUTHENTICATION_GUIDE.md)

### Endpoints d'authentification

| Méthode | Endpoint | Description | Auth |
|---------|----------|-------------|------|
| POST | `/auth/register` | Créer un compte utilisateur | Non |
| POST | `/auth/login` | Connexion (JWT) | Non |
| POST | `/auth/login/oauth2` | Connexion OAuth2 | Non |
| POST | `/auth/refresh` | Rafraîchir le token | Refresh Token |
| POST | `/auth/logout` | Déconnexion | Access Token |
| GET | `/auth/me` | Profil utilisateur | Access Token |
| POST | `/auth/change-password` | Changer mot de passe | Access Token |
| GET | `/auth/health` | Santé du système auth | Non |

### Configuration des tokens

```bash
# Dans .env
GENEWEB_JWT_SECRET_KEY="votre-clé-secrète-256-bits"
GENEWEB_JWT_ALGORITHM="HS256"
GENEWEB_JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
GENEWEB_JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
```

### Exemples d'utilisation

#### 1. Créer un compte

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john.doe",
    "email": "john@example.com",
    "password": "SecureP@ss123!",
    "full_name": "John Doe"
  }'
```

**Réponse** (201 Created) :
```json
{
  "user_id": 1,
  "username": "john.doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2025-01-10T10:30:00Z"
}
```

#### 2. Se connecter

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john.doe",
    "password": "SecureP@ss123!"
  }'
```

**Réponse** (200 OK) :
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### 3. Utiliser le token

```bash
# Stocker le token
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Appeler un endpoint protégé
curl -X GET "http://localhost:8000/api/v1/persons" \
  -H "Authorization: Bearer $TOKEN"
```

#### 4. Rafraîchir le token

```bash
curl -X POST "http://localhost:8000/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

**Réponse** (200 OK) :
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### 5. Se déconnecter

```bash
curl -X POST "http://localhost:8000/auth/logout" \
  -H "Authorization: Bearer $TOKEN"
```

**Réponse** (200 OK) :
```json
{
  "message": "Successfully logged out"
}
```

### Structure du JWT

**Access Token** (validité: 30 minutes) :
```json
{
  "sub": "john.doe",
  "user_id": 1,
  "email": "john@example.com",
  "jti": "550e8400-e29b-41d4-a716-446655440000",
  "type": "access",
  "exp": 1705750200,
  "iat": 1705748400
}
```

**Refresh Token** (validité: 7 jours) :
```json
{
  "sub": "john.doe",
  "user_id": 1,
  "jti": "6fa459ea-ee8a-3ca4-894e-db77e160355e",
  "type": "refresh",
  "exp": 1706353200,
  "iat": 1705748400
}
```

### Gestion des erreurs

| Code | Erreur | Description |
|------|--------|-------------|
| 400 | `invalid_credentials` | Username/password incorrect |
| 401 | `invalid_token` | Token expiré ou invalide |
| 401 | `token_blacklisted` | Token révoqué |
| 403 | `insufficient_permissions` | Permissions insuffisantes |
| 422 | `validation_error` | Données invalides |
| 429 | `rate_limit_exceeded` | Trop de requêtes |

**Exemple d'erreur** :
```json
{
  "detail": "Invalid credentials"
}
```

### Sécurité

#### Stockage des mots de passe
- **Algorithme** : bcrypt
- **Cost factor** : 12 (2^12 itérations)
- **Salt** : Automatique et unique par mot de passe

#### Protection contre les attaques
- **Brute force** : Rate limiting (100 req/min)
- **Rejeu** : JTI unique par token
- **Session hijacking** : Token blacklist
- **Rainbow tables** : Salt automatique

#### Bonnes pratiques
1. **Toujours HTTPS** en production
2. **Ne jamais loguer** les tokens
3. **Stocker les tokens** en mémoire (pas localStorage)
4. **Rotation automatique** des refresh tokens
5. **Expiration courte** des access tokens (30 min)

## Endpoints

### Vue d'ensemble des endpoints

L'API Geneweb expose plusieurs groupes d'endpoints :

- **Health** (`/health`) : Vérifications de santé et monitoring
- **Persons** (`/api/v1/persons`) : Gestion des personnes
- **Families** (`/api/v1/families`) : Gestion des familles
- **GDPR** (`/api/v1/persons/{id}/gdpr-*`) : Conformité RGPD
- **Database** (`/api/v1/database`) : Gestion de la base de données active
- **Multi-Database** (`/api/v1/database/databases`) : Gestion multi-bases de données
- **Search & Genealogy** (`/api/v1/search`, `/api/v1/genealogy`) : Recherche avec protection vie privée

### Tableau récapitulatif

| Méthode | Endpoint | Description | Auth | Admin |
|---------|----------|-------------|------|-------|
| **Authentification** |
| POST | `/auth/register` | Créer un compte utilisateur | Non | Non |
| POST | `/auth/login` | Connexion (retourne JWT) | Non | Non |
| POST | `/auth/login/oauth2` | Connexion OAuth2 compatible | Non | Non |
| POST | `/auth/refresh` | Rafraîchir l'access token | Refresh | Non |
| POST | `/auth/logout` | Déconnexion (blacklist token) | Oui | Non |
| GET | `/auth/me` | Profil utilisateur connecté | Oui | Non |
| POST | `/auth/change-password` | Changer le mot de passe | Oui | Non |
| GET | `/auth/health` | Santé du système d'auth | Non | Non |
| **Health Checks** |
| GET | `/health` | Health check basique | Non | Non |
| GET | `/health/live` | Liveness probe | Non | Non |
| GET | `/health/ready` | Readiness probe | Non | Non |
| GET | `/health/detailed` | Health check détaillé | Non | Non |
| GET | `/metrics` | Métriques Prometheus | Non | Non |
| **Personnes** |
| POST | `/api/v1/persons` | Créer une personne | Oui | Non |
| GET | `/api/v1/persons/{id}` | Récupérer une personne | Oui | Non |
| GET | `/api/v1/persons` | Lister les personnes | Oui | Non |
| PUT | `/api/v1/persons/{id}` | Mettre à jour une personne | Oui | Non |
| DELETE | `/api/v1/persons/{id}` | Supprimer une personne | Oui | Oui |
| **Familles** |
| POST | `/api/v1/families` | Créer une famille | Oui | Non |
| GET | `/api/v1/families/{id}` | Récupérer une famille | Oui | Non |
| GET | `/api/v1/families` | Lister les familles | Oui | Non |
| PATCH | `/api/v1/families/{id}` | Mettre à jour une famille | Oui | Non |
| DELETE | `/api/v1/families/{id}` | Supprimer une famille | Oui | Oui |
| **RGPD** |
| GET | `/api/v1/persons/{id}/gdpr-export` | Exporter les données (droit d'accès) | Oui | Non |
| POST | `/api/v1/persons/{id}/anonymize` | Anonymiser (droit à l'oubli) | Oui | Oui |
| POST | `/api/v1/persons/{id}/consent` | Gérer le consentement | Oui | Non |
| GET | `/api/v1/persons/{id}/data-processing-info` | Info traitement données | Oui | Non |
| **Recherche & Généalogie (Protection Vie Privée)** |
| GET | `/api/v1/search/persons` | Recherche avec anonymisation auto | Non* | Non |
| GET | `/api/v1/genealogy/ancestors/{id}` | Arbre ancêtres protégé | Non* | Non |
| GET | `/api/v1/genealogy/descendants/{id}` | Arbre descendants (vivants filtrés) | Non* | Non |
| GET | `/api/v1/genealogy/sosa/{number}` | Recherche par numéro Sosa | Non* | Non |
| GET | `/api/v1/genealogy/tree/{id}` | Arbre généalogique complet | Non* | Non |
| GET | `/api/v1/search/privacy-info` | Règles de confidentialité | Non | Non |
| **Base de données** |
| GET | `/api/v1/database/stats` | Statistiques de la DB active | Non* | Non |
| GET | `/api/v1/database/health` | Santé de la DB active | Non* | Non |
| POST | `/api/v1/database/reload` | Recharger la DB active | Oui | Oui |
| POST | `/api/v1/database/commit` | Commiter les changements | Oui | Oui |
| GET | `/api/v1/database/info` | Informations de la DB active | Non* | Non |
| **Gestion Multi-Bases** |
| GET | `/api/v1/database/databases` | Lister toutes les DB | Non* | Non |
| GET | `/api/v1/database/databases/active` | Obtenir la DB active | Non* | Non |
| POST | `/api/v1/database/databases` | Créer une nouvelle DB | Oui | Oui |
| POST | `/api/v1/database/databases/{name}/activate` | Activer une DB | Oui | Oui |
| PUT | `/api/v1/database/databases/{name}/rename` | Renommer une DB | Oui | Oui |
| DELETE | `/api/v1/database/databases/{name}` | Supprimer une DB | Oui | Oui |

*Non* : Authentification optionnelle (détails complets si authentifié)

---

### 1. Health Checks

#### `GET /health`

Vérification de santé basique (publique).

**Réponse :**
```json
{
  "status": "healthy",
  "timestamp": 1640995200.0,
  "version": "0.1.0",
  "environment": "production",
  "uptime": 3600.5,
  "checks": {
    "api": "healthy",
    "configuration": "healthy"
  }
}
```

#### `GET /health/live`

Probe de vivacité pour Kubernetes.

**Réponse :**
```json
{
  "status": "live",
  "timestamp": 1640995200.0
}
```

#### `GET /health/ready`

Probe de disponibilité pour Kubernetes.

**Réponse :**
```json
{
  "status": "ready",
  "timestamp": 1640995200.0,
  "checks": {
    "configuration": "ready",
    "database": "ready"
  }
}
```

#### `GET /health/detailed`

Vérification détaillée (réseaux internes uniquement).

**Réponse :**
```json
{
  "status": "healthy",
  "timestamp": 1640995200.0,
  "version": "0.1.0",
  "environment": "production",
  "uptime": 3600.5,
  "checks": {
    "api": "healthy",
    "configuration": "healthy"
  },
  "metrics": {
    "total_requests": 12345,
    "active_connections": 5,
    "rate_limit_hits": 23,
    "security_events": 1
  },
  "system": {
    "python_version": "3.11.5",
    "platform": "linux"
  }
}
```

---

### 2. Gestion des Personnes

#### `POST /api/v1/persons`

Créer une nouvelle personne.

**Authentification :** Requise

**Corps de la requête :**
```json
{
  "first_name": "Jean",
  "surname": "Dupont",
  "sex": "male",
  "birth_date": "1990-05-15",
  "birth_place": "Paris, France",
  "occupation": "Ingénieur",
  "public_name": "Jean D.",
  "qualifiers": ["Junior"],
  "aliases": ["JD"],
  "first_names_aliases": ["John"],
  "surname_aliases": ["Durant"],
  "titles": ["M."],
  "notes": "Notes personnelles",
  "psources": "Registre d'état civil"
}
```

**Réponse :** `201 Created`
```json
{
  "person_id": "550e8400-e29b-41d4-a716-446655440000",
  "first_name": "Jean",
  "surname": "Dupont",
  "sex": "male",
  "birth_date": "1990-05-15",
  "created_at": "2025-10-19T10:30:00Z",
  "updated_at": "2025-10-19T10:30:00Z"
}
```

**Codes d'erreur :**
- `400` : Données invalides
- `401` : Non authentifié
- `422` : Erreur de validation

#### `GET /api/v1/persons/{person_id}`

Récupérer les informations d'une personne.

**Authentification :** Requise

**Paramètres :**
- `person_id` (UUID) : Identifiant unique de la personne

**Réponse :** `200 OK`
```json
{
  "person_id": "550e8400-e29b-41d4-a716-446655440000",
  "first_name": "Jean",
  "surname": "Dupont",
  "sex": "male",
  "birth_date": "1990-05-15",
  "birth_place": "Paris, France",
  "created_at": "2025-10-19T10:30:00Z",
  "updated_at": "2025-10-19T10:30:00Z"
}
```

**Codes d'erreur :**
- `401` : Non authentifié
- `404` : Personne non trouvée

#### `GET /api/v1/persons`

Lister toutes les personnes avec pagination.

**Authentification :** Requise

**Paramètres de requête :**
- `skip` (int, optionnel) : Nombre d'éléments à ignorer (défaut: 0)
- `limit` (int, optionnel) : Nombre maximum d'éléments (défaut: 100, max: 1000)

**Réponse :** `200 OK`
```json
{
  "persons": [
    {
      "person_id": "550e8400-e29b-41d4-a716-446655440000",
      "first_name": "Jean",
      "surname": "Dupont",
      "sex": "male",
      "birth_date": "1990-05-15"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100
}
```

**Codes d'erreur :**
- `401` : Non authentifié
- `422` : Paramètres invalides

#### `PUT /api/v1/persons/{person_id}`

Mettre à jour une personne.

**Authentification :** Requise

**Paramètres :**
- `person_id` (UUID) : Identifiant unique de la personne

**Corps de la requête :**
```json
{
  "first_name": "Jean",
  "surname": "Dupont-Martin",
  "occupation": "Architecte",
  "notes": "Notes mises à jour"
}
```

**Réponse :** `200 OK`
```json
{
  "person_id": "550e8400-e29b-41d4-a716-446655440000",
  "first_name": "Jean",
  "surname": "Dupont-Martin",
  "sex": "male",
  "updated_at": "2025-10-19T11:00:00Z"
}
```

**Codes d'erreur :**
- `400` : Données invalides
- `401` : Non authentifié
- `404` : Personne non trouvée
- `422` : Erreur de validation

#### `DELETE /api/v1/persons/{person_id}`

Supprimer une personne.

**Authentification :** Requise (Admin)

**Paramètres :**
- `person_id` (UUID) : Identifiant unique de la personne

**Réponse :** `204 No Content`

**Codes d'erreur :**
- `401` : Non authentifié
- `403` : Non autorisé (Admin requis)
- `404` : Personne non trouvée

---

### 3. RGPD (GDPR)

#### `GET /api/v1/persons/{person_id}/gdpr-export`

Exporter toutes les données d'une personne (conformité RGPD).

**Authentification :** Requise

**Paramètres :**
- `person_id` (UUID) : Identifiant unique de la personne

**Réponse :** `200 OK`
```json
{
  "person_id": "550e8400-e29b-41d4-a716-446655440000",
  "export_timestamp": "2025-10-19T12:00:00Z",
  "personal_data": {
    "first_name": "Jean",
    "surname": "Dupont",
    "sex": "male",
    "birth_date": "1990-05-15",
    "birth_place": "Paris, France"
  },
  "metadata": {
    "created_at": "2025-10-19T10:30:00Z",
    "updated_at": "2025-10-19T11:00:00Z",
    "data_processing_consent": true,
    "consent_date": "2025-10-19T10:30:00Z"
  },
  "processing_purposes": [
    "Recherche généalogique",
    "Conservation historique"
  ]
}
```

**Codes d'erreur :**
- `401` : Non authentifié
- `404` : Personne non trouvée

#### `POST /api/v1/persons/{person_id}/anonymize`

Anonymiser les données d'une personne.

**Authentification :** Requise (Admin)

**Paramètres :**
- `person_id` (UUID) : Identifiant unique de la personne

**Corps de la requête :**
```json
{
  "reason": "Demande de l'utilisateur (droit à l'oubli)",
  "keep_statistical_data": false
}
```

**Réponse :** `200 OK`
```json
{
  "success": true,
  "message": "Personne anonymisée avec succès",
  "person_id": "550e8400-e29b-41d4-a716-446655440000",
  "anonymized_at": "2025-10-19T12:30:00Z"
}
```

**Codes d'erreur :**
- `401` : Non authentifié
- `403` : Non autorisé (Admin requis)
- `404` : Personne non trouvée

#### `POST /api/v1/persons/{person_id}/consent`

Gérer le consentement de traitement des données.

**Authentification :** Requise

**Paramètres :**
- `person_id` (UUID) : Identifiant unique de la personne

**Corps de la requête :**
```json
{
  "consent_given": true,
  "processing_purposes": [
    "Recherche généalogique",
    "Conservation historique",
    "Partage avec d'autres chercheurs"
  ],
  "consent_version": "1.0"
}
```

**Réponse :** `200 OK`
```json
{
  "success": true,
  "message": "Consentement enregistré",
  "person_id": "550e8400-e29b-41d4-a716-446655440000",
  "consent_date": "2025-10-19T13:00:00Z"
}
```

**Codes d'erreur :**
- `401` : Non authentifié
- `404` : Personne non trouvée
- `422` : Erreur de validation

#### `GET /api/v1/persons/{person_id}/data-processing-info`

Obtenir les informations sur le traitement des données.

**Authentification :** Requise

**Paramètres :**
- `person_id` (UUID) : Identifiant unique de la personne

**Réponse :** `200 OK`
```json
{
  "person_id": "550e8400-e29b-41d4-a716-446655440000",
  "data_controller": "Geneweb Organization",
  "processing_purposes": [
    "Recherche généalogique",
    "Conservation historique"
  ],
  "legal_basis": "Consentement",
  "retention_period": "Illimitée (tant que consentement actif)",
  "data_recipients": [
    "Chercheurs autorisés",
    "Membres de la famille"
  ],
  "user_rights": [
    "Droit d'accès",
    "Droit de rectification",
    "Droit à l'effacement",
    "Droit à la portabilité",
    "Droit d'opposition"
  ],
  "contact": "dpo@geneweb.org"
}
```

**Codes d'erreur :**
- `401` : Non authentifié
- `404` : Personne non trouvée

---

### 4. Gestion de la Base de Données

#### `GET /api/v1/database/stats`

Obtenir les statistiques de la base de données.

**Authentification :** Optionnelle (détails complets si authentifié)

**Réponse :** `200 OK`
```json
{
  "person_count": 1523,
  "family_count": 892,
  "pending_patches": 5,
  "read_only": false,
  "last_update": "2025-10-19T14:00:00Z"
}
```

**Codes d'erreur :**
- `500` : Erreur serveur

#### `GET /api/v1/database/health`

Vérifier la santé de la base de données.

**Authentification :** Optionnelle

**Réponse :** `200 OK`
```json
{
  "status": "healthy",
  "message": "Base de données opérationnelle",
  "stats": {
    "person_count": 1523,
    "family_count": 892,
    "pending_patches": 5,
    "read_only": false
  },
  "timestamp": "2025-10-19T14:05:00Z"
}
```

**États possibles :**
- `healthy` : Base de données opérationnelle
- `read_only` : Base de données en lecture seule
- `unhealthy` : Base de données non disponible

**Codes d'erreur :**
- `503` : Base de données non disponible

#### `POST /api/v1/database/reload`

Recharger la base de données depuis le disque.

**Authentification :** Requise (Admin)

**Réponse :** `200 OK`
```json
{
  "success": true,
  "message": "Base de données rechargée avec succès",
  "stats": {
    "person_count": 1524,
    "family_count": 893,
    "pending_patches": 0,
    "read_only": false
  },
  "reloaded_at": "2025-10-19T14:10:00Z"
}
```

**Codes d'erreur :**
- `401` : Non authentifié
- `403` : Non autorisé (Admin requis)
- `500` : Erreur lors du rechargement

#### `POST /api/v1/database/commit`

Commit des changements en attente vers le disque.

**Authentification :** Requise (Admin)

**Réponse :** `200 OK`
```json
{
  "success": true,
  "message": "5 patches committés avec succès",
  "patches_committed": 5,
  "committed_at": "2025-10-19T14:15:00Z"
}
```

**Codes d'erreur :**
- `401` : Non authentifié
- `403` : Non autorisé (Admin requis)
- `409` : Base de données en lecture seule
- `500` : Erreur lors du commit

#### `GET /api/v1/database/info`

Obtenir les informations de base sur la base de données.

**Authentification :** Optionnelle

**Réponse :** `200 OK`
```json
{
  "database_path": "/path/to/database.gwb",
  "read_only": false,
  "initialized": true,
  "version": "1.0",
  "created_at": "2025-01-01T00:00:00Z"
}
```

**Codes d'erreur :**
- `500` : Erreur serveur

---

### 5. Gestion Multi-Bases de Données

> **Nouveauté** : L'API supporte maintenant la gestion de plusieurs bases de données simultanément.

#### `GET /api/v1/database/databases`

Lister toutes les bases de données chargées en mémoire.

**Authentification :** Optionnelle

**Réponse :** `200 OK`
```json
{
  "databases": [
    {
      "name": "family_tree",
      "path": "/data/family_tree.gwb",
      "active": true,
      "person_count": 1523,
      "family_count": 892,
      "read_only": false,
      "pending_patches": 5
    },
    {
      "name": "research",
      "path": "/data/research.gwb",
      "active": false,
      "person_count": 245,
      "family_count": 120,
      "read_only": false,
      "pending_patches": 0
    }
  ],
  "active_database": "family_tree"
}
```

**Codes d'erreur :**
- `500` : Erreur serveur

#### `GET /api/v1/database/databases/active`

Obtenir les informations de la base de données actuellement active.

**Authentification :** Optionnelle

**Réponse :** `200 OK`
```json
{
  "name": "family_tree",
  "path": "/data/family_tree.gwb",
  "active": true,
  "person_count": 1523,
  "family_count": 892,
  "read_only": false,
  "pending_patches": 5
}
```

**Codes d'erreur :**
- `404` : Aucune base de données active
- `500` : Erreur serveur

#### `POST /api/v1/database/databases`

Créer une nouvelle base de données.

**Authentification :** Requise (Admin)

**Corps de la requête :**
```json
{
  "name": "nouvelle_famille",
  "set_active": false
}
```

**Paramètres :**
- `name` (obligatoire) : Nom de la nouvelle base de données (sans .gwb)
- `set_active` (optionnel, défaut: false) : Activer cette DB après création

**Réponse :** `201 Created`
```json
{
  "success": true,
  "message": "Database 'nouvelle_famille' created successfully",
  "database": {
    "name": "nouvelle_famille",
    "path": "/data/nouvelle_famille.gwb",
    "active": false,
    "person_count": 0,
    "family_count": 0,
    "read_only": false,
    "pending_patches": 0
  }
}
```

**Codes d'erreur :**
- `400` : Nom de base invalide ou DB existante
- `401` : Non authentifié
- `403` : Non autorisé (Admin requis)
- `500` : Erreur lors de la création

#### `POST /api/v1/database/databases/{name}/activate`

Activer une base de données existante (la définir comme DB active).

**Authentification :** Requise (Admin)

**Paramètres de chemin :**
- `name` : Nom de la base de données à activer

**Réponse :** `200 OK`
```json
{
  "success": true,
  "message": "Database 'research' is now active",
  "active_database": "research"
}
```

**Codes d'erreur :**
- `401` : Non authentifié
- `403` : Non autorisé (Admin requis)
- `404` : Base de données non trouvée
- `500` : Erreur lors de l'activation

#### `PATCH /api/v1/database/databases/{name}/rename`

Renommer une base de données existante.

**Authentification :** Requise (Admin)

**Paramètres de chemin :**
- `name` : Nom actuel de la base de données à renommer

**Corps de la requête :**
```json
{
  "new_name": "nouveau_nom",
  "rename_files": false
}
```

**Paramètres :**
- `new_name` (obligatoire) : Nouveau nom pour la base de données (sans .gwb)
- `rename_files` (optionnel, défaut: false) : Renommer aussi les fichiers sur le disque

**Exemple de requête :**
```bash
PATCH /api/v1/database/databases/old_name/rename
Content-Type: application/json

{
  "new_name": "family_archive_2024",
  "rename_files": true
}
```

**Réponse :** `200 OK`
```json
{
  "success": true,
  "message": "Database renamed from 'old_name' to 'family_archive_2024' successfully",
  "old_name": "old_name",
  "new_name": "family_archive_2024",
  "files_renamed": true,
  "database": {
    "name": "family_archive_2024",
    "path": "/data/family_archive_2024.gwb",
    "active": false,
    "person_count": 1523,
    "family_count": 892,
    "read_only": false,
    "pending_patches": 0
  }
}
```

**Codes d'erreur :**
- `400` : Nom invalide, nouveau nom existe déjà, ou nom vide
- `401` : Non authentifié
- `403` : Non autorisé (Admin requis)
- `404` : Base de données source non trouvée
- `500` : Erreur lors du renommage (ex: problème de fichiers)

**📋 Notes importantes :**
- Si la base renommée est la base active, elle reste active avec le nouveau nom
- `rename_files=false` : Renomme uniquement en mémoire (les fichiers restent inchangés)
- `rename_files=true` : Renomme également les fichiers/répertoires sur le disque
- Les changements non commités sont automatiquement sauvegardés avant le renommage
- Aucun autre processus ne doit accéder aux fichiers pendant le renommage

**💡 Cas d'usage :**
- Organisation et archivage de bases de données
- Changement de convention de nommage
- Préparation pour export/backup
- Migration de nomenclature

#### `DELETE /api/v1/database/databases/{name}`

Supprimer une base de données de la mémoire et optionnellement du disque.

**Authentification :** Requise (Admin)

**Paramètres de chemin :**
- `name` : Nom de la base de données à supprimer

**Paramètres de requête :**
- `delete_files` (optionnel, défaut: false) : Supprimer aussi les fichiers du disque

**Exemple :**
```
DELETE /api/v1/database/databases/old_db?delete_files=true
```

**Réponse :** `200 OK`
```json
{
  "success": true,
  "message": "Database 'old_db' deleted successfully",
  "deleted_files": true
}
```

**Codes d'erreur :**
- `400` : Impossible de supprimer la DB active (changer d'abord de DB)
- `401` : Non authentifié
- `403` : Non autorisé (Admin requis)
- `404` : Base de données non trouvée
- `500` : Erreur lors de la suppression

**⚠️ Important :**
- Une base de données active ne peut pas être supprimée
- Activez une autre base avant de supprimer la base active
- `delete_files=true` supprime définitivement les données du disque

---

### 6. Recherche et Généalogie avec Protection Vie Privée

> **Nouveauté** : Ces endpoints implémentent une protection automatique de la vie privée conforme au RGPD.

#### Niveaux de Confidentialité

| Niveau | Application | Données Visibles |
|--------|-------------|------------------|
| **PUBLIC** | Personnes décédées | Toutes informations complètes |
| **RESTRICTED** | Famille autorisée | Nom + année naissance uniquement |
| **ANONYMIZED** | Non autorisé | "[Personne vivante]" / "[Confidentiel]" |

**Critère "Vivant"** : Pas de date de décès ET (âge < 100 ans OU date naissance inconnue)

#### `GET /api/v1/search/persons`

Recherche de personnes avec anonymisation automatique.

**Authentification :** Optionnelle (plus de détails si authentifié)

**Paramètres de requête :**
- `query` (requis) : Texte de recherche (nom, prénom)
- `first_name` (optionnel) : Filtrer par prénom
- `surname` (optionnel) : Filtrer par nom de famille
- `birth_year_from` (optionnel) : Année de naissance minimale (1000-2100)
- `birth_year_to` (optionnel) : Année de naissance maximale (1000-2100)
- `birth_place` (optionnel) : Lieu de naissance
- `sex` (optionnel) : male|female|unknown
- `include_living` (optionnel, défaut: false) : Inclure personnes vivantes
- `limit` (optionnel, défaut: 20, max: 100) : Nombre de résultats
- `offset` (optionnel, défaut: 0) : Pagination
- `user_id` (optionnel) : ID utilisateur pour autorisation

**Exemple :**
```bash
GET /api/v1/search/persons?query=Dupont&birth_year_from=1900&birth_year_to=1950&limit=10
```

**Réponse :** `200 OK`
```json
{
  "results": [
    {
      "person_id": "P001",
      "first_name": "Jean",
      "surname": "Dupont",
      "sex": "male",
      "birth_date": "1920-05-15",
      "birth_place": "Paris, France",
      "death_date": "1995-12-20",
      "death_place": "Lyon, France",
      "is_living": false,
      "privacy_level": "public",
      "anonymized": false,
      "occupation": "Médecin"
    },
    {
      "person_id": "P002",
      "first_name": "Marie",
      "surname": "Dupont",
      "sex": "female",
      "birth_date": "1990",
      "birth_place": null,
      "death_date": null,
      "death_place": null,
      "is_living": true,
      "privacy_level": "restricted",
      "anonymized": true
    }
  ],
  "total": 2,
  "offset": 0,
  "limit": 10,
  "query": "Dupont",
  "anonymized_count": 1
}
```

**Protection :**
- Personnes décédées : Informations complètes (PUBLIC)
- Personnes vivantes : Anonymisées ou limitées selon autorisation
- Par défaut (`include_living=false`) : Seules personnes décédées retournées

**Codes d'erreur :**
- `400` : Paramètres de requête invalides
- `500` : Erreur de recherche

#### `GET /api/v1/genealogy/ancestors/{person_id}`

Récupère l'arbre des ancêtres avec protection vie privée.

**Authentification :** Optionnelle

**Paramètres de chemin :**
- `person_id` : ID de la personne racine

**Paramètres de requête :**
- `max_generations` (optionnel, défaut: 5, max: 10) : Nombre de générations
- `user_id` (optionnel) : ID utilisateur pour autorisation

**Exemple :**
```bash
GET /api/v1/genealogy/ancestors/P001?max_generations=3
```

**Réponse :** `200 OK`
```json
{
  "root_person_id": "P001",
  "tree_type": "ancestors",
  "nodes": [
    {
      "person_id": "P001",
      "first_name": "Jean",
      "surname": "Dupont",
      "generation": 0,
      "sosa_number": 1,
      "birth_date": "1950-03-15",
      "death_date": null,
      "is_living": true,
      "privacy_level": "restricted",
      "father_id": "P002",
      "mother_id": "P003"
    },
    {
      "person_id": "P002",
      "first_name": "Pierre",
      "surname": "Dupont",
      "generation": 1,
      "sosa_number": 2,
      "birth_date": "1920-07-10",
      "death_date": "2005-11-20",
      "is_living": false,
      "privacy_level": "public",
      "father_id": "P004",
      "mother_id": "P005"
    }
  ],
  "total_nodes": 7,
  "max_generation": 2,
  "anonymized_count": 1
}
```

**Protection :**
- Ancêtres vivants : Filtrés ou anonymisés
- Informations sensibles masquées selon niveau d'autorisation

**Codes d'erreur :**
- `404` : Personne non trouvée
- `500` : Erreur de récupération

#### `GET /api/v1/genealogy/descendants/{person_id}`

Récupère l'arbre des descendants avec protection des personnes vivantes.

**Authentification :** Optionnelle

**Paramètres :** Identiques à `/ancestors/{person_id}`

**Exemple :**
```bash
GET /api/v1/genealogy/descendants/P001?max_generations=2
```

**Réponse :** `200 OK`
```json
{
  "root_person_id": "P001",
  "tree_type": "descendants",
  "nodes": [
    {
      "person_id": "P001",
      "first_name": "Jean",
      "surname": "Dupont",
      "generation": 0,
      "birth_date": "1920-05-15",
      "is_living": false,
      "privacy_level": "public",
      "children_ids": ["P010", "P011"]
    },
    {
      "person_id": "P010",
      "first_name": "Marie",
      "surname": "Dupont",
      "generation": 1,
      "birth_date": "1950",
      "is_living": true,
      "privacy_level": "restricted",
      "children_ids": ["P020"]
    }
  ],
  "total_nodes": 5,
  "max_generation": 2,
  "anonymized_count": 2
}
```

**Protection :**
- Descendants vivants automatiquement filtrés ou anonymisés
- Seules personnes décédées ou autorisées affichées

#### `GET /api/v1/genealogy/sosa/{sosa_number}`

Recherche une personne par numéro Sosa.

**Numérotation Sosa :**
- 1 = Personne de référence (de cujus)
- 2 = Père, 3 = Mère
- 4 = Grand-père paternel, 5 = Grand-mère paternelle
- 6 = Grand-père maternel, 7 = Grand-mère maternelle
- Formule : 2n = père, 2n+1 = mère

**Authentification :** Optionnelle

**Paramètres de chemin :**
- `sosa_number` : Numéro Sosa (≥1)

**Paramètres de requête :**
- `root_person_id` (requis) : ID de la personne racine (Sosa 1)
- `user_id` (optionnel) : ID utilisateur

**Exemple :**
```bash
GET /api/v1/genealogy/sosa/2?root_person_id=P001
```

**Réponse :** `200 OK`
```json
{
  "sosa_number": 2,
  "person_id": "P002",
  "first_name": "Pierre",
  "surname": "Dupont",
  "generation": 1,
  "birth_date": "1920-07-10",
  "death_date": "2005-11-20",
  "is_living": false,
  "privacy_level": "public",
  "relationship": "father"
}
```

**Codes d'erreur :**
- `404` : Personne avec ce numéro Sosa non trouvée
- `500` : Erreur de recherche

#### `GET /api/v1/genealogy/tree/{person_id}`

Arbre généalogique personnalisé (ascendants, descendants ou complet).

**Authentification :** Optionnelle

**Paramètres de chemin :**
- `person_id` : ID de la personne racine

**Paramètres de requête :**
- `tree_type` (optionnel, défaut: full) : ancestors|descendants|full
- `max_generations` (optionnel, défaut: 5, max: 10) : Nombre de générations
- `user_id` (optionnel) : ID utilisateur

**Exemple :**
```bash
GET /api/v1/genealogy/tree/P001?tree_type=full&max_generations=3
```

**Réponse :** `200 OK`
```json
{
  "root_person_id": "P001",
  "tree_type": "full",
  "nodes": [
    // Ancêtres et descendants combinés
  ],
  "total_nodes": 15,
  "max_generation": 3,
  "anonymized_count": 3
}
```

**Types d'arbres :**
- `ancestors` : Arbre ascendant uniquement
- `descendants` : Arbre descendant uniquement
- `full` : Ascendants + Descendants combinés

#### `GET /api/v1/search/privacy-info`

Informations sur les règles de protection de la vie privée.

**Authentification :** Non

**Réponse :** `200 OK`
```json
{
  "privacy_levels": {
    "public": {
      "description": "Personnes décédées - Informations complètes",
      "data_visible": [
        "Nom complet",
        "Dates complètes",
        "Lieux",
        "Occupation",
        "Notes"
      ]
    },
    "restricted": {
      "description": "Membres famille - Informations limitées",
      "data_visible": [
        "Nom complet",
        "Année de naissance",
        "Sexe"
      ]
    },
    "anonymized": {
      "description": "Personnes vivantes - Anonymisé",
      "data_visible": [
        "Aucune donnée personnelle"
      ]
    }
  },
  "living_criteria": "Pas de date de décès ET (âge < 100 ans OU date inconnue)",
  "default_access": "PUBLIC pour décédés, ANONYMIZED pour vivants"
}
```

---

### 7. Gestion des Familles

> **Nouveauté** : Ces endpoints permettent de gérer les familles (couples et leurs enfants) avec événements, témoins, et sources.

#### Modèles de données

##### RelationKind (Type de relation)
- `married` : Mariés
- `not_married` : Non mariés
- `engaged` : Fiancés
- `no_sexes_check_not_married` : Non mariés (sans vérification sexe)
- `no_sexes_check_married` : Mariés (sans vérification sexe)
- `marriage_bann` : Bans de mariage
- `marriage_contract` : Contrat de mariage
- `marriage_license` : Licence de mariage
- `pacs` : PACS
- `residence` : Résidence commune
- `no_mention` : Sans mention

##### DivorceStatus (Statut de divorce)
- `not_divorced` : Non divorcés
- `divorced` : Divorcés
- `separated` : Séparés

##### FamilyEventName (Types d'événements)
- `marriage` : Mariage
- `no_marriage` : Pas de mariage
- `engagement` : Fiançailles
- `divorce` : Divorce
- `separated` : Séparation
- `family_note` : Note familiale
- `generic_family_event` : Événement générique
- `religious_marriage` : Mariage religieux
- `cremation` : Crémation
- `civil_union` : Union civile

##### WitnessKind (Type de témoin)
- `witness` : Témoin général
- `witness_godparent` : Parrain/Marraine
- `witness_officer` : Officiant

#### `POST /api/v1/families`

Créer une nouvelle famille.

**Authentification :** Requise

**Corps de la requête :**
```json
{
  "father_ids": ["1", "2"],
  "mother_ids": ["3"],
  "children_ids": ["4", "5"],
  "relation": "married",
  "marriage_date": "2020-06-15",
  "marriage_place": "Paris, France",
  "marriage_source": "Registre d'état civil",
  "divorce_info": {
    "divorce_status": "not_divorced",
    "divorce_date": null
  },
  "comment": "Notes sur la famille",
  "events": [
    {
      "event_name": "marriage",
      "custom_name": null,
      "date": "2020-06-15",
      "place": "Paris, France",
      "note": "Belle cérémonie",
      "source": "Photos de famille",
      "reason": "",
      "witnesses": [
        {
          "person_id": "6",
          "witness_kind": "witness"
        }
      ]
    }
  ]
}
```

**Réponse :** `201 Created`
```json
{
  "success": true,
  "message": "Family created successfully with ID: 550e8400-e29b-41d4-a716-446655440000",
  "family": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "father_ids": ["1", "2"],
    "mother_ids": ["3"],
    "children_ids": ["4", "5"],
    "relation": "married",
    "marriage_date": "2020-06-15",
    "marriage_place": "Paris, France",
    "marriage_source": "Registre d'état civil",
    "divorce_info": null,
    "comment": "Notes sur la famille",
    "events": [...],
    "created_at": "2025-10-23T10:30:00Z",
    "updated_at": "2025-10-23T10:30:00Z"
  }
}
```

**Codes d'erreur :**
- `400` : Données invalides (au moins un parent requis)
- `401` : Non authentifié
- `422` : Erreur de validation

#### `GET /api/v1/families/{family_id}`

Récupérer les informations d'une famille.

**Authentification :** Requise

**Paramètres :**
- `family_id` (UUID) : Identifiant unique de la famille

**Réponse :** `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "father_ids": ["1", "2"],
  "mother_ids": ["3"],
  "children_ids": ["4", "5"],
  "relation": "married",
  "marriage_date": "2020-06-15",
  "marriage_place": "Paris, France",
  "marriage_source": "Registre d'état civil",
  "divorce_info": null,
  "comment": "Notes sur la famille",
  "events": [
    {
      "event_name": "marriage",
      "custom_name": null,
      "date": "2020-06-15",
      "place": "Paris, France",
      "note": "Belle cérémonie",
      "source": "Photos de famille",
      "reason": "",
      "witnesses": [
        {
          "person_id": "6",
          "witness_kind": "witness"
        }
      ]
    }
  ],
  "created_at": "2025-10-23T10:30:00Z",
  "updated_at": "2025-10-23T10:30:00Z"
}
```

**Codes d'erreur :**
- `401` : Non authentifié
- `404` : Famille non trouvée

#### `GET /api/v1/families`

Lister toutes les familles avec pagination.

**Authentification :** Requise

**Paramètres de requête :**
- `offset` (optionnel, défaut: 0) : Nombre de résultats à sauter
- `limit` (optionnel, défaut: 50, max: 100) : Nombre de résultats par page

**Exemple :**
```bash
GET /api/v1/families?offset=0&limit=20
```

**Réponse :** `200 OK`
```json
{
  "families": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "father_ids": ["1"],
      "mother_ids": ["2"],
      "children_ids": ["3", "4"],
      "relation": "married",
      "marriage_date": "2020-06-15",
      "created_at": "2025-10-23T10:30:00Z"
    }
  ],
  "total": 150,
  "offset": 0,
  "limit": 20
}
```

**Codes d'erreur :**
- `401` : Non authentifié
- `422` : Paramètres invalides

#### `PATCH /api/v1/families/{family_id}`

Mettre à jour une famille (mise à jour partielle).

**Authentification :** Requise

**Paramètres :**
- `family_id` (UUID) : Identifiant unique de la famille

**Corps de la requête (tous les champs sont optionnels) :**
```json
{
  "children_ids": ["4", "5", "6"],
  "relation": "married",
  "divorce_info": {
    "divorce_status": "divorced",
    "divorce_date": "2023-01-15"
  },
  "comment": "Notes mises à jour"
}
```

**Réponse :** `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "father_ids": ["1"],
  "mother_ids": ["2"],
  "children_ids": ["4", "5", "6"],
  "relation": "married",
  "divorce_info": {
    "divorce_status": "divorced",
    "divorce_date": "2023-01-15"
  },
  "comment": "Notes mises à jour",
  "updated_at": "2025-10-23T11:00:00Z"
}
```

**Codes d'erreur :**
- `400` : Données invalides
- `401` : Non authentifié
- `404` : Famille non trouvée
- `422` : Erreur de validation

#### `DELETE /api/v1/families/{family_id}`

Supprimer une famille.

**Authentification :** Requise (Admin recommandé)

**Paramètres :**
- `family_id` (UUID) : Identifiant unique de la famille

**Réponse :** `200 OK`
```json
{
  "success": true,
  "message": "Family 550e8400-e29b-41d4-a716-446655440000 deleted successfully",
  "family_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Note :** La suppression d'une famille ne supprime pas les personnes associées.

**Codes d'erreur :**
- `401` : Non authentifié
- `404` : Famille non trouvée

---

### 8. Monitoring

#### `GET /metrics`

Métriques Prometheus (si activées).

**Réponse :** Format Prometheus
```
# TYPE geneweb_http_requests_total counter
geneweb_http_requests_total{method="GET",endpoint="/health",status_code="200"} 1234

# TYPE geneweb_http_request_duration_seconds histogram
geneweb_http_request_duration_seconds_bucket{method="GET",endpoint="/health",le="0.1"} 1000
```

---

## Exemples d'utilisation

### Scénario 1 : Créer et gérer une personne

```bash
# 1. Créer une personne
curl -X POST https://api.geneweb.com/api/v1/persons \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Marie",
    "surname": "Curie",
    "sex": "female",
    "birth_date": "1867-11-07",
    "birth_place": "Varsovie, Pologne",
    "occupation": "Physicienne"
  }'

# Réponse : {"person_id": "abc123...", ...}

# 2. Récupérer la personne
curl -X GET https://api.geneweb.com/api/v1/persons/abc123 \
  -H "Authorization: Bearer YOUR_API_KEY"

# 3. Mettre à jour
curl -X PUT https://api.geneweb.com/api/v1/persons/abc123 \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "notes": "Prix Nobel de Physique (1903) et de Chimie (1911)"
  }'

# 4. Lister toutes les personnes
curl -X GET "https://api.geneweb.com/api/v1/persons?limit=10&skip=0" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Scénario 2 : Gestion RGPD

```bash
# 1. Enregistrer le consentement
curl -X POST https://api.geneweb.com/api/v1/persons/abc123/consent \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "consent_given": true,
    "processing_purposes": [
      "Recherche généalogique",
      "Conservation historique"
    ]
  }'

# 2. Exporter les données (droit d'accès)
curl -X GET https://api.geneweb.com/api/v1/persons/abc123/gdpr-export \
  -H "Authorization: Bearer YOUR_API_KEY" \
  > marie_curie_data.json

# 3. Obtenir les informations de traitement
curl -X GET https://api.geneweb.com/api/v1/persons/abc123/data-processing-info \
  -H "Authorization: Bearer YOUR_API_KEY"

# 4. Anonymiser (droit à l'oubli)
curl -X POST https://api.geneweb.com/api/v1/persons/abc123/anonymize \
  -H "Authorization: Bearer ADMIN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "Demande de l'utilisateur"
  }'
```

### Scénario 3 : Gestion de la base de données

```bash
# 1. Vérifier la santé de la DB
curl -X GET https://api.geneweb.com/api/v1/database/health

# 2. Obtenir les statistiques
curl -X GET https://api.geneweb.com/api/v1/database/stats

# 3. Obtenir les informations
curl -X GET https://api.geneweb.com/api/v1/database/info

# 4. Recharger depuis le disque (admin)
curl -X POST https://api.geneweb.com/api/v1/database/reload \
  -H "Authorization: Bearer ADMIN_API_KEY"

# 5. Commiter les changements (admin)
curl -X POST https://api.geneweb.com/api/v1/database/commit \
  -H "Authorization: Bearer ADMIN_API_KEY"
```

### Scénario 3b : Gestion Multi-Bases de Données

```bash
# 1. Lister toutes les bases de données
curl -X GET https://api.geneweb.com/api/v1/database/databases

# 2. Obtenir la base active
curl -X GET https://api.geneweb.com/api/v1/database/databases/active

# 3. Créer une nouvelle base de données (admin)
curl -X POST https://api.geneweb.com/api/v1/database/databases \
  -H "Authorization: Bearer ADMIN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "nouvelle_famille",
    "set_active": false
  }'

# 4. Activer une base de données (admin)
curl -X POST https://api.geneweb.com/api/v1/database/databases/nouvelle_famille/activate \
  -H "Authorization: Bearer ADMIN_API_KEY"

# 5. Renommer une base de données (admin)
curl -X PUT https://api.geneweb.com/api/v1/database/databases/nouvelle_famille/rename \
  -H "Authorization: Bearer ADMIN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "new_name": "famille_dupont_2024",
    "rename_files": true
  }'

# 6. Supprimer une base (mémoire uniquement, admin)
curl -X DELETE "https://api.geneweb.com/api/v1/database/databases/old_db?delete_files=false" \
  -H "Authorization: Bearer ADMIN_API_KEY"

# 7. Supprimer une base avec fichiers (admin, ATTENTION!)
curl -X DELETE "https://api.geneweb.com/api/v1/database/databases/temp_db?delete_files=true" \
  -H "Authorization: Bearer ADMIN_API_KEY"
```

### Scénario 4 : Monitoring et Health Checks

```bash
# 1. Health check basique
curl -X GET https://api.geneweb.com/health

# 2. Liveness probe (Kubernetes)
curl -X GET https://api.geneweb.com/health/live

# 3. Readiness probe (Kubernetes)
curl -X GET https://api.geneweb.com/health/ready

# 4. Health check détaillé
curl -X GET https://api.geneweb.com/health/detailed

# 5. Métriques Prometheus
curl -X GET https://api.geneweb.com/metrics
```

### Exemple Python

```python
import requests

# Configuration
BASE_URL = "https://api.geneweb.com"
API_KEY = "YOUR_API_KEY"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Créer une personne
person_data = {
    "first_name": "Albert",
    "surname": "Einstein",
    "sex": "male",
    "birth_date": "1879-03-14",
    "birth_place": "Ulm, Allemagne",
    "occupation": "Physicien théoricien"
}

response = requests.post(
    f"{BASE_URL}/api/v1/persons",
    headers=headers,
    json=person_data
)

if response.status_code == 201:
    person = response.json()
    person_id = person["person_id"]
    print(f"Personne créée : {person_id}")
    
    # Récupérer la personne
    response = requests.get(
        f"{BASE_URL}/api/v1/persons/{person_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        person_details = response.json()
        print(f"Détails : {person_details}")
    
    # Enregistrer le consentement RGPD
    consent_data = {
        "consent_given": True,
        "processing_purposes": ["Recherche généalogique"]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/persons/{person_id}/consent",
        headers=headers,
        json=consent_data
    )
    
    if response.status_code == 200:
        print("Consentement enregistré")
    
    # Vérifier les stats de la DB
    response = requests.get(f"{BASE_URL}/api/v1/database/stats")
    if response.status_code == 200:
        stats = response.json()
        print(f"Statistiques DB : {stats}")
else:
    print(f"Erreur : {response.status_code}")
    print(response.json())
```

### Exemple JavaScript/TypeScript

```typescript
// Configuration
const BASE_URL = 'https://api.geneweb.com';
const API_KEY = 'YOUR_API_KEY';

const headers = {
  'Authorization': `Bearer ${API_KEY}`,
  'Content-Type': 'application/json'
};

// Créer une personne
async function createPerson() {
  const personData = {
    first_name: 'Ada',
    surname: 'Lovelace',
    sex: 'female',
    birth_date: '1815-12-10',
    birth_place: 'Londres, Angleterre',
    occupation: 'Mathématicienne'
  };

  try {
    const response = await fetch(`${BASE_URL}/api/v1/persons`, {
      method: 'POST',
      headers: headers,
      body: JSON.stringify(personData)
    });

    if (response.ok) {
      const person = await response.json();
      console.log('Personne créée :', person.person_id);
      
      // Récupérer la personne
      const getResponse = await fetch(
        `${BASE_URL}/api/v1/persons/${person.person_id}`,
        { headers: headers }
      );
      
      if (getResponse.ok) {
        const details = await getResponse.json();
        console.log('Détails :', details);
      }
      
      // Vérifier la santé de la DB
      const healthResponse = await fetch(`${BASE_URL}/api/v1/database/health`);
      if (healthResponse.ok) {
        const health = await healthResponse.json();
        console.log('Santé DB :', health.status);
      }
      
      return person;
    } else {
      const error = await response.json();
      console.error('Erreur :', error);
    }
  } catch (error) {
    console.error('Erreur réseau :', error);
  }
}

// Lister les personnes avec pagination
async function listPersons(skip = 0, limit = 10) {
  try {
    const response = await fetch(
      `${BASE_URL}/api/v1/persons?skip=${skip}&limit=${limit}`,
      { headers: headers }
    );

    if (response.ok) {
      const data = await response.json();
      console.log(`Total: ${data.total}, Retourné: ${data.persons.length}`);
      return data.persons;
    }
  } catch (error) {
    console.error('Erreur :', error);
  }
}

// Utilisation
createPerson();
listPersons(0, 20);
```

### Scénario 3c : Gestion Multi-Bases de Données (Python)

```python
import requests

# Configuration
BASE_URL = 'http://localhost:8000'

# 1. Lister les bases de données disponibles
response = requests.get(f"{BASE_URL}/api/v1/databases")
if response.status_code == 200:
    databases = response.json()
    print(f"Nombre de bases : {databases['total']}")
    print(f"Base active : {databases['active_database']}")
    for db in databases['databases']:
        print(f"  - {db['name']} : {db['status']}")

# 2. Créer une nouvelle base de données
new_db_data = {
    "name": "famille_dupont",
    "base_path": "./databases/dupont.gwb",
    "create_if_missing": True,
    "set_active": False
}

response = requests.post(f"{BASE_URL}/api/v1/databases", json=new_db_data)
if response.status_code == 201:
    db_info = response.json()
    print(f"Base créée : {db_info['name']}")
    print(f"Chemin : {db_info['base_path']}")

# 3. Ajouter des personnes à la base active
person_data = {
    "first_name": "Jean",
    "surname": "Martin",
    "sex": "male",
    "birth_date": "1980-05-15"
}

response = requests.post(f"{BASE_URL}/api/v1/persons", json=person_data)
if response.status_code == 201:
    person = response.json()
    print(f"Personne ajoutée à la base active : {person['person_id']}")

# 4. Activer une autre base de données
response = requests.post(f"{BASE_URL}/api/v1/databases/famille_dupont/activate")
if response.status_code == 200:
    active_db = response.json()
    print(f"Base active maintenant : {active_db['name']}")

# 5. Renommer une base de données
rename_data = {
    "new_name": "famille_dupont_archives",
    "rename_files": True
}

response = requests.patch(
    f"{BASE_URL}/api/v1/database/databases/famille_dupont/rename",
    json=rename_data
)
if response.status_code == 200:
    result = response.json()
    print(f"Base renommée : {result['old_name']} -> {result['new_name']}")
    print(f"Fichiers renommés : {result['files_renamed']}")
    print(f"Nouvelle DB info : {result['database']}")

# 6. Vérifier quelle base est active
response = requests.get(f"{BASE_URL}/api/v1/databases/active")
if response.status_code == 200:
    active_db = response.json()
    print(f"Base actuellement active : {active_db['name']}")
    print(f"État : {active_db['status']}")
    print(f"Nombre de personnes : {active_db.get('person_count', 'N/A')}")

# 6. Lister les personnes dans la nouvelle base (devrait être vide)
response = requests.get(f"{BASE_URL}/api/v1/persons")
if response.status_code == 200:
    data = response.json()
    print(f"Personnes dans {active_db['name']} : {data['total']}")

# 7. Revenir à la base principale
response = requests.post(f"{BASE_URL}/api/v1/databases/main/activate")
if response.status_code == 200:
    print("Retour à la base principale")

# 8. Supprimer une base (sans supprimer les fichiers)
response = requests.delete(f"{BASE_URL}/api/v1/databases/famille_dupont?delete_files=false")
if response.status_code == 204:
    print("Base 'famille_dupont' déchargée (fichiers conservés)")

# 9. Exemple de gestion d'erreurs
response = requests.post(f"{BASE_URL}/api/v1/databases/inexistante/activate")
if response.status_code == 404:
    error = response.json()
    print(f"Erreur attendue : {error['detail']}")
```

### Scénario 4 : Recherche Généalogique avec Protection Vie Privée (Python)

```python
import requests

# Configuration
BASE_URL = 'http://localhost:8000'

# 1. Recherche simple de personnes
response = requests.get(
    f"{BASE_URL}/api/v1/search/persons",
    params={
        "query": "Dupont",
        "include_living": False,  # Exclure personnes vivantes par défaut
        "limit": 20
    }
)

if response.status_code == 200:
    data = response.json()
    print(f"Trouvé {data['total']} personnes nommées Dupont")
    print(f"{data['anonymized_count']} personnes anonymisées")
    
    for person in data['results']:
        print(f"- {person['first_name']} {person['surname']}")
        print(f"  Né(e): {person['birth_date'] or 'Date inconnue'}")
        print(f"  Niveau: {person['privacy_level']}")

# 2. Recherche avancée avec filtres
response = requests.get(
    f"{BASE_URL}/api/v1/search/persons",
    params={
        "query": "Martin",
        "first_name": "Jean",
        "birth_year_from": 1900,
        "birth_year_to": 1950,
        "sex": "male",
        "birth_place": "Paris",
        "limit": 10
    }
)

if response.status_code == 200:
    results = response.json()
    print(f"Résultats filtrés : {results['total']}")

# 3. Récupérer l'arbre des ancêtres
person_id = "P001"
response = requests.get(
    f"{BASE_URL}/api/v1/genealogy/ancestors/{person_id}",
    params={
        "max_generations": 5
    }
)

if response.status_code == 200:
    tree = response.json()
    print(f"Arbre des ancêtres de {person_id}")
    print(f"  Total: {tree['total_nodes']} personnes")
    print(f"  Générations: {tree['max_generation']}")
    print(f"  Anonymisées: {tree['anonymized_count']}")
    
    for node in tree['nodes']:
        indent = "  " * node['generation']
        status = "✓ Décédé(e)" if not node['is_living'] else "• Vivant(e)"
        print(f"{indent}{node['first_name']} {node['surname']} - {status}")
        if node.get('sosa_number'):
            print(f"{indent}  Sosa: {node['sosa_number']}")

# 4. Récupérer l'arbre des descendants
response = requests.get(
    f"{BASE_URL}/api/v1/genealogy/descendants/{person_id}",
    params={
        "max_generations": 3
    }
)

if response.status_code == 200:
    tree = response.json()
    print(f"Arbre des descendants de {person_id}")
    print(f"  Total: {tree['total_nodes']} personnes")
    print(f"  Note: Les vivants non autorisés sont filtrés")

# 5. Recherche par numéro Sosa
response = requests.get(
    f"{BASE_URL}/api/v1/genealogy/sosa/2",
    params={
        "root_person_id": person_id
    }
)

if response.status_code == 200:
    person = response.json()
    print(f"Sosa 2 (père) : {person['first_name']} {person['surname']}")
    print(f"  Relation: {person['relationship']}")
    print(f"  Génération: {person['generation']}")
elif response.status_code == 404:
    print("Sosa 2 non trouvé (père inconnu)")

# 6. Arbre généalogique complet
response = requests.get(
    f"{BASE_URL}/api/v1/genealogy/tree/{person_id}",
    params={
        "tree_type": "full",  # ancestors, descendants, ou full
        "max_generations": 4
    }
)

if response.status_code == 200:
    tree = response.json()
    print(f"Arbre généalogique complet")
    print(f"  Type: {tree['tree_type']}")
    print(f"  Total: {tree['total_nodes']} personnes")
    print(f"  Protection: {tree['anonymized_count']} anonymisées")

# 7. Consulter les règles de confidentialité
response = requests.get(f"{BASE_URL}/api/v1/search/privacy-info")

if response.status_code == 200:
    info = response.json()
    print("\nRègles de confidentialité :")
    for level, details in info['privacy_levels'].items():
        print(f"  {level.upper()}: {details['description']}")
        print(f"    Données: {', '.join(details['data_visible'])}")
    
    print(f"\nCritère personne vivante: {info['living_criteria']}")
    print(f"Accès par défaut: {info['default_access']}")

# 8. Recherche incluant les personnes vivantes (avec autorisation)
response = requests.get(
    f"{BASE_URL}/api/v1/search/persons",
    params={
        "query": "Dupont",
        "include_living": True,  # Nécessite autorisation
        "user_id": "user123",    # ID utilisateur authentifié
        "limit": 50
    }
)

if response.status_code == 200:
    data = response.json()
    print(f"\nRecherche incluant vivants : {data['total']} résultats")
    
    # Analyser les niveaux de confidentialité
    public_count = sum(1 for p in data['results'] if p['privacy_level'] == 'public')
    restricted_count = sum(1 for p in data['results'] if p['privacy_level'] == 'restricted')
    anonymized_count = sum(1 for p in data['results'] if p['privacy_level'] == 'anonymized')
    
    print(f"  PUBLIC: {public_count}")
    print(f"  RESTRICTED: {restricted_count}")
    print(f"  ANONYMIZED: {anonymized_count}")
```

### Scénario 4b : Recherche Généalogique (cURL)

```bash
# Recherche simple
curl "http://localhost:8000/api/v1/search/persons?query=Dupont&limit=10"

# Recherche avec filtres
curl "http://localhost:8000/api/v1/search/persons?query=Martin&first_name=Jean&birth_year_from=1900&birth_year_to=1950&sex=male"

# Arbre des ancêtres
curl "http://localhost:8000/api/v1/genealogy/ancestors/P001?max_generations=5"

# Arbre des descendants
curl "http://localhost:8000/api/v1/genealogy/descendants/P001?max_generations=3"

# Recherche par numéro Sosa
curl "http://localhost:8000/api/v1/genealogy/sosa/2?root_person_id=P001"

# Arbre complet
curl "http://localhost:8000/api/v1/genealogy/tree/P001?tree_type=full&max_generations=4"

# Règles de confidentialité
curl "http://localhost:8000/api/v1/search/privacy-info"
```

---

### Monitoring

#### `GET /metrics`

## Sécurité

### Mesures de sécurité implémentées

#### Transport et HTTPS
- ✅ **HTTPS obligatoire** en production
- ✅ **HSTS** avec preload et subdomains
- ✅ **TLS 1.2+** minimum
- ✅ **Certificate pinning** (optionnel)

#### Headers de sécurité
- ✅ **Content-Security-Policy**
- ✅ **X-Frame-Options: DENY**
- ✅ **X-Content-Type-Options: nosniff**
- ✅ **X-XSS-Protection**
- ✅ **Referrer-Policy**
- ✅ **Permissions-Policy**

#### Protection contre les attaques
- ✅ **Rate limiting** (100 req/min par IP)
- ✅ **Protection DDoS**
- ✅ **Validation des entrées** globale
- ✅ **Protection injection SQL**
- ✅ **Protection XSS**
- ✅ **Protection CSRF**

#### CORS sécurisé
- ✅ **Origins restreints** (frontend uniquement)
- ✅ **Méthodes contrôlées**
- ✅ **Headers validés**

#### Logging sécurisé
- ✅ **Filtrage des données PII**
- ✅ **Masquage des secrets**
- ✅ **Événements de sécurité tracés**

### Codes d'erreur standardisés

L'API utilise les codes HTTP standard et retourne des messages d'erreur structurés :

#### Codes de succès
- **200 OK** : Requête réussie
- **201 Created** : Ressource créée avec succès
- **204 No Content** : Suppression réussie

#### Codes d'erreur client (4xx)
- **400 Bad Request** : Données invalides
- **401 Unauthorized** : Non authentifié
- **403 Forbidden** : Non autorisé (permissions insuffisantes)
- **404 Not Found** : Ressource non trouvée
- **409 Conflict** : Conflit (ex: base de données en lecture seule)
- **422 Unprocessable Entity** : Erreur de validation
- **429 Too Many Requests** : Rate limiting dépassé

#### Codes d'erreur serveur (5xx)
- **500 Internal Server Error** : Erreur interne
- **503 Service Unavailable** : Service temporairement indisponible

#### Format des erreurs

```json
{
  "detail": "Message d'erreur descriptif",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2025-10-19T14:30:00Z",
  "path": "/api/v1/persons",
  "validation_errors": [
    {
      "field": "birth_date",
      "message": "Format de date invalide"
    }
  ]
}
```

### Recommandations de sécurité

1. **Certificats SSL** : Utilisez des certificats valides d'une CA reconnue
2. **Secrets forts** : Générez des clés de 32+ caractères
3. **Firewall** : Limitez l'accès aux ports nécessaires
4. **Monitoring** : Surveillez les événements de sécurité
5. **Mises à jour** : Maintenez les dépendances à jour

### Rate Limiting

L'API implémente un rate limiting pour prévenir les abus :

- **Limite par défaut** : 100 requêtes par minute par IP
- **Limite admin** : 1000 requêtes par minute
- **Headers de réponse** :
  - `X-RateLimit-Limit` : Limite maximale
  - `X-RateLimit-Remaining` : Requêtes restantes
  - `X-RateLimit-Reset` : Timestamp de réinitialisation

**Exemple de réponse rate limited :**
```json
{
  "detail": "Trop de requêtes. Réessayez dans 45 secondes.",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "retry_after": 45
}
```

## Monitoring

### Métriques disponibles

#### Métriques HTTP
- `geneweb_http_requests_total` : Nombre total de requêtes
- `geneweb_http_request_duration_seconds` : Durée des requêtes
- `geneweb_active_connections` : Connexions actives

#### Métriques de sécurité
- `geneweb_rate_limit_hits_total` : Violations de rate limiting
- `geneweb_security_events_total` : Événements de sécurité

#### Métriques d'application
- `geneweb_application_info` : Informations sur l'application
- `geneweb_database_operations_total` : Opérations base de données

### Configuration Prometheus

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'geneweb-api'
    static_configs:
      - targets: ['api.geneweb.com:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s
```

### Alertes recommandées

```yaml
# alerts.yml
groups:
  - name: geneweb-api
    rules:
      - alert: HighErrorRate
        expr: rate(geneweb_http_requests_total{status_code=~"5.."}[5m]) > 0.1
        for: 2m
        
      - alert: RateLimitHigh
        expr: rate(geneweb_rate_limit_hits_total[5m]) > 10
        for: 1m
```

## Déploiement

### Déploiement de base

```bash
# Mode développement
python start_api.py --dev --reload

# Mode production
python start_api.py --host 0.0.0.0 --port 8000 --workers 4
```

### Déploiement Docker

```bash
# Construction
docker build -t geneweb-api .

# Exécution
docker run -d \
  --name geneweb-api \
  -p 8443:8000 \
  -v /path/to/ssl:/etc/geneweb/ssl:ro \
  -e GENEWEB_SECURITY_SECRET_KEY=your_secret \
  geneweb-api
```

### Déploiement Docker Compose

```bash
# Démarrage complet avec base de données et monitoring
docker-compose up -d

# Vérification des logs
docker-compose logs -f geneweb-api
```

### Déploiement Kubernetes

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: geneweb-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: geneweb-api
  template:
    metadata:
      labels:
        app: geneweb-api
    spec:
      containers:
      - name: geneweb-api
        image: geneweb-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: GENEWEB_SECURITY_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: geneweb-secrets
              key: secret-key
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Reverse Proxy (Nginx)

```nginx
# nginx.conf
server {
    listen 443 ssl http2;
    server_name api.geneweb.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload";
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Développement

### Configuration de l'environnement de développement

```bash
# Installation des dépendances de développement
pip install -r requirements-dev.txt

# Configuration pre-commit
pre-commit install

# Tests de linting
flake8 src/ start_api.py
black src/ start_api.py
isort src/ start_api.py

# Tests de sécurité
python start_api.py --check-only
```

### Structure des tests

```bash
tests/
├── test_security.py        # Tests de sécurité
├── test_endpoints.py       # Tests des endpoints
├── test_middleware.py      # Tests des middlewares
├── test_validation.py      # Tests de validation
└── test_monitoring.py      # Tests du monitoring
```

### Ajouter un nouvel endpoint

1. **Créer le router** dans `src/geneweb/api/routers/`
2. **Définir les modèles** avec `SecureBaseModel`
3. **Ajouter la validation** des entrées
4. **Implémenter le logging** de sécurité
5. **Ajouter les métriques** si nécessaire
6. **Inclure dans main.py**

Exemple :

```python
# routers/users.py
from fastapi import APIRouter
from ..security.validation import SecureBaseModel
from ..security.logging import log_security_event

router = APIRouter()

class UserModel(SecureBaseModel):
    name: str = Field(..., max_length=100)
    email: str = Field(..., max_length=254)

@router.post("/users/")
async def create_user(user: UserModel):
    log_security_event("user_creation", {"user_email": user.email})
    # Implémentation...
    return {"status": "created"}
```

## Exemples

### Utilisation avec curl

```bash
# Health check
curl https://api.geneweb.com/health

# Avec API key
curl -H "Authorization: Bearer gw_your_api_key" \
     https://api.geneweb.com/api/v1/users

# Avec données JSON
curl -X POST \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer gw_your_api_key" \
     -d '{"name":"John Doe","email":"john@example.com"}' \
     https://api.geneweb.com/api/v1/users
```

### Utilisation avec Python

```python
import httpx

# Configuration du client
client = httpx.Client(
    base_url="https://api.geneweb.com",
    headers={"Authorization": "Bearer gw_your_api_key"},
    timeout=30.0
)

# Health check
response = client.get("/health")
print(response.json())

# Création d'utilisateur
user_data = {
    "name": "John Doe",
    "email": "john@example.com"
}
response = client.post("/api/v1/users", json=user_data)
print(response.json())
```

### Utilisation avec JavaScript

```javascript
// Configuration
const API_BASE = 'https://api.geneweb.com';
const API_KEY = 'gw_your_api_key';

// Headers par défaut
const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${API_KEY}`
};

// Health check
fetch(`${API_BASE}/health`)
    .then(response => response.json())
    .then(data => console.log(data));

// Création d'utilisateur
fetch(`${API_BASE}/api/v1/users`, {
    method: 'POST',
    headers: headers,
    body: JSON.stringify({
        name: 'John Doe',
        email: 'john@example.com'
    })
})
.then(response => response.json())
.then(data => console.log(data));
```

## Codes d'erreur

### Codes de statut HTTP

| Code | Description | Utilisation |
|------|-------------|-------------|
| 200 | OK | Succès |
| 201 | Created | Ressource créée |
| 400 | Bad Request | Données invalides |
| 401 | Unauthorized | Authentification requise |
| 403 | Forbidden | Accès refusé |
| 404 | Not Found | Ressource non trouvée |
| 429 | Too Many Requests | Rate limit dépassé |
| 500 | Internal Server Error | Erreur serveur |

### Format des erreurs

```json
{
    "error": "validation_error",
    "message": "Les données fournies sont invalides",
    "details": {
        "field": "email",
        "reason": "Format d'email invalide"
    },
    "request_id": "req_123456789"
}
```

## Support et Maintenance

### Logs importants

```bash
# Logs de sécurité
tail -f /var/log/geneweb/api.log | grep "security_event"

# Erreurs d'authentification
tail -f /var/log/geneweb/api.log | grep "auth_failure"

# Rate limiting
tail -f /var/log/geneweb/api.log | grep "rate_limit"
```

### Commandes de diagnostic

```bash
# Vérifier la santé de l'API
curl https://api.geneweb.com/health/detailed

# Vérifier les métriques
curl https://api.geneweb.com/metrics

# Tester les certificats SSL
openssl s_client -connect api.geneweb.com:443 -servername api.geneweb.com
```

### Mise à jour

```bash
# Sauvegarder la configuration
cp .env .env.backup

# Mettre à jour les dépendances
pip install --upgrade -r requirements.txt

# Relancer les tests de sécurité
python start_api.py --check-only

# Redémarrer le service
systemctl restart geneweb-api
```

---

Cette documentation couvre tous les aspects de l'API Geneweb. Pour des questions spécifiques ou des problèmes, consultez les logs ou contactez l'équipe de développement.