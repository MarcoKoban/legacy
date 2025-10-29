# Architecture de l'API Geneweb

## Vue d'ensemble

L'API Geneweb est construite selon une architecture en couches qui privilégie la sécurité, la performance et la maintenabilité.

## Diagramme d'architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          Client Layer                           │
├─────────────────────────────────────────────────────────────────┤
│  Angular Frontend  │  Mobile App  │  External APIs  │  CLI Tools │
└─────────────────────┬───────────────┬─────────────────┬───────────┘
                      │               │                 │
                      ▼               ▼                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Load Balancer / Reverse Proxy              │
│                        (Nginx / Apache)                         │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Security Layer                               │
├─────────────────────────────────────────────────────────────────┤
│  HTTPS Termination  │  Rate Limiting  │  DDoS Protection       │
│  Certificate Pinning │ CORS           │  Input Validation      │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FastAPI Application                           │
├─────────────────────────────────────────────────────────────────┤
│                    Middleware Stack                             │
│  ┌─────────────────┬─────────────────┬─────────────────────────┐ │
│  │ Security Headers│ Rate Limiting   │ Request Size Limiting   │ │
│  │ HTTPS Redirect  │ IP Whitelisting │ Timing Attack Protection│ │
│  │ CORS Control    │ Metrics         │ Error Handling          │ │
│  └─────────────────┴─────────────────┴─────────────────────────┘ │
│                                                                 │
│                      Router Layer                               │
│  ┌─────────────────┬─────────────────┬─────────────────────────┐ │
│  │ Health Endpoints│ API v1 Endpoints│ Admin Endpoints         │ │
│  │ /health         │ /api/v1/        │ /admin/                 │ │
│  │ /metrics        │ - persons       │ - config                │ │
│  └─────────────────┴─────────────────┴─────────────────────────┘ │
│                                                                 │
│                     Service Layer                               │
│  ┌─────────────────┬─────────────────┬─────────────────────────┐ │
│  │ Business Logic  │ Validation      │ Security Services       │ │
│  │ - Genealogy     │ - Input         │ - Authentication        │ │
│  │ - Relationships │ - Business Rules│ - Authorization         │ │
│  │ - SOSA Numbers  │ - Data Integrity│ - Encryption            │ │
│  └─────────────────┴─────────────────┴─────────────────────────┘ │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Data Access Layer                            │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┬─────────────────┬─────────────────────────┐ │
│  │ ORM/Database    │ Cache Layer     │ File Storage            │ │
│  │ - SQLAlchemy    │ - Redis         │ - Media Files           │ │
│  │ - PostgreSQL    │ - Session Store │ - Document Storage      │ │
│  └─────────────────┴─────────────────┴─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Monitoring & Logging                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┬─────────────────┬─────────────────────────┐ │
│  │ Metrics         │ Logging         │ Alerting                │ │
│  │ - Prometheus    │ - Structured    │ - Grafana               │ │
│  │ - Custom        │ - Security      │ - Email/Slack           │ │
│  │ - Performance   │ - Audit Trail   │ - PagerDuty             │ │
│  └─────────────────┴─────────────────┴─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Architecture des modules

### 1. Configuration Layer (`config.py`)

**Responsabilités :**
- Gestion centralisée de la configuration
- Variables d'environnement sécurisées
- Validation des paramètres
- Configuration par environnement (dev/prod)

**Composants :**
```python
SecuritySettings    # Configuration sécurité
DatabaseSettings    # Configuration base de données
LoggingSettings     # Configuration logging
MonitoringSettings  # Configuration monitoring
APISettings         # Configuration générale
```

### 2. Security Layer (`security/`)

**Responsabilités :**
- Authentification et autorisation
- Chiffrement et hachage
- Validation des entrées
- Logging sécurisé
- Gestion des secrets

**Modules :**
```python
secrets.py      # Gestion des secrets et chiffrement
validation.py   # Validation globale des entrées
logging.py      # Logging sécurisé et filtrage PII
```

### 3. Middleware Layer (`middleware/`)

**Responsabilités :**
- Traitement des requêtes/réponses
- Application des politiques de sécurité
- Métriques et monitoring
- Gestion des erreurs

**Modules :**
```python
security.py         # Headers de sécurité, HTTPS, timing
rate_limiting.py    # Protection DDoS et rate limiting
```

### 4. Router Layer (`routers/`)

**Responsabilités :**
- Définition des endpoints
- Validation des données d'entrée
- Sérialisation des réponses
- Documentation API

**Structure :**
```python
health.py       # Health checks et monitoring
auth.py         # Authentification (à implémenter)
persons.py      # Gestion des personnes (à implémenter)
families.py     # Gestion des familles (à implémenter)
events.py       # Gestion des événements (à implémenter)
```

### 5. Monitoring Layer (`monitoring/`)

**Responsabilités :**
- Collection de métriques
- Surveillance de la performance
- Alerting et notifications
- Tableaux de bord

**Modules :**
```python
metrics.py      # Métriques Prometheus
health.py       # Vérifications de santé
alerts.py       # Système d'alertes (à implémenter)
```

## Patterns architecturaux utilisés

### 1. Dependency Injection

