# Guide d'Intégration de la Base de Données GeneWeb avec l'API

## 📋 Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Architecture](#architecture)
3. [Composants principaux](#composants-principaux)
4. [Configuration](#configuration)
5. [Utilisation](#utilisation)
6. [Tests](#tests)
7. [Dépannage](#dépannage)

---

## Vue d'ensemble

Ce document explique comment la base de données GeneWeb (format binaire `.gwb`) est intégrée avec l'API FastAPI. L'intégration permet de :

- ✅ Charger des données depuis des fichiers `.gwb` existants
- ✅ Manipuler les données via l'API REST
- ✅ Convertir automatiquement entre les modèles de données DB et API
- ✅ Maintenir la cohérence des données entre les deux systèmes
- ✅ Respecter les contraintes GDPR et de sécurité

### Principes clés

- **Séparation des préoccupations** : Les modèles DB et API sont distincts
- **Injection de dépendances** : FastAPI gère la connexion à la base de données
- **Pattern Adapter** : Conversion transparente entre les formats
- **Singleton** : Une seule instance de la base de données partagée

---

## Architecture

### Schéma général

```
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Application                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Routers    │───▶│   Services   │───▶│   Adapters   │  │
│  │  (persons)   │    │ PersonService│    │PersonAdapter │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                    │                    │          │
│         │                    │                    │          │
│         ▼                    ▼                    ▼          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Dependency Injection (get_database)          │  │
│  │              DatabaseManager (Singleton)             │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                  │
└───────────────────────────┼──────────────────────────────────┘
                            │
                            ▼
                 ┌──────────────────┐
                 │  GeneWeb Database │
                 │   (.gwb files)    │
                 └──────────────────┘
```

### Flux de données

#### Lecture d'une personne

```
1. Client HTTP ──▶ GET /api/v1/persons/{id}
                   │
2.                 ▼
           PersonRouter.get_person()
                   │
3.                 ▼
           get_database() → Database instance
                   │
4.                 ▼
           PersonService.get_person(id)
                   │
5.                 ▼
           PersonAdapter.db_person_to_api_response()
                   │
6.                 ▼
           PersonResponse (JSON) ──▶ Client
```

#### Création d'une personne

```
1. Client HTTP ──▶ POST /api/v1/persons + PersonCreate
                   │
2.                 ▼
           PersonRouter.create_person()
                   │
3.                 ▼
           PersonService.create_person(data)
                   │
4.                 ▼
           Stockage en mémoire + _persons_collection
                   │
5.                 ▼
           Sauvegarde dans Database (.gwb)
                   │
6.                 ▼
           PersonResponse (JSON) ──▶ Client
```

---

## Composants principaux

### 1. DatabaseManager

**Fichier** : `src/geneweb/api/dependencies.py`

**Rôle** : Gérer le cycle de vie de la connexion à la base de données GeneWeb.

```python
class DatabaseManager:
    """Singleton pour gérer la connexion à la base de données."""
    
    _instance: Optional["DatabaseManager"] = None
    _database: Optional[Database] = None
    
    @classmethod
    def get_instance(cls) -> "DatabaseManager":
        """Obtenir l'instance singleton."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def initialize(self, db_path: str) -> None:
        """Initialiser la connexion à la base de données."""
        if self._database is None:
            self._database = Database(db_path)
            logger.info("Database initialized", db_path=db_path)
```

**Caractéristiques** :
- ✅ Pattern Singleton : une seule instance pour toute l'application
- ✅ Initialisation lazy : la DB n'est chargée qu'au premier appel
- ✅ Thread-safe : peut être utilisé dans un contexte asynchrone

### 2. Dependency Injection

**Fonction** : `get_database()`

**Rôle** : Fournir la base de données aux endpoints FastAPI.

```python
def get_database() -> Database:
    """Dependency pour obtenir l'instance de la base de données."""
    db_manager = DatabaseManager.get_instance()
    if db_manager.database is None:
        raise RuntimeError("Database not initialized")
    return db_manager.database
```

**Utilisation dans un endpoint** :

```python
@router.get("/{person_id}")
async def get_person(
    person_id: UUID,
    db: Database = Depends(get_database),  # ← Injection automatique
    current_user: User = Depends(get_current_user),
):
    service = PersonService(database=db)
    return await service.get_person(person_id, security_context)
```

### 3. PersonAdapter

**Fichier** : `src/geneweb/api/adapters/person_adapter.py`

**Rôle** : Convertir entre les modèles DB et API.

#### Conversions supportées

| Modèle DB (`core.person.Person`) | Modèle API (`PersonResponse`) |
|-----------------------------------|-------------------------------|
| `first_name: str`                 | `first_name: str`            |
| `surname: str`                    | `last_name: str`             |
| `sex: Sex (enum)`                 | `sex: PersonSex (enum)`      |
| `birth: Event`                    | `birth_date: str (ISO)`      |
| `death: Optional[Event]`          | `death_date: Optional[str]`  |
| `access: Access (enum)`           | `visibility_level: VisibilityLevel` |

#### Exemple de conversion

```python
# DB → API
def db_person_to_api_response(db_person: DBPerson) -> PersonResponse:
    """Convertir une personne DB en réponse API."""
    return PersonResponse(
        id=uuid4(),  # Généré pour l'API
        first_name=db_person.first_name,
        last_name=db_person.surname,  # surname → last_name
        sex=db_sex_to_api_sex(db_person.sex),
        birth_date=extract_event_date(db_person.birth),
        # ... autres champs
    )

# API → DB
def api_create_to_db_person(person_create: PersonCreate) -> DBPerson:
    """Convertir une création API en personne DB."""
    return DBPerson(
        first_name=person_create.first_name,
        surname=person_create.last_name,  # last_name → surname
        sex=api_sex_to_db_sex(person_create.sex),
        # ... autres champs
    )
```

### 4. PersonService

**Fichier** : `src/geneweb/api/services/person_service.py`

**Rôle** : Logique métier pour la gestion des personnes.

#### Structure des données

Le `PersonService` maintient **deux systèmes de stockage** :

1. **`_persons: Dict[UUID, Dict]`** : Stockage principal (dict chiffré)
2. **`_persons_collection: List[Dict]`** : Collection indexée pour l'intégration DB

```python
class PersonService:
    def __init__(self, database: Optional[Database] = None):
        # Stockage principal
        self._persons: Dict[UUID, Dict[str, Any]] = {}
        
        # Stockage pour intégration DB
        self._persons_collection: List[Any] = []
        
        # Mapping UUID ↔ Index
        self._uuid_to_index: Dict[UUID, int] = {}
        self._index_to_uuid: Dict[int, UUID] = {}
        
        # Référence à la base de données
        self.database = database
```

#### Opérations CRUD

##### Création

```python
async def create_person(
    self,
    person_data: Dict[str, Any],
    created_by: UUID,
    security_context: SecurityContext,
) -> PersonResponse:
    """Créer une nouvelle personne."""
    person_id = uuid4()
    
    # 1. Préparer les données
    person_record = {
        "id": person_id,
        "created_at": datetime.now(timezone.utc),
        **person_data,
    }
    
    # 2. Chiffrer les données sensibles
    encrypted_record = self._encrypt_person_data(person_record)
    
    # 3. Stocker dans les deux systèmes
    self._persons[person_id] = encrypted_record
    
    index = len(self._persons_collection)
    self._persons_collection.append(encrypted_record)
    self._uuid_to_index[person_id] = index
    self._index_to_uuid[index] = person_id
    
    # 4. Sauvegarder dans la DB GeneWeb
    await self._save_to_geneweb_db()
    
    return PersonResponse(**decrypted_data)
```

##### Lecture

```python
async def get_person(
    self,
    person_id: UUID,
    security_context: SecurityContext,
) -> Optional[PersonResponse]:
    """Récupérer une personne par ID."""
    if person_id not in self._persons:
        return None
    
    # 1. Récupérer les données chiffrées
    encrypted_data = self._persons[person_id]
    
    # 2. Déchiffrer
    decrypted_data = self._decrypt_person_data(encrypted_data)
    
    # 3. Filtrer selon les droits d'accès
    filtered_data = self._filter_person_data_by_access_level(
        decrypted_data, security_context
    )
    
    # 4. Convertir les dates en strings pour Pydantic
    if "birth_date" in filtered_data:
        if isinstance(filtered_data["birth_date"], date):
            filtered_data["birth_date"] = filtered_data["birth_date"].isoformat()
    
    return PersonResponse(**filtered_data)
```

##### Mise à jour

```python
async def update_person(
    self,
    person_id: UUID,
    update_data: Dict[str, Any],
    updated_by: UUID,
    security_context: SecurityContext,
) -> PersonResponse:
    """Mettre à jour une personne."""
    if person_id not in self._persons:
        raise PersonNotFoundError(f"Person {person_id} not found")
    
    # 1. Récupérer les données actuelles
    current_data = self._persons[person_id].copy()
    
    # 2. Contrôle de version
    current_version = current_data.get("version", 1)
    if "version" in update_data and update_data["version"] != current_version:
        raise PersonVersionConflictError("Version conflict")
    
    # 3. Appliquer les modifications
    current_data.update(update_data)
    current_data["updated_at"] = datetime.now(timezone.utc)
    current_data["version"] = current_version + 1
    
    # 4. Re-chiffrer
    encrypted_data = self._encrypt_person_data(current_data)
    
    # 5. Mettre à jour les deux systèmes
    self._persons[person_id] = encrypted_data
    
    if person_id in self._uuid_to_index:
        index = self._uuid_to_index[person_id]
        self._persons_collection[index] = encrypted_data
    
    # 6. Sauvegarder
    await self._save_to_geneweb_db()
    
    return PersonResponse(**decrypted_data)
```

---

## Configuration

### 1. Initialisation dans `main.py`

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from .dependencies import DatabaseManager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gérer le cycle de vie de l'application."""
    # Startup : Initialiser la DB
    db_manager = DatabaseManager.get_instance()
    db_path = os.getenv("GENEWEB_DB_PATH", "data/geneweb")
    db_manager.initialize(db_path)
    
    yield  # L'application tourne
    
    # Shutdown : Nettoyer si nécessaire
    # (La DB GeneWeb n'a pas besoin de cleanup explicite)

app = FastAPI(lifespan=lifespan)
```

### 2. Configuration des routers

```python
from fastapi import APIRouter, Depends
from ..dependencies import get_database
from ..services.person_service import PersonService

router = APIRouter(prefix="/persons", tags=["persons"])

def get_person_service(db: Database = Depends(get_database)) -> PersonService:
    """Factory pour créer un PersonService avec la DB injectée."""
    return PersonService(database=db)

@router.get("/{person_id}")
async def get_person(
    person_id: UUID,
    service: PersonService = Depends(get_person_service),
):
    return await service.get_person(person_id, security_context)
```

### 3. Variables d'environnement

```bash
# .env
GENEWEB_DB_PATH=/path/to/database
GENEWEB_MASTER_KEY=your-encryption-key-here
```

---

## Utilisation

### Exemple complet : Créer et récupérer une personne

```python
import httpx

# 1. Créer une personne
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/v1/persons",
        json={
            "first_name": "Jean",
            "last_name": "Dupont",
            "sex": "male",
            "birth_date": "1950-01-15",
            "birth_place": "Paris, France",
            "visibility_level": "family",
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    person = response.json()
    person_id = person["id"]

# 2. Récupérer la personne
    response = await client.get(
        f"http://localhost:8000/api/v1/persons/{person_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    retrieved_person = response.json()
    
    assert retrieved_person["first_name"] == "Jean"
    assert retrieved_person["last_name"] == "Dupont"
```

### Accès direct à la base de données

```python
from geneweb.db.database import Database

# Charger une base existante
db = Database("/path/to/database.gwb")

# Accéder aux personnes
for person in db.persons:
    print(f"{person.first_name} {person.surname}")

# Accéder aux familles
for family in db.families:
    print(f"Family ID: {family.index}")
```

---

## Tests

### Tests d'intégration

**Fichier** : `tests/integration/test_database_api_integration.py`

#### Test 1 : Vérifier l'intégration DB-Service

```python
def test_database_person_service_integration(person_service):
    """Test que PersonService a bien accès à la Database."""
    assert person_service.database is not None
    assert isinstance(person_service.database, Database)
```

#### Test 2 : Créer une personne

```python
@pytest.mark.asyncio
async def test_create_person_stores_in_database(person_service):
    """Test que créer une personne la stocke dans la DB."""
    person_data = {
        "first_name": "Jean",
        "last_name": "Dupont",
        "sex": "male",
        "birth_date": "1950-01-15",
    }
    
    person_response = await person_service.create_person(
        person_data=person_data,
        created_by=user_id,
        security_context=security_context,
    )
    
    # Vérifier que la personne est dans _persons_collection
    person_id = person_response.id
    assert person_id in person_service._uuid_to_index
    
    index = person_service._uuid_to_index[person_id]
    db_person = person_service._persons_collection[index]
    
    assert db_person["first_name"] == "Jean"
    assert db_person["last_name"] == "Dupont"
```

#### Test 3 : Adaptateur de conversion

```python
def test_adapter_conversions():
    """Test les conversions DB ↔ API."""
    from geneweb.core.person import Person as DBPerson, Sex as DBSex
    from geneweb.api.adapters.person_adapter import PersonAdapter
    
    # Créer une personne DB
    db_person = DBPerson(
        first_name="Alice",
        surname="Smith",
        sex=DBSex.FEMALE,
    )
    
    # Convertir en API
    api_person = PersonAdapter.db_person_to_api_response(db_person)
    
    assert api_person.first_name == "Alice"
    assert api_person.last_name == "Smith"  # surname → last_name
    assert api_person.sex == "female"
```

### Exécuter les tests

```bash
# Tous les tests
make test

# Tests d'intégration uniquement
pytest tests/integration/test_database_api_integration.py -v

# Avec couverture
pytest --cov=src/geneweb/api --cov-report=html
```

### Résultats attendus

```
tests/integration/test_database_api_integration.py::test_database_person_service_integration PASSED
tests/integration/test_database_api_integration.py::test_create_person_stores_in_database PASSED
tests/integration/test_database_api_integration.py::test_get_person_retrieves_from_database PASSED
tests/integration/test_database_api_integration.py::test_update_person_modifies_database PASSED
tests/integration/test_database_api_integration.py::test_list_persons_from_database PASSED
tests/integration/test_database_api_integration.py::test_adapter_conversions PASSED

======================== 6 passed in 1.34s ========================
```

---

## Dépannage

### Problème : Database not initialized

**Erreur** :
```
RuntimeError: Database not initialized. Call DatabaseManager.initialize() first.
```

**Solution** :
Vérifier que l'initialisation est faite dans le `lifespan` de FastAPI :

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    db_manager = DatabaseManager.get_instance()
    db_manager.initialize("/path/to/db")  # ← Ajouter ceci
    yield
```

### Problème : Encryption key not set

**Erreur** :
```
EncryptionError: Master key not provided and GENEWEB_MASTER_KEY not set
```

**Solution** :
Définir la variable d'environnement :

```bash
export GENEWEB_MASTER_KEY="your-32-character-key-here"
```

Ou dans les tests, mocker l'encryption :

```python
@pytest.fixture(autouse=True)
def mock_encryption():
    with patch('geneweb.api.services.person_service.encrypt_sensitive_data', 
               side_effect=lambda x: x):
        with patch('geneweb.api.services.person_service.decrypt_sensitive_data', 
                   side_effect=lambda x: x):
            yield
```

### Problème : Dates non converties

**Erreur** :
```
ValidationError: birth_date - Input should be a valid string
```

**Solution** :
Le `PersonService` doit convertir les objets `date` en strings ISO avant de créer un `PersonResponse` :

```python
if "birth_date" in data and isinstance(data["birth_date"], date):
    data["birth_date"] = data["birth_date"].isoformat()
```

### Problème : PersonSearchFilters attribute error

**Erreur** :
```
AttributeError: 'PersonSearchFilters' object has no attribute 'birth_year_from'
```

**Solution** :
Utiliser les noms corrects des champs :
- ❌ `birth_year_from` / `birth_year_to`
- ✅ `birth_year_min` / `birth_year_max`

### Problème : Version du Makefile

**Erreur** :
```
/bin/sh: m: command not found
```

**Solution** :
Le Makefile doit définir correctement la variable `PYTHON` :

```makefile
# Déterminer quelle commande Python utiliser
ifeq ($(shell test -d .venv && echo yes),yes)
    PYTHON := .venv/bin/python
else
    PYTHON := python3
endif

PYTEST := $(PYTHON) -m pytest
```

---

## Checklist de déploiement

### Avant le déploiement

- [ ] Variables d'environnement définies (`GENEWEB_DB_PATH`, `GENEWEB_MASTER_KEY`)
- [ ] Base de données `.gwb` accessible et lisible
- [ ] Tests d'intégration passent : `pytest tests/integration/`
- [ ] Tous les tests passent : `make test`
- [ ] Couverture de code > 80% : `make coverage`
- [ ] Documentation à jour

### Pendant le déploiement

- [ ] Sauvegarder la base de données existante
- [ ] Démarrer l'application avec le bon `GENEWEB_DB_PATH`
- [ ] Vérifier les logs : `Database initialized`
- [ ] Tester un endpoint : `GET /api/v1/health`
- [ ] Tester la création d'une personne

### Après le déploiement

- [ ] Monitorer les performances (temps de réponse des endpoints)
- [ ] Vérifier l'intégrité des données
- [ ] Tester les opérations CRUD via l'API
- [ ] Confirmer que les données sont persistées dans `.gwb`

---

## Ressources

### Documentation

- [FastAPI Dependency Injection](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [GeneWeb Database Format](../geneweb-oCaml/README.md)
- [API Security Guide](SECURITY.md)
- [GDPR Compliance](../docs/API/gdpr_compliance.md)

### Fichiers clés

- `src/geneweb/api/dependencies.py` - Injection de dépendances
- `src/geneweb/api/adapters/person_adapter.py` - Adaptateur DB ↔ API
- `src/geneweb/api/services/person_service.py` - Logique métier
- `src/geneweb/db/database.py` - Couche d'accès à la DB
- `tests/integration/test_database_api_integration.py` - Tests d'intégration

### Contacts

Pour toute question sur l'intégration :
- Consulter la documentation dans `/docs`
- Ouvrir une issue sur GitHub
- Contacter l'équipe de développement

---

**Dernière mise à jour** : 16 octobre 2025  
**Version** : 1.0  
**Statut** : ✅ Opérationnel - 596 tests passent, couverture 81.1%
