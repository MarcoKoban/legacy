# Geneweb Python Implementation

A Test-Driven Development (TDD) migration of the Geneweb genealogy software from OCaml to Python with **secure JWT authentication**.

## 🔐 New: Authentication System

The API now includes a **complete JWT-based authentication system**:

- ✅ **JWT Tokens** (Access + Refresh)
- ✅ **Bcrypt password hashing** (cost=12)
- ✅ **Token blacklist** for revocation
- ✅ **Session management** with audit logging
- ✅ **8 authentication endpoints**

> 📖 See [AUTHENTICATION_GUIDE.md](docs/AUTHENTICATION_GUIDE.md) for complete documentation

### Quick Authentication Example

```bash
# 1. Register
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "email": "user@example.com", "password": "SecureP@ss123!"}'

# 2. Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "SecureP@ss123!"}'

# Returns: {"access_token": "eyJ...", "refresh_token": "eyJ...", ...}

# 3. Use token
curl -X GET "http://localhost:8000/api/v1/persons" \
  -H "Authorization: Bearer eyJ..."
```

## Project Structure

```
geneweb_python/
├── src/                    # Source code
│   └── geneweb/           # Main package
│       ├── core/          # Core domain models (✅ Complete)
│       │   ├── person.py     # Person entities & relationships
│       │   ├── family.py     # Family structures & validation
│       │   ├── sosa.py       # Genealogical numbering system
│       │   ├── calendar.py   # Multi-calendar date system
│       │   ├── event.py      # Life events & timeline
│       │   ├── place.py      # Geographic data management
│       │   └── validation.py # Business rules validation
│       ├── api/          # REST API (✅ Complete with Auth)
│       │   ├── routers/      # API endpoints
│       │   │   └── auth.py   # 🆕 Authentication (8 endpoints)
│       │   ├── security/     # Security layer
│       │   │   ├── auth.py   # 🆕 JWT & password handling
│       │   │   └── token_blacklist.py  # 🆕 Token revocation
│       │   └── db/           # 🆕 Database models
│       │       ├── models.py     # User, Session, LoginAttempt
│       │       └── database.py   # SQLAlchemy config
│       ├── utils/         # Utility functions (🚧 Planned)
│       ├── web/          # Web interface (🚧 In Development)
│       └── db/           # Database layer (🚧 In Development)
├── tests/                 # Test suite (✅ 280+ tests auth)
│   ├── unit/             # Unit tests (220+ tests)
│   ├── integration/      # Integration tests (5 tests)
│   ├── e2e/              # End-to-end tests (8 prepared)
│   └── fixtures/         # Test data
├── docs/                 # Documentation
│   ├── AUTHENTICATION_GUIDE.md      # 🆕 Complete auth guide
│   ├── QUICK_START_AUTH.md          # 🆕 Quick start auth
│   ├── API/API_DOCUMENTATION.md     # ✅ Updated with auth
│   ├── README_API.md                # ✅ Updated with auth
│   └── SECURITY.md                  # ✅ Updated with JWT
└── htmlcov/              # Coverage reports
```

## TDD Development Process

This project follows strict Test-Driven Development:

1. **🔴 RED**: Write a failing test
2. **🟢 GREEN**: Write minimal code to pass
3. **🔵 REFACTOR**: Improve code quality

## Quick Start

### Setup Development Environment

**Option 1: Automatique (recommandée)**
```bash
# Tout-en-un : installe les dépendances + configure pre-commit
make dev-setup

# Vérifier que tout fonctionne
make test
```

**Option 2: Manuelle**
```bash
# Install development dependencies
pip install -e ".[dev]"

# Setup pre-commit hooks (required for automatic code quality checks)
# Note: This modifies your local .git/hooks/ and must be run once per clone
pre-commit install

# Run initial test suite
pytest
```

> **💡 Pourquoi `pre-commit install` ?**
> Pre-commit hooks modifient les hooks Git locaux (`.git/hooks/`) qui ne sont **pas versionnés**.
> Cette commande doit être exécutée une fois après avoir cloné le dépôt pour activer les
> vérifications automatiques de formatage, linting et tests avant chaque commit.
>
> **✨ Astuce**: Utilisez `make dev-setup` pour tout automatiser en une seule commande !
>
> 📖 **Guide complet** : [docs/PRECOMMIT_GUIDE.md](./docs/PRECOMMIT_GUIDE.md)

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m tdd           # TDD cycle tests

# Run tests in parallel
pytest -n auto
```

### Code Quality

```bash
# Format code
black src tests

# Sort imports
isort src tests

# Type checking
mypy src

