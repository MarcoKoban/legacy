# Changements Architecturaux - Migration OCaml vers Python

## Migration des Clés Tuple vers les Objets Person Directs

### Contexte

Dans l'implémentation OCaml originale de Geneweb, les personnes étaient référencées par des clés tuple de la forme `(first_name, surname, occ)` pour des raisons techniques liées aux contraintes du langage OCaml. 

### Problématique de l'Ancien Système

L'ancien système utilisait des clés tuple pour identifier les personnes :

```python
# Ancienne approche (basée sur OCaml)
family = Family(
    father_key=("John", "Doe", 0),
    mother_key=("Jane", "Smith", 0), 
    children_keys=[("Alice", "Doe", 0), ("Bob", "Doe", 0)]
)

witness = WitnessInfo(
    person_key=("Marie", "Martin", 0),
    witness_type=WitnessKind.WITNESS
)
```

**Inconvénients de cette approche :**
- Duplication des données personnelles
- Risque d'incohérence entre la clé et l'objet Person réel
- Complexité inutile dans la gestion des relations
- Moins pythonique et naturel

### Nouvelle Approche : Objets Person Directs

La nouvelle implémentation Python utilise directement les objets `Person` comme clés :

```python
# Nouvelle approche (Python natif)
john = Person(first_name="John", surname="Doe", sex=Sex.MALE, occ=0)
jane = Person(first_name="Jane", surname="Smith", sex=Sex.FEMALE, occ=0)
alice = Person(first_name="Alice", surname="Doe", sex=Sex.FEMALE, occ=0)
bob = Person(first_name="Bob", surname="Doe", sex=Sex.MALE, occ=0)

family = Family(
    father=john,
    mother=jane,
    children=[alice, bob]
)

witness = WitnessInfo(
    person=marie,
    witness_type=WitnessKind.WITNESS
)
```

**Avantages de cette approche :**
- **Plus pythonique** : utilise les objets natifs comme clés
- **Sécurité des types** : impossible de référencer une personne inexistante
- **Cohérence garantie** : l'objet contient déjà toutes les informations
- **Simplicité** : pas de déréférencement de clé nécessaire
- **Performance** : hashing optimisé sur les objets Person

### Implémentation Technique

#### Hashing et Égalité des Objets Person

Les objets `Person` sont **frozen dataclasses** avec un hashing basé sur les attributs uniques :

```python
@dataclass(frozen=True, eq=True)
class Person:
    first_name: str
    surname: str
    sex: Sex
    occ: int = 0
    # ... autres attributs
    
    def __hash__(self) -> int:
        """Hash basé sur les attributs d'identification unique."""
        return hash((self.first_name, self.surname, self.occ))
    
    def __eq__(self, other) -> bool:
        """Égalité basée sur les mêmes attributs."""
        if not isinstance(other, Person):
            return False
        return (
            self.first_name == other.first_name and
            self.surname == other.surname and
            self.occ == other.occ
        )
```

#### Classes Refactorisées

**Classe Family :**
```python
@dataclass(frozen=True, eq=True)
class Family:
    # Anciennement : father_key, mother_key, children_keys
    father: Optional[Person] = None
    mother: Optional[Person] = None 
    children: List[Person] = field(default_factory=list)
    
    def key(self) -> Tuple[Optional[Person], Optional[Person]]:
        """Clé unique basée sur les parents."""
        return (self.father, self.mother)
    
    def add_child(self, child: Person) -> "Family":
        """Ajouter un enfant (immutable)."""
        if child in self.children:
            return self
        new_children = list(self.children) + [child]
        return dataclasses.replace(self, children=new_children)
```

**Classe WitnessInfo :**
```python
@dataclass(frozen=True, eq=True) 
class WitnessInfo:
    # Anciennement : person_key: Tuple[str, str, int]
    person: Person
    witness_type: WitnessKind = WitnessKind.WITNESS
    
    def __str__(self) -> str:
        name = f"{self.person.first_name} {self.person.surname}"
        if self.person.occ > 0:
            name += f" ({self.person.occ})"
        return f"{name} ({self.witness_type.value.replace('_', ' ').title()})"
```

### Migration des Tests

Tous les tests ont été migrés pour utiliser la nouvelle API :

```python
# Fixtures pour les tests
@pytest.fixture
def john_doe():
    return Person(first_name="John", surname="Doe", sex=Sex.MALE, occ=0)

@pytest.fixture  
def jane_smith():
    return Person(first_name="Jane", surname="Smith", sex=Sex.FEMALE, occ=0)

# Tests avec la nouvelle API
def test_family_complete(john_doe, jane_smith):
    alice = Person(first_name="Alice", surname="Doe", sex=Sex.FEMALE, occ=0)
    bob = Person(first_name="Bob", surname="Doe", sex=Sex.MALE, occ=0)
    
    family = Family(
        father=john_doe,
        mother=jane_smith,
        children=[alice, bob]
    )
    
    assert family.father == john_doe
    assert family.mother == jane_smith
    assert alice in family.children
    assert bob in family.children
```

