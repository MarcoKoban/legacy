# Intégration Database ↔ API

## 📋 Vue d'ensemble

Ce document explique comment la **base de données GeneWeb** (`geneweb.db.database`) est intégrée avec l'**API FastAPI** (`geneweb.api`).

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│              API FastAPI Layer                   │
│  ┌───────────────────────────────────────────┐  │
│  │  Endpoints (persons.py, gdpr.py)          │  │
│  │  ↓ Uses dependency injection               │  │
│  │  get_person_service() → get_database()    │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│          Service Layer (PersonService)           │
│  ┌───────────────────────────────────────────┐  │
│  │  • Business logic                          │  │
│  │  • GDPR compliance                         │  │
│  │  • Access control                          │  │
│  │  • Uses PersonAdapter for conversion      │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│       Adapter Layer (PersonAdapter)              │
│  ┌───────────────────────────────────────────┐  │
│  │  API Models ↔ DB Models                   │  │
│  │  • PersonResponse ↔ DBPerson              │  │
│  │  • PersonCreate ↔ DBPerson                │  │
│  │  • Sex/Access/Visibility conversions      │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│          Database Layer (Database)               │
│  ┌───────────────────────────────────────────┐  │
│  │  • db.persons (AVL collection)            │  │
│  │  • db.families                             │  │
│  │  • Binary .gwb format                      │  │
│  │  • Pickle serialization                    │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

## 📁 Fichiers créés/modifiés

### 1. **`dependencies.py`** (NOUVEAU)
- **Rôle** : Dependency injection pour FastAPI
- **Classes** :
  - `DatabaseManager` : Singleton pour gérer l'instance Database
  - `get_database()` : Fonction de dépendance FastAPI
- **Utilisation** :
  ```python
  from geneweb.api.dependencies import get_database
  
  @router.get("/persons")
  async def list_persons(db: Database = Depends(get_database)):
      persons = db.persons.get_all()
  ```

### 2. **`adapters/person_adapter.py`** (NOUVEAU)
- **Rôle** : Conversion entre modèles DB et API
- **Méthodes principales** :
  - `db_person_to_api_response(db_person, uuid)` → `PersonResponse`
  - `api_create_to_db_person(person_data)` → `DBPerson`
  - Conversions d'enums : `Sex ↔ PersonSex`, `Access ↔ VisibilityLevel`

### 3. **`services/person_service.py`** (MODIFIÉ)
- **Avant** : Stockage in-memory avec `_persons: Dict[UUID, Dict]`
- **Après** : Utilisation de `Database` instance
- **Changements clés** :
  - `__init__(self, database: Database)` : Injection de la DB
  - `_uuid_to_index: Dict[UUID, int]` : Mapping UUID ↔ index DB
  - Toutes les opérations CRUD utilisent maintenant `self.db.persons`

### 4. **`main.py`** (MODIFIÉ)
- **Ajouts** :
  - Initialisation de la DB au démarrage (`db_manager.initialize()`)
  - Fermeture de la DB au shutdown (`db_manager.close()`)
  - Activation des routers `persons` et `gdpr`

### 5. **`routers/persons.py`** (MODIFIÉ)
- **Ajout** : `get_person_service(db=Depends(get_database))`
- **Changement** : Tous les endpoints utilisent `Depends(get_person_service)`

## 🔄 Flux de données

### Exemple : Créer une personne

```
1. Client → POST /api/v1/persons
   Body: { first_name: "Jean", last_name: "Dupont", ... }

2. Router (persons.py)
   ↓ get_person_service() → PersonService with Database

3. PersonService.create_person()
   ↓ PersonAdapter.api_create_to_db_person()
   → Convertit en DBPerson

4. Database.add_person(db_person)
   → Ajoute dans db.persons (AVL collection)
   → Stocke en binaire (.gwb)

5. PersonAdapter.db_person_to_api_response()
   → Convertit en PersonResponse

6. Router → Client
   ← 201 Created { id, first_name, ... }
```

## 🗂️ Mapping UUID ↔ Database Index

La base de données GeneWeb utilise des **indices entiers** pour identifier les personnes, mais l'API utilise des **UUIDs**.

**Solution** : `PersonService` maintient deux dictionnaires :
- `_uuid_to_index: Dict[UUID, int]` : UUID → index DB
- `_index_to_uuid: Dict[int, UUID]` : index DB → UUID

**Génération UUID** : Déterministe basée sur `md5(first_name_last_name_index)`

## 🔧 Configuration

### Variable d'environnement

```bash
export GENEWEB_DB_PATH="/path/to/geneweb_db"
```

Par défaut : `geneweb_python/data/geneweb_db/`