# Linting
flake8 src tests
```

## Test Coverage Results

- **Current**: 238 tests (far exceeding original OCaml test plan)
- **Coverage**: 96% (exceeding 90% target)
- **Test Categories**:
  - Sosa: 25 tests (100% coverage)
  - Person: 38 tests (97% coverage)
  - Family: 34 tests (99% coverage)
  - Calendar: 39 tests (98% coverage)
  - Place: 11 tests (90% coverage)
  - Event: 15 tests (95% coverage)
  - Validation: 33 tests (88% coverage)
  - Relations: 10 tests (bidirectional)
  - Integration: 5 tests
  - E2E: 8 tests (skipped - awaiting web interface)

## Development Status

### ✅ Completed Modules
- [x] Project setup with TDD infrastructure
- [x] Core domain models (Person, Family, Sosa)
- [x] Sosa module (TDD) - 25 tests, 100% coverage
- [x] Person module (TDD) - 38 tests, 97% coverage
- [x] Family module (TDD) - 34 tests, 99% coverage
- [x] Calendar system (TDD) - 39 tests, 98% coverage
- [x] Event module (TDD) - 15 tests, 95% coverage
- [x] Place module (TDD) - 11 tests, 90% coverage
- [x] Validation engine (TDD) - 33 tests, 88% coverage
- [x] Bidirectional relationships - 10 tests
- [x] Integration testing - 5 tests

### 🚧 In Development
- [ ] Web interface (UI/UX)
- [ ] Database integration (persistence layer)
- [ ] REST API endpoints
- [ ] User authentication system

### 📋 Planned Features
- [ ] Wiki markup parser
- [ ] GEDCOM import/export
- [ ] Advanced search functionality
- [ ] Performance optimizations
- [ ] E2E workflow testing (8 tests prepared)

## Architectural Improvements

This Python implementation introduces several key improvements over the original OCaml codebase:

### Major Architectural Changes from OCaml

#### 1. Person Object Keys (Breaking Change)
**Previous (OCaml-style)**: Used tuple keys `(first_name, surname, occ)` to reference persons
```python
# Old approach
family = Family(
    father_key=("John", "Doe", 0),
    mother_key=("Jane", "Smith", 0),
    children_keys=[("Alice", "Doe", 0)]
)
```

**Current (Python-native)**: Use `Person` objects directly as keys
```python
# New approach - Person objects as keys
john = Person(first_name="John", surname="Doe", sex=Sex.MALE)
jane = Person(first_name="Jane", surname="Smith", sex=Sex.FEMALE)
alice = Person(first_name="Alice", surname="Doe", sex=Sex.FEMALE)

family = Family(
    father=[john],     # Parents as lists for flexibility
    mother=[jane],
    children=[alice]
)
```

#### 2. Flexible Parent Modeling
**Innovation**: Parents are now modeled as `Optional[List[Person]]` instead of `Optional[Person]` to support:
- Multiple father figures (biological, adoptive, step-parents)
- Multiple mother figures
- Complex family structures
- Future genealogical requirements

#### 3. Immutable Domain Objects
**Design Choice**: All core domain objects are immutable (frozen dataclasses):
```python
@dataclass(frozen=True, eq=True)
class Person:
    # Immutable person objects for data integrity

@dataclass(frozen=True, eq=True)
class Family:
    # Immutable family structures
```

#### 4. Comprehensive Validation Engine
**Innovation**: Integrated validation system with business rules:
```python
# Automatic validation with detailed error reporting
family.add_child(child, validate=True)  # Validates age gaps, relationships
person.validate_birth_death_dates()     # Ensures chronological consistency
```

**Benefits:**
- ✅ More pythonic and type-safe architecture
- ✅ Eliminates key-object inconsistencies
- ✅ Supports complex family structures
- ✅ Better performance with native object hashing
- ✅ Better IDE support and autocompletion
- ✅ Flexible parent modeling for real genealogy needs
- ✅ Immutable objects prevent accidental data corruption
- ✅ Comprehensive validation prevents invalid relationships
- ✅ Multi-calendar support for historical accuracy

See [ARCHITECTURAL_CHANGES.md](./ARCHITECTURAL_CHANGES.md) for detailed documentation.

## Contributing

### Development Workflow
1. All new features must be developed using TDD
2. Maintain 90%+ test coverage (currently at 96%)
3. Follow the existing test patterns and conventions
4. Run pre-commit hooks before committing
5. Ensure all existing tests pass before PR submission

### Code Quality Standards
- Type hints required for all public methods
- Docstrings for all classes and complex methods
- Black formatting and isort import sorting
- Mypy type checking without errors
- Test coverage must not decrease below current level

### Current Architecture Status
The core domain is complete and production-ready. Future development focuses on:
- Web interface development
- Database integration and persistence
- API endpoint implementation
- Performance optimization and caching
# Test pre-commit
