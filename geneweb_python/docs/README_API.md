# Geneweb API - Secure FastAPI Implementation

## Overview
Secure REST API implementation for the Geneweb genealogy system using FastAPI with comprehensive security features and JWT authentication.

## 🔐 Authentication System

L'API utilise maintenant un **système d'authentification JWT moderne** avec :

- ✅ **JWT Tokens** (Access + Refresh)
- ✅ **Stockage sécurisé** des mots de passe (bcrypt)
- ✅ **Token blacklist** pour révocation
- ✅ **Historique des mots de passe**
- ✅ **Sessions utilisateur** traçables
- ✅ **Audit complet** des événements d'authentification

### Quick Start Authentication

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

#### 2. Se connecter
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john.doe",
    "password": "SecureP@ss123!"
  }'
```

**Réponse** :
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
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X GET "http://localhost:8000/api/v1/persons" \
  -H "Authorization: Bearer $TOKEN"
```

> 📖 **Documentation complète** : [AUTHENTICATION_GUIDE.md](AUTHENTICATION_GUIDE.md)

## Security Features ✅

### 🔒 **Authentication & Authorization**
- JWT tokens with JTI for revocation
- Bcrypt password hashing (cost=12)
- Token blacklist mechanism
- Password history tracking
- Session management
- Audit logging

### 🔒 **HTTPS and Transport Security**
- Forced HTTPS redirects in production
- HSTS headers with 1-year max-age
- TLS 1.2+ enforcement
- Optional certificate pinning (HPKP)

### 🛡️ **Security Headers**
- Content Security Policy (CSP)
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- X-XSS-Protection
- Referrer-Policy
- Permissions-Policy

### 🌐 **CORS Security**
- Restricted to Angular frontend domains only
- Secure credential handling
- Method and header whitelisting

### 🚦 **Rate Limiting & DDoS Protection**
- 100 requests/minute per IP (configurable)
- Burst protection (200 requests)
- IP whitelisting for internal networks
- Request size limiting (1MB max)

### 🔍 **Input Validation**
- Global injection attack prevention
- SQL injection protection
- XSS prevention
- Command injection blocking
- Path traversal protection
- Automatic data sanitization

### 📊 **Secure Logging & Monitoring**
- Structured JSON logging
- PII and secret filtering
- Security event tracking
- Prometheus metrics integration
- Grafana dashboards ready

### 🔐 **Secrets Management**
- Environment-based configuration
- Fernet encryption for secrets
- PBKDF2 password hashing
- Secure token generation
- API key management

## Quick Start

### 1. **Installation**
```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env

# Edit .env with your secure configuration
nano .env
```

### 2. **Development Mode**
```bash
# Run security checks only
python start_api.py --check-only

# Start in development mode (HTTP allowed)
python start_api.py --dev --reload
```

### 3. **Production Deployment**
```bash
# Generate SSL certificates first
# Edit .env with production settings

# Start with SSL
python start_api.py --host 0.0.0.0 --port 8000 --workers 4
```

### 4. **Docker Deployment**
```bash
# Build and start with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f geneweb-api
```

## API Endpoints

### Authentication
- `POST /auth/register` - Créer un compte utilisateur
- `POST /auth/login` - Connexion (retourne JWT)
- `POST /auth/login/oauth2` - Connexion OAuth2 compatible
- `POST /auth/refresh` - Rafraîchir l'access token
- `POST /auth/logout` - Déconnexion (blacklist token)
- `GET /auth/me` - Profil utilisateur connecté
- `POST /auth/change-password` - Changer le mot de passe
- `GET /auth/health` - Santé du système d'authentification

### Health Checks
- `GET /health` - Basic health check (public)
- `GET /health/live` - Kubernetes liveness probe
- `GET /health/ready` - Kubernetes readiness probe  
- `GET /health/detailed` - Detailed health (internal networks only)

### Monitoring
- `GET /metrics` - Prometheus metrics (if enabled)
- Security event metrics
- Performance monitoring
- Rate limiting statistics

### Persons & Families
- `POST /api/v1/persons` - Créer une personne
- `GET /api/v1/persons/{id}` - Récupérer une personne
- `GET /api/v1/persons` - Lister les personnes
- `PUT /api/v1/persons/{id}` - Mettre à jour une personne
- `DELETE /api/v1/persons/{id}` - Supprimer une personne (Admin)
- `POST /api/v1/families` - Créer une famille
- `GET /api/v1/families/{id}` - Récupérer une famille

> 📖 Voir [API_DOCUMENTATION.md](API/API_DOCUMENTATION.md) pour la liste complète des endpoints

## Configuration