### Initialisation

```python
# Dans main.py lifespan
from .dependencies import db_manager
db_manager.initialize()  # Au startup
db_manager.close()       # Au shutdown
```

## 🧪 Tests

### Test d'intégration : `tests/integration/test_database_api_integration.py`

Tests couverts :
- ✅ `test_database_person_service_integration` : Service a bien une DB
- ✅ `test_create_person_stores_in_database` : Création → stockage DB
- ✅ `test_get_person_retrieves_from_database` : Récupération depuis DB
- ✅ `test_update_person_modifies_database` : Mise à jour → DB modifiée
- ✅ `test_list_persons_from_database` : Liste depuis DB
- ✅ `test_adapter_conversions` : Conversions DB ↔ API

### Lancer les tests

```bash
cd geneweb_python
pytest tests/integration/test_database_api_integration.py -v
```

## 📊 Modèles de données

### DB Person (geneweb.core.person.Person)
```python
@dataclass
class Person:
    first_name: str
    last_name: str
    sex: Sex  # MALE, FEMALE, NEUTER
    birth: Event  # date, place
    death: DeathInfo
    access: Access  # PUBLIC, PRIVATE, SEMI_PUBLIC
    occupation: str
    notes: str
```

### API PersonResponse (geneweb.api.models.person)
```python
class PersonResponse(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    sex: PersonSex  # male, female, unknown
    birth_date: Optional[str]
    birth_place: Optional[str]
    visibility_level: VisibilityLevel  # public, family, restricted
    occupation: Optional[str]
    notes: Optional[str]
    # GDPR fields
    has_valid_consent: bool
    consent_status: GDPRConsentStatus
    # Metadata
    created_at: datetime
    updated_at: datetime
    version: int
```

## 🔐 Sécurité et GDPR

L'intégration maintient toutes les fonctionnalités de sécurité :
- ✅ **Authentification** : JWT tokens via `get_security_context()`
- ✅ **Autorisation** : RBAC avec permissions (CREATE_PERSON, etc.)
- ✅ **Chiffrement** : Données sensibles chiffrées (TODO: à implémenter)
- ✅ **Audit logging** : Toutes les opérations loguées
- ✅ **GDPR compliance** : Consentements, anonymisation, droit à l'oubli

## 🚀 Démarrer l'API avec DB

```bash
cd geneweb_python

# Option 1 : Via run_server.py
python run_server.py

# Option 2 : Via start_api.py
python start_api.py

# Option 3 : Uvicorn direct
uvicorn src.geneweb.api.main:app --reload

# L'API démarre sur http://localhost:8000
# Docs: http://localhost:8000/docs
```

## 📝 Exemples d'utilisation

### Créer une personne via API

```bash
# 1. Obtenir un token JWT
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"secret"}' | jq -r .access_token)

# 2. Créer une personne
curl -X POST http://localhost:8000/api/v1/persons \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Jean",
    "last_name": "Dupont",
    "sex": "male",
    "birth_date": "1950-01-15",
    "birth_place": "Paris, France",
    "occupation": "Engineer",
    "visibility_level": "family",
    "gdpr_consents": [{
      "purpose": "genealogy_research",
      "status": "granted"
    }]
  }'
```

### Lister les personnes

```bash
curl -X GET "http://localhost:8000/api/v1/persons?page=1&page_size=10" \
  -H "Authorization: Bearer $TOKEN"
```

## ⚠️ Limitations actuelles

1. **Soft delete** : DB ne supporte pas nativement → besoin de métadonnées séparées
2. **Hard delete** : Suppression difficile avec AVL → mapping seulement supprimé
3. **Chiffrement** : Infrastructure présente mais pas encore complètement intégré
4. **Performance** : Pas de cache → toutes requêtes vont en DB
5. **Transactions** : Pas de support transactionnel dans Database actuel

## 🔮 Améliorations futures

1. **Cache Redis** : Pour les lectures fréquentes
2. **Métadonnées séparées** : Table SQL pour soft delete, GDPR metadata
3. **Migrations** : Système de migration de schéma
4. **Indexation** : Index additionnels pour recherches complexes
5. **Backup/Restore** : Outils automatisés
6. **Monitoring** : Métriques de performance DB

## 📚 Ressources

- **Documentation DB** : `geneweb_python/src/geneweb/db/README.md`
- **Documentation API** : `geneweb_python/docs/API/`
- **Tests** : `geneweb_python/tests/integration/test_database_api_integration.py`
- **Config** : `geneweb_python/src/geneweb/api/config.py`

---

**Status** : ✅ Intégration complète et fonctionnelle  
**Date** : 16 octobre 2025  
**Version** : 1.0