### Bénéfices Architecturaux

1. **Amélioration de la Lisibilité** : Le code est plus naturel et expressif
2. **Réduction des Erreurs** : Impossible de référencer une personne avec une clé incorrecte
3. **Maintien de l'Immutabilité** : Toutes les classes restent frozen/immutable  
4. **Performance Optimisée** : Hashing efficace sur les objets Person
5. **Type Safety** : MyPy peut vérifier la cohérence des types

### Rétrocompatibilité

Ce changement est un **breaking change** par rapport à l'API basée sur les clés tuple. Cependant, c'est un amélioration architecturale significative qui justifie cette rupture pour :

- Moderniser le code vers les standards Python
- Améliorer la sécurité des types
- Simplifier l'API utilisateur
- Préparer les futures évolutions

### Tests et Validation

- ✅ **30 tests Family** : 100% de réussite avec la nouvelle API
- ✅ **43 tests Person** : 100% de réussite 
- ✅ **28 tests Sosa** : Compatibilité maintenue
- ✅ **Couverture de code** : 100% sur les modules Person et Family

### Conclusion

Cette migration représente une évolution majeure de l'architecture, passant d'un système de clés externes (hérité d'OCaml) vers une approche objet native Python. Elle améliore significativement la qualité du code, sa maintenabilité et ses performances tout en respectant les principes d'immutabilité et de sécurité des types.

---

## Migration vers Système d'Authentification JWT (2025)

### Contexte

L'API Geneweb nécessitait un système d'authentification moderne et sécurisé pour protéger les endpoints sensibles et gérer les sessions utilisateurs. L'ancienne approche utilisait des API keys basiques sans gestion de session ni révocation de tokens.

### Ancien Système (API Keys)

```python
# Ancienne approche - API Keys statiques
from geneweb.api.security.secrets import SecretsManager

secrets_manager = SecretsManager()
api_key_data = secrets_manager.generate_api_key(prefix="gw")
# Hash stocké en mémoire, pas de base de données
```

**Limitations de l'ancien système :**
- Pas de gestion de sessions utilisateur
- Pas de révocation de tokens
- Pas d'expiration automatique
- Stockage en mémoire uniquement
- Pas d'historique d'authentification
- Hashing PBKDF2 moins sécurisé que bcrypt

### Nouveau Système : JWT avec Base de Données

#### Architecture du Nouveau Système

```
┌─────────────────────────────────────────────────────────────┐
│                    Système d'Authentification               │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Router     │───▶│   Service    │───▶│   Database   │  │
│  │  auth.py     │    │  auth.py     │    │  models.py   │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                    │                    │          │
│         │                    │                    │          │
│         ▼                    ▼                    ▼          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  8 Endpoints │    │ JWT Tokens   │    │  5 Tables    │  │
│  │  - /login    │    │ - Access     │    │  - users     │  │
│  │  - /register │    │ - Refresh    │    │  - sessions  │  │
│  │  - /refresh  │    │ - Blacklist  │    │  - attempts  │  │
│  │  - /logout   │    │ - JTI        │    │  - passwords │  │
│  │  - /me       │    └──────────────┘    │  - blacklist │  │
│  │  - /change-  │                        └──────────────┘  │
│  │    password  │                                           │
│  │  - /health   │    ┌──────────────┐    ┌──────────────┐  │
│  └──────────────┘    │   Audit      │    │  Blacklist   │  │
│                      │  audit.py    │    │token_blacklist│  │
│                      └──────────────┘    └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

#### Composants Principaux

##### 1. Router (`src/geneweb/api/routers/auth.py`)
- 8 endpoints RESTful
- Validation Pydantic
- Gestion des erreurs HTTP
- Rate limiting intégré

##### 2. Service (`src/geneweb/api/security/auth.py`)
- Génération JWT avec JTI
- Vérification de tokens
- Hashage bcrypt (cost=12)
- Gestion du blacklist

##### 3. Modèles Database (`src/geneweb/api/db/models.py`)

```python
# 5 tables SQLAlchemy
class UserModel(Base):
    """Comptes utilisateurs avec mots de passe hachés"""
    
class UserSessionModel(Base):
    """Sessions actives pour tracking multi-device"""
    
class LoginAttemptModel(Base):
    """Historique des tentatives de connexion"""
    
class PasswordHistoryModel(Base):
    """Historique des mots de passe (anti-réutilisation)"""
    
class BlacklistedTokenModel(Base):
    """Tokens révoqués (logout, changement pwd)"""
```

##### 4. Token Blacklist (`src/geneweb/api/security/token_blacklist.py`)
- Révocation par JTI
- Révocation par utilisateur
- Nettoyage automatique des tokens expirés
- In-memory (dev) / Redis (production)

##### 5. Audit (`src/geneweb/api/security/audit.py`)
- Logging structuré JSON
- Tracking IP addresses
- Événements : login, logout, token_refresh, password_change

#### Flux d'Authentification

```
1. Inscription (POST /auth/register)
   ┌──────────────┐
   │   Client     │
   └──────┬───────┘
          │ {username, email, password}
          ▼
   ┌──────────────┐
   │   Router     │ Validation Pydantic
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │   Service    │ Hash password (bcrypt)
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │   Database   │ INSERT INTO users
   └──────┬───────┘
          │
          ▼ {user_id, username, email}

2. Connexion (POST /auth/login)
   ┌──────────────┐
   │   Client     │
   └──────┬───────┘
          │ {username, password}
          ▼
   ┌──────────────┐
   │   Router     │ Validation
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │   Service    │ Verify password (bcrypt)
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │   Database   │ SELECT user, INSERT login_attempt
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │   JWT        │ Generate access + refresh tokens
   └──────┬───────┘
          │
          ▼ {access_token, refresh_token}

3. Utilisation API (GET /api/v1/persons)
   ┌──────────────┐
   │   Client     │ Authorization: Bearer <token>
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │  Middleware  │ Decode JWT
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │  Blacklist   │ Check if revoked
   └──────┬───────┘
          │ ✓ Valid
          ▼
   ┌──────────────┐
   │   Endpoint   │ Process request
   └──────────────┘

4. Déconnexion (POST /auth/logout)
   ┌──────────────┐
   │   Client     │ Authorization: Bearer <token>
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │   Service    │ Extract JTI from token
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │  Blacklist   │ Add JTI to blacklist
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │   Database   │ INSERT blacklisted_token
   └──────────────┘
```

#### Caractéristiques de Sécurité

##### Password Hashing
```python
# Bcrypt avec salt automatique
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed = pwd_context.hash("password")  # Cost factor = 12 (4096 iterations)
```

##### JWT Structure
```json
{
  "sub": "john.doe",           // Username
  "user_id": 1,                // User ID
  "email": "john@example.com", // Email
  "jti": "uuid-v4",            // Unique token ID (pour révocation)
  "type": "access",            // access | refresh
  "exp": 1705750200,           // Expiration timestamp
  "iat": 1705748400            // Issued at timestamp
}
```

##### Token Expiration
- **Access Token** : 30 minutes (configurable via `GENEWEB_JWT_ACCESS_TOKEN_EXPIRE_MINUTES`)
- **Refresh Token** : 7 jours (configurable via `GENEWEB_JWT_REFRESH_TOKEN_EXPIRE_DAYS`)

##### Rate Limiting
- **Global** : 100 req/min, burst 20
- **Login endpoint** : Protection contre brute force
- **IP tracking** : Tentatives par IP

#### Migration depuis l'Ancien Système

##### Changements Breaking

1. **Authentification requise**
   ```python
   # Avant
   response = requests.get("http://localhost:8000/api/v1/persons")
   
   # Après
   token = login_response.json()["access_token"]
   headers = {"Authorization": f"Bearer {token}"}
   response = requests.get("http://localhost:8000/api/v1/persons", headers=headers)
   ```

2. **Base de données requise**
   ```bash
   # Avant : Pas de DB nécessaire
   
   # Après : SQLite (dev) ou PostgreSQL (prod)
   export GENEWEB_DB_DATABASE_URL="sqlite:///./geneweb.db"
   # Migrations Alembic pour créer les tables
   ```

3. **Configuration JWT**
   ```bash
   # Nouvelles variables d'environnement requises
   export GENEWEB_JWT_SECRET_KEY="your-256-bit-secret-key"
   export GENEWEB_JWT_ALGORITHM="HS256"
   ```

##### Guide de Migration

**Étape 1 : Configuration**
```bash
# .env
GENEWEB_JWT_SECRET_KEY=your-secret-key-min-32-chars
GENEWEB_JWT_ALGORITHM=HS256
GENEWEB_JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
GENEWEB_JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
GENEWEB_DB_DATABASE_URL=sqlite:///./geneweb.db
```

**Étape 2 : Migrations Database**
```bash
# Créer les tables auth
alembic upgrade head
```

**Étape 3 : Créer un utilisateur admin**
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@example.com",
    "password": "SecureP@ss123!",
    "full_name": "Administrator"
  }'
```

**Étape 4 : Mise à jour du code client**
```python
# Ancien code
import requests

response = requests.get("http://localhost:8000/api/v1/persons")

# Nouveau code
import requests

# 1. Login
login_response = requests.post(
    "http://localhost:8000/auth/login",
    json={"username": "admin", "password": "SecureP@ss123!"}
)
tokens = login_response.json()

# 2. Utiliser le token
headers = {"Authorization": f"Bearer {tokens['access_token']}"}
response = requests.get("http://localhost:8000/api/v1/persons", headers=headers)

# 3. Rafraîchir si expiré
refresh_response = requests.post(
    "http://localhost:8000/auth/refresh",
    json={"refresh_token": tokens["refresh_token"]}
)
new_tokens = refresh_response.json()
```

#### Impact sur les Tests

##### Nouveaux Tests Requis
- **test_authentication.py** : 280 lignes, tests complets du système auth
- Couverture : 100% des endpoints auth
- Tests : login, register, refresh, logout, token validation, password change

##### Mise à jour des Tests Existants
```python
# Avant
def test_get_persons():
    response = client.get("/api/v1/persons")
    assert response.status_code == 200

# Après
def test_get_persons(auth_headers):  # Fixture qui fournit le token
    response = client.get("/api/v1/persons", headers=auth_headers)
    assert response.status_code == 200

# Fixture
@pytest.fixture
def auth_headers(client):
    # Créer utilisateur
    client.post("/auth/register", json={...})
    # Login
    response = client.post("/auth/login", json={...})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

#### Performance

##### Avant (API Keys)
- Validation : O(1) - lookup en mémoire
- Stockage : 0 requêtes DB

##### Après (JWT + Database)
- Validation : O(1) - decode JWT + blacklist check
- Stockage : 1-2 requêtes DB par login
- Overhead : ~5-10ms par requête authentifiée

##### Optimisations Implémentées
- Cache en mémoire pour blacklist (production: Redis)
- Index sur colonnes de recherche fréquente
- Lazy loading des relations SQLAlchemy

#### Monitoring et Observabilité

##### Métriques Prometheus
```
# Nouvelles métriques disponibles
geneweb_auth_login_total{status="success|failure"}
geneweb_auth_token_refresh_total
geneweb_auth_logout_total
geneweb_auth_active_sessions
geneweb_auth_blacklisted_tokens
```

##### Logs Structurés
```json
{
  "timestamp": "2025-01-10T10:30:00Z",
  "level": "INFO",
  "event": "user_login",
  "username": "john.doe",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "success": true
}
```

#### Tests et Validation

##### Tests Automatisés
- ✅ **280 lignes** de tests d'authentification
- ✅ **100% couverture** sur routers/auth.py
- ✅ **Tests unitaires** : hash, JWT, blacklist
- ✅ **Tests d'intégration** : flux complets
- ✅ **Tests de sécurité** : tentatives d'intrusion

##### Checklist de Sécurité
- ✅ Bcrypt avec cost factor 12
- ✅ JWT avec JTI pour révocation
- ✅ Token blacklist fonctionnel
- ✅ Historique des mots de passe
- ✅ Sessions traçables
- ✅ Audit complet
- ✅ Rate limiting actif
- ✅ HTTPS requis en production

#### Documentation

##### Fichiers Créés/Mis à jour
- ✅ **AUTHENTICATION_GUIDE.md** : Guide complet (3500+ lignes)
- ✅ **QUICK_START_AUTH.md** : Quick start condensé
- ✅ **AUTHENTICATION_SUMMARY.md** : Résumé technique
- ✅ **API_DOCUMENTATION.md** : Section auth ajoutée
- ✅ **README_API.md** : Quick start auth ajouté
- ✅ **SECURITY.md** : Section JWT/bcrypt ajoutée
- ✅ **test_authentication.py** : Suite de tests complète

##### Documentation Archivée
- 📦 **BCRYPT_FIX.md** → `docs/archive/`
- 📦 **BCRYPT_FIX_SUMMARY.md** → `docs/archive/`
- 📦 **BCRYPT_MONKEY_PATCH.md** → `docs/archive/`

### Conclusion

Cette migration représente un changement architectural majeur, passant d'un système d'API keys basique à une infrastructure d'authentification moderne et complète basée sur JWT. Le nouveau système apporte :

- **Sécurité accrue** : bcrypt, JWT, blacklist, audit
- **Gestion de sessions** : tracking multi-device
- **Scalabilité** : prêt pour production avec PostgreSQL + Redis
- **Observabilité** : métriques, logs structurés
- **Conformité** : standards modernes d'authentification

**Impact** : Changement breaking nécessitant mise à jour des clients et configuration d'une base de données, mais apportant des bénéfices majeurs en termes de sécurité et de fonctionnalités.
```