### Required Environment Variables
```bash
# JWT Authentication (REQUIRED)
GENEWEB_JWT_SECRET_KEY=your-256-bit-secret-key-here
GENEWEB_JWT_ALGORITHM=HS256
GENEWEB_JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
GENEWEB_JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Database (REQUIRED for authentication)
GENEWEB_DB_DATABASE_URL=sqlite:///./geneweb.db
# or for production:
# GENEWEB_DB_DATABASE_URL=postgresql://user:pass@localhost:5432/geneweb

# Security (REQUIRED for production)
GENEWEB_SECURITY_SECRET_KEY=your-32-char-secret-key
GENEWEB_SECURITY_ENCRYPTION_KEY=your-32-char-encryption-key

# SSL Certificates (REQUIRED for production)
GENEWEB_API_SSL_CERTFILE=/path/to/cert.pem
GENEWEB_API_SSL_KEYFILE=/path/to/key.pem

# CORS Origins (Restrict to your frontend)
GENEWEB_SECURITY_CORS_ORIGINS=["https://your-frontend.com"]
```

### Optional Configuration
```bash
# Rate limiting
GENEWEB_SECURITY_RATE_LIMIT_PER_MINUTE=100
GENEWEB_SECURITY_RATE_LIMIT_BURST=200

# Logging
GENEWEB_LOG_LOG_LEVEL=INFO
GENEWEB_LOG_LOG_FORMAT=json

# Monitoring
GENEWEB_MONITORING_ENABLE_METRICS=true
```

## Security Compliance ✅

### Criteria Met:
- ✅ **JWT Authentication** with access + refresh tokens
- ✅ **Bcrypt password hashing** (cost=12, auto salt)
- ✅ **Token blacklist** for revocation
- ✅ **Password history** tracking
- ✅ **Session management** with audit logging
- ✅ **API starts HTTPS only** (production mode)
- ✅ **Security headers on all responses** 
- ✅ **Rate limiting configured** (100 req/min per IP)
- ✅ **Structured logs without PII**
- ✅ **Secure health check** (/health endpoint)
- ✅ **CORS restricted to Angular only**
- ✅ **DDoS protection implemented**
- ✅ **Input validation globally applied**
- ✅ **Secrets management with encryption**
- ✅ **Certificate pinning ready**
- ✅ **Prometheus monitoring integrated**

### OWASP Top 10 Protection:
- ✅ **A01: Broken Access Control** - Rate limiting, CORS, validation
- ✅ **A02: Cryptographic Failures** - HTTPS, HSTS, encrypted secrets
- ✅ **A03: Injection** - Input validation, SQL injection prevention
- ✅ **A04: Insecure Design** - Security by design architecture
- ✅ **A05: Security Misconfiguration** - Secure defaults, headers
- ✅ **A06: Vulnerable Components** - Dependency management
- ✅ **A07: Authentication Failures** - Secure auth infrastructure
- ✅ **A08: Software Integrity** - Secure build pipeline
- ✅ **A09: Security Logging** - Comprehensive security logging
- ✅ **A10: Server-Side Request Forgery** - Input validation, URL filtering

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Angular       │    │   Geneweb API    │    │   Database      │
│   Frontend      │────│   (FastAPI)      │────│   (PostgreSQL)  │
│   (HTTPS only)  │    │   + Security     │    │   (Encrypted)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                       ┌──────────────────┐
                       │   Monitoring     │
                       │   (Prometheus +  │
                       │    Grafana)      │
                       └──────────────────┘
```

## Development

### Project Structure
```
src/geneweb/api/
├── __init__.py
├── main.py              # FastAPI application
├── config.py            # Security configuration
├── middleware/          # Security middlewares
│   ├── security.py      # Security headers, HTTPS
│   └── rate_limiting.py # DDoS protection
├── security/            # Security modules
│   ├── logging.py       # Secure logging
│   ├── secrets.py       # Encryption, secrets
│   └── validation.py    # Input validation
├── monitoring/          # Monitoring and metrics
│   └── metrics.py       # Prometheus integration
└── routers/             # API endpoints
    └── health.py        # Health check endpoints
```

### Adding New Features
1. All new endpoints must use `SecureBaseModel` for input validation
2. Add security logging for sensitive operations
3. Update rate limiting rules if needed
4. Add metrics for monitoring
5. Update health checks if dependencies are added

## Production Deployment Checklist

### Before Deployment:
- [ ] SSL certificates configured and valid
- [ ] All environment variables set securely  
- [ ] Database connections encrypted
- [ ] CORS origins restricted to frontend domains
- [ ] Monitoring and alerting configured
- [ ] Log rotation and backup configured
- [ ] Firewall rules configured (only necessary ports)
- [ ] Regular security updates scheduled

### Security Monitoring:
- [ ] Prometheus metrics collection enabled
- [ ] Grafana dashboards configured
- [ ] Security event alerting set up
- [ ] Log analysis tools configured
- [ ] Incident response procedures documented

## Support

For security issues or questions:
- Review `SECURITY.md` for detailed security documentation
- Check logs for security events and errors
- Monitor metrics for unusual patterns
- Follow secure deployment practices

---

**🔒 This implementation prioritizes security while maintaining performance and usability. All security measures are configurable and follow industry best practices.**