```python
# Configuration centralisée
from geneweb.api.config import settings

# Services injectés
def get_database():
    return Database(settings.database.database_url)

def get_secrets_manager():
    return SecretsManager(settings.security.secret_key)
```

### 2. Middleware Pattern

```python
# Chaînage des middlewares
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(CORSMiddleware)
```

### 3. Repository Pattern (à implémenter)

```python
class PersonRepository:
    def __init__(self, db: Database):
        self.db = db
    
    async def create(self, person: PersonModel) -> Person:
        # Implémentation
        pass
```

### 4. Factory Pattern

```python
def create_app() -> FastAPI:
    """Factory pour créer l'application FastAPI"""
    app = FastAPI(...)
    setup_middleware(app)
    setup_routes(app)
    setup_monitoring(app)
    return app
```

## Sécurité par couches

### 1. Transport Security
- **HTTPS obligatoire** en production
- **HSTS** avec preload
- **Certificate pinning** (optionnel)
- **TLS 1.2+** minimum

### 2. Application Security
- **Headers de sécurité** automatiques
- **CORS** restreint
- **Rate limiting** par IP
- **Input validation** globale

### 3. Data Security
- **Chiffrement** des secrets
- **Hachage** des mots de passe
- **PII filtering** dans les logs
- **Audit trail** des opérations

### 4. Infrastructure Security
- **Conteneurs** non-privilégiés
- **Secrets management**
- **Network segmentation**
- **Resource limiting**

## Performance et Scalabilité

### 1. Async/Await
```python
# Tous les endpoints sont asynchrones
async def get_person(person_id: int):
    async with get_database() as db:
        return await db.persons.get(person_id)
```

### 2. Connection Pooling
```python
# Pool de connexions pour la base de données
database = Database(
    url=settings.database.database_url,
    min_connections=5,
    max_connections=20
)
```

### 3. Caching Strategy
```python
# Cache Redis pour les données fréquemment accédées
@cache(ttl=3600)  # 1 heure
async def get_person_sosa(person_id: int):
    # Calcul complexe mis en cache
    pass
```

### 4. Load Balancing
- **Horizontal scaling** avec plusieurs instances
- **Health checks** pour load balancer
- **Session affinity** si nécessaire

## Monitoring et Observabilité

### 1. Métriques (Prometheus)
```python
# Métriques custom
business_operations = Counter(
    'geneweb_business_operations_total',
    'Business operations',
    ['operation', 'status']
)
```

### 2. Logging structuré
```python
# Logs JSON avec contexte
logger.info(
    "Person created",
    person_id=person.id,
    user_id=user.id,
    operation="create_person"
)
```

### 3. Tracing (à implémenter)
```python
# OpenTelemetry pour le tracing distribué
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

@tracer.start_span("create_person")
async def create_person(...):
    pass
```

### 4. Health Checks
```python
# Health checks multi-niveaux
- /health          # Basique
- /health/live     # Liveness
- /health/ready    # Readiness
- /health/detailed # Complet
```

## Tests et Qualité

### 1. Test Pyramid
```
    ┌─────────────────┐
    │   E2E Tests     │ ← Tests d'intégration complets
    ├─────────────────┤
    │ Integration     │ ← Tests d'API
    │    Tests        │
    ├─────────────────┤
    │   Unit Tests    │ ← Tests unitaires
    │                 │
    └─────────────────┘
```

### 2. Security Testing
- **Static analysis** (bandit, semgrep)
- **Dependency scanning** (safety)
- **SAST/DAST** testing
- **Penetration testing**

### 3. Performance Testing
- **Load testing** (locust)
- **Stress testing**
- **Benchmark** des endpoints critiques

## Déploiement et DevOps

### 1. Container Strategy
```dockerfile
# Multi-stage build
FROM python:3.11-slim as builder
# Build dependencies

FROM python:3.11-slim as production
# Runtime minimal
```

### 2. Infrastructure as Code
```yaml
# Kubernetes manifests
apiVersion: apps/v1
kind: Deployment
metadata:
  name: geneweb-api
spec:
  replicas: 3
  # Configuration...
```

### 3. CI/CD Pipeline
```yaml
# GitHub Actions / GitLab CI
stages:
  - test
  - security-scan
  - build
  - deploy
```

### 4. Environment Management
```bash
# Environnements séparés
- development   # Développement local
- staging      # Tests d'intégration
- production   # Production
```

## Évolution et Extensibilité

### 1. API Versioning
```python
# Versioning par préfixe
/api/v1/persons
/api/v2/persons

# Backward compatibility
```

### 2. Plugin Architecture
```python
# Interface pour extensions
class Plugin(ABC):
    @abstractmethod
    def setup(self, app: FastAPI):
        pass
```

### 3. Event-Driven Architecture
```python
# Events pour découplage
@event_handler("person.created")
async def on_person_created(event: PersonCreatedEvent):
    # Actions post-création
    pass
```

### 4. Microservices Ready
```python
# Modularité pour extraction future
- geneweb-persons-service
- geneweb-families-service
- geneweb-events-service
```

---

Cette architecture garantit **sécurité**, **performance**, **maintenabilité** et **évolutivité** pour l'API Geneweb.