# Guide du Développeur - Geneweb Python

> **Guide complet pour les développeurs travaillant sur le projet Geneweb Python**

## 📋 Table des matières

1. [Introduction](#introduction)
2. [Setup de l'environnement](#setup-de-lenvironnement)
3. [Processus TDD (Test-Driven Development)](#processus-tdd)
4. [Workflow de développement](#workflow-de-développement)
5. [Standards de code](#standards-de-code)
6. [Pre-commit hooks](#pre-commit-hooks)
7. [Tests et couverture](#tests-et-couverture)
8. [Sécurité](#sécurité)
9. [Documentation](#documentation)
10. [Résolution de problèmes](#résolution-de-problèmes)

---

## Introduction

Geneweb Python est un projet de généalogie développé avec une approche **Test-Driven Development (TDD)** stricte. Ce guide explique comment contribuer au projet en respectant les standards et processus établis.

### Philosophie du projet

- ✅ **Tests d'abord** : On écrit les tests AVANT le code
- 🔒 **Sécurité par design** : Toutes les fonctionnalités incluent la sécurité dès le départ
- 📊 **Couverture élevée** : Objectif minimum de 90% de couverture de code
- 🎯 **Code propre** : Formatage automatique et validation stricte

---

## Setup de l'environnement

### 1. Prérequis

```bash
# Python 3.11 ou supérieur
python --version  # >= 3.11

# Git
git --version
```

### 2. Installation initiale

```bash
# Cloner le projet
git clone <repository-url>
cd geneweb_python

# Créer un environnement virtuel
python -m venv .venv

# Activer l'environnement virtuel
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows

# Installer les dépendances de développement
pip install -e ".[dev]"

# Configurer les pre-commit hooks
pre-commit install
```

### 3. Vérification de l'installation

```bash
# Lancer les tests pour vérifier que tout fonctionne
make test

# Devrait afficher : "589 passed, 8 skipped"
```

---

## Processus TDD

### Cycle TDD : Red-Green-Refactor

Le projet suit strictement le cycle TDD en 3 étapes :

```
🔴 RED → 🟢 GREEN → 🔵 REFACTOR
```

#### 🔴 ÉTAPE 1 : RED (Écrire un test qui échoue)

**TOUJOURS commencer par écrire un test**

```python
# tests/unit/test_example.py
import pytest
from mymodule import MyClass

class TestMyClass:
    """Test suite for MyClass"""

    def test_should_return_sum_of_two_numbers(self):
        """Test that add method returns sum of two numbers"""
        # ARRANGE
        calculator = MyClass()

        # ACT
        result = calculator.add(2, 3)

        # ASSERT
        assert result == 5
```

**Lancer le test :**
```bash
pytest tests/unit/test_example.py -v
# ❌ DOIT ÉCHOUER (le code n'existe pas encore)
```

#### 🟢 ÉTAPE 2 : GREEN (Écrire le code minimal)

**Écrire UNIQUEMENT le code nécessaire pour faire passer le test**

```python
# src/mymodule.py
class MyClass:
    """My calculator class"""

    def add(self, a: int, b: int) -> int:
        """Add two numbers"""
        return a + b
```

**Relancer le test :**
```bash
pytest tests/unit/test_example.py -v
# ✅ DOIT PASSER
```

#### 🔵 ÉTAPE 3 : REFACTOR (Améliorer le code)

**Améliorer le code sans casser les tests**

```python
# src/mymodule.py
from typing import Union

class MyClass:
    """Calculator with type hints and documentation"""

    def add(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """
        Add two numbers together.

        Args:
            a: First number
            b: Second number

        Returns:
            Sum of a and b

        Example:
            >>> calc = MyClass()
            >>> calc.add(2, 3)
            5
        """
        return a + b
```

**Relancer les tests :**
```bash
pytest tests/unit/test_example.py -v
# ✅ DOIT TOUJOURS PASSER
```

### Règles TDD strictes

❌ **JAMAIS :**
- Écrire du code de production sans test
- Écrire plus de code que nécessaire pour faire passer le test
- Skipper l'étape REFACTOR

✅ **TOUJOURS :**
- Écrire le test en premier
- Vérifier que le test échoue avant d'écrire le code
- Faire des commits petit à petit (un test à la fois)

---

## Workflow de développement

### Workflow Git standard

```bash
# 1. Créer une branche pour votre fonctionnalité
git checkout -b feature/ma-nouvelle-fonctionnalite

# 2. Développer en TDD (Red-Green-Refactor)
# ... écrire tests et code ...

# 3. Vérifier la qualité du code
make quality  # Format, lint, type-check

# 4. Lancer tous les tests
make test

# 5. Vérifier la couverture
make coverage
# Ouvrir htmlcov/index.html dans un navigateur

# 6. Commiter (les pre-commit hooks vont s'exécuter)
git add .
git commit -m "feat: add new feature with tests"

# 7. Push
git push origin feature/ma-nouvelle-fonctionnalite

# 8. Créer une Pull Request
```

### Exemple complet : Ajouter une nouvelle fonctionnalité

**Objectif** : Ajouter une méthode `multiply` à la classe `MyClass`

#### Étape 1 : Créer la branche
```bash
git checkout -b feature/add-multiply-method
```

#### Étape 2 : Écrire le test (RED)
```python
# tests/unit/test_example.py
def test_should_multiply_two_numbers(self):
    """Test that multiply method returns product"""
    calculator = MyClass()
    result = calculator.multiply(3, 4)
    assert result == 12
```

```bash
pytest tests/unit/test_example.py::TestMyClass::test_should_multiply_two_numbers -v
# ❌ ÉCHOUE : AttributeError: 'MyClass' object has no attribute 'multiply'
```

#### Étape 3 : Écrire le code minimal (GREEN)
```python
# src/mymodule.py
def multiply(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """Multiply two numbers"""
    return a * b
```

```bash
pytest tests/unit/test_example.py::TestMyClass::test_should_multiply_two_numbers -v
# ✅ PASSE
```

#### Étape 4 : Refactor (BLUE)
```python
# Ajouter documentation complète, gestion d'erreurs, etc.
def multiply(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """
    Multiply two numbers together.

    Args:
        a: First number
        b: Second number

    Returns:
        Product of a and b

    Raises:
        TypeError: If arguments are not numbers
    """
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("Arguments must be numbers")
    return a * b
```

#### Étape 5 : Ajouter tests de cas limites
```python
def test_multiply_with_zero(self):
    """Test multiply with zero"""
    calculator = MyClass()
    assert calculator.multiply(5, 0) == 0

def test_multiply_with_negative(self):
    """Test multiply with negative number"""
    calculator = MyClass()
    assert calculator.multiply(-3, 4) == -12

def test_multiply_raises_error_with_string(self):
    """Test multiply raises TypeError with string"""
    calculator = MyClass()
    with pytest.raises(TypeError):
        calculator.multiply("2", 3)
```

#### Étape 6 : Vérification finale
```bash
# Tous les tests
make test

# Couverture
make coverage

# Qualité du code
make quality
```

#### Étape 7 : Commit
```bash
git add tests/unit/test_example.py src/mymodule.py
git commit -m "feat: add multiply method with full test coverage"
```

---

## Standards de code

### Style de code

Le projet utilise :
- **Black** pour le formatage automatique
- **isort** pour trier les imports
- **flake8** pour le linting
- **mypy** pour la vérification de types

### Convention de nommage

```python
# Classes : PascalCase
class PersonService:
    pass

# Fonctions et méthodes : snake_case
def calculate_sosa_number():
    pass

# Constantes : UPPER_SNAKE_CASE
MAX_RETRY_COUNT = 3

# Variables privées : _prefixe
_internal_cache = {}

# Tests : test_should_describe_what_it_tests
def test_should_return_true_when_valid():
    pass
```

### Organisation des imports

```python
# 1. Imports standard library
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

# 2. Imports third-party
import pytest
from fastapi import FastAPI
from pydantic import BaseModel

# 3. Imports locaux
from geneweb.core.person import Person
from geneweb.core.family import Family
```

### Documentation (Docstrings)

Utiliser le format Google pour les docstrings :

```python
def create_person(first_name: str, surname: str, sex: Sex) -> Person:
    """
    Create a new person instance with validation.

    This function creates a person object and validates all required
    fields according to genealogy standards.

    Args:
        first_name: The person's first name (1-100 characters)
        surname: The person's family name (1-100 characters)
        sex: The person's biological sex (Sex enum)

    Returns:
        A validated Person instance

    Raises:
        ValueError: If names are empty or too long
        ValidationError: If data doesn't meet genealogy standards

    Example:
        >>> person = create_person("John", "Doe", Sex.MALE)
        >>> person.first_name
        'John'

    Note:
        All names are automatically sanitized to remove dangerous characters.
    """
    # Implementation here
    pass
```

---

## Pre-commit hooks

### Pourquoi `pre-commit install` est nécessaire ?

⚠️ **Important** : Les hooks Git sont stockés dans `.git/hooks/` qui n'est **pas versionné**.

**Raisons techniques :**
- `.git/hooks/` est local à chaque clone du dépôt
- Git ne synchronise pas ces fichiers (pour des raisons de sécurité)
- Chaque développeur doit installer les hooks manuellement

**Solution automatique :**
```bash
# Méthode recommandée (tout-en-un)
make dev-setup

# OU manuellement
pip install -e ".[dev]"
pre-commit install
```

### Configuration

Les pre-commit hooks s'exécutent automatiquement avant chaque commit.

```yaml
# .pre-commit-config.yaml (déjà configuré)
repos:
  - repo: https://github.com/psf/black
    hooks:
      - id: black

  - repo: https://github.com/pycqa/isort
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    hooks:
      - id: flake8

  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
```

### Que font les hooks ?

1. **black** : Reformate automatiquement votre code
2. **isort** : Trie vos imports
3. **flake8** : Vérifie les erreurs de style (PEP8)
4. **pytest** : Lance les tests avant le commit

### Tester manuellement les hooks

Avant de committer, vous pouvez tester manuellement les hooks :

#### Exécuter tous les hooks sur les fichiers modifiés
```bash
# Lance tous les hooks sur les fichiers staged
pre-commit run

# Exemple de sortie :
# black....................................................................Passed
# isort....................................................................Passed
# flake8...................................................................Passed
# pytest...................................................................Passed
```

#### Exécuter tous les hooks sur tous les fichiers
```bash
# Lance tous les hooks sur TOUS les fichiers du projet
pre-commit run --all-files

# Utile pour :
# - Vérifier tout le projet après une mise à jour des hooks
# - S'assurer qu'aucun fichier ne viole les règles
```

#### Exécuter un hook spécifique
```bash
# Tester uniquement black
pre-commit run black

# Tester uniquement flake8
pre-commit run flake8

# Tester uniquement isort
pre-commit run isort
```

#### Exécuter un hook sur des fichiers spécifiques
```bash
# Tester black sur un fichier spécifique
pre-commit run black --files src/geneweb/api/routers/health.py

# Tester tous les hooks sur plusieurs fichiers
pre-commit run --files src/geneweb/api/routers/*.py
```

#### Tester manuellement chaque outil

Vous pouvez aussi exécuter les outils directement :

```bash
# Black - formatter le code
black src/geneweb/api/routers/health.py
black --check src/  # Vérifier sans modifier

# isort - trier les imports
isort src/geneweb/api/routers/health.py
isort --check-only src/  # Vérifier sans modifier

# flake8 - linter
flake8 src/geneweb/api/routers/health.py
flake8 src/  # Tout le projet

# mypy - vérification de types
mypy src/geneweb/api/routers/health.py
mypy src/  # Tout le projet
```

#### Workflow recommandé

```bash
# 1. Pendant le développement : tester régulièrement
black src/geneweb/api/routers/health.py
flake8 src/geneweb/api/routers/health.py

# 2. Avant de stager : vérifier tout
pre-commit run --all-files

# 3. Après staging : vérification finale
git add src/geneweb/api/routers/health.py
pre-commit run

# 4. Commit (les hooks se lancent automatiquement)
git commit -m "feat: add health check endpoint"
```

### Si un hook échoue

```bash
# Les hooks ont reformaté vos fichiers
# Ajoutez-les à nouveau et recommitez
git add .
git commit -m "votre message"
```

### Bypasser les hooks (DÉCONSEILLÉ)

```bash
# Uniquement en cas d'urgence extrême
git commit --no-verify -m "emergency fix"

# ⚠️ N'utilisez JAMAIS --no-verify sans raison valable
```

---

## Tests et couverture

### Structure des tests

```
tests/
├── unit/              # Tests unitaires (fonctions isolées)
│   ├── test_person.py
│   ├── test_family.py
│   └── api/
│       ├── test_health_router.py
│       └── test_secrets.py
├── integration/       # Tests d'intégration (plusieurs composants)
│   └── test_genealogy_system.py
└── e2e/              # Tests end-to-end (workflow complet)
    └── test_workflows.py
```

### Commandes de test

```bash
# Tous les tests
make test

# Tests unitaires uniquement
make test-unit

# Tests d'intégration
make test-integration

# Tests E2E (skipped par défaut)
make test-e2e

# Tests rapides (sans E2E)
make test-fast

# Avec couverture HTML
make coverage
# Ouvrir htmlcov/index.html

# Tests en mode watch (relance automatiquement)
make test-watch

# Tests parallèles (plus rapide)
pytest -n auto
```

### Markers de tests

```python
import pytest

@pytest.mark.unit
def test_unit_example():
    """Test unitaire rapide"""
    pass

@pytest.mark.integration
def test_integration_example():
    """Test d'intégration"""
    pass

@pytest.mark.e2e
@pytest.mark.skip(reason="Requires web interface")
def test_e2e_example():
    """Test end-to-end"""
    pass

@pytest.mark.slow
def test_slow_example():
    """Test qui prend du temps"""
    pass
```

### Fixtures pytest

```python
# tests/conftest.py
import pytest
from geneweb.core.person import Person, Sex

@pytest.fixture
def sample_person():
    """Create a sample person for tests"""
    return Person(
        first_name="John",
        surname="Doe",
        sex=Sex.MALE
    )

# Utilisation dans un test
def test_person_age(sample_person):
    """Test using fixture"""
    assert sample_person.first_name == "John"
```

### Objectifs de couverture

| Module | Objectif | Actuel |
|--------|----------|--------|
| Core (person, family, sosa) | 95%+ | 97-100% ✅ |
| API Security | 90%+ | 96-99% ✅ |
| API Routers | 85%+ | 88% ✅ |
| Database | 90%+ | 96-100% ✅ |
| **Global** | **90%+** | **75%** 🔄 |

---

## Sécurité

### Principes de sécurité

1. **Validation des entrées** : Toujours valider et sanitizer
2. **Chiffrement** : Données sensibles toujours chiffrées
3. **Audit trail** : Logger toutes les actions critiques
4. **GDPR compliant** : Respect de la vie privée

### Exemple de code sécurisé

```python
from geneweb.api.security.validation import validate_and_sanitize_input
from geneweb.api.security.encryption import encrypt_sensitive_data
from geneweb.api.security.audit import audit_logger

async def create_person_secure(person_data: dict, user_id: str):
    """Create person with security checks"""

    # 1. Validation et sanitization
    validated_data = validate_and_sanitize_input(person_data)

    # 2. Chiffrement des données sensibles
    if "social_security_number" in validated_data:
        validated_data["social_security_number"] = encrypt_sensitive_data(
            validated_data["social_security_number"]
        )

    # 3. Création
    person = Person(**validated_data)

    # 4. Audit logging
    await audit_logger.log_person_created(
        user_id=user_id,
        person_id=person.id,
        action="CREATE_PERSON"
    )

    return person
```

### Checklist sécurité

Avant chaque commit :
- [ ] Toutes les entrées utilisateur sont validées
- [ ] Pas de données sensibles en clair
- [ ] Actions critiques loggées dans l'audit trail
- [ ] Tests de sécurité ajoutés (injection SQL, XSS, etc.)
- [ ] Pas de secrets hardcodés dans le code

---

## Documentation

### Types de documentation

1. **Docstrings** : Dans le code (obligatoire)
2. **README.md** : Vue d'ensemble du projet
3. **docs/** : Documentation détaillée
4. **Comments** : Pour la logique complexe uniquement

### Quand documenter

```python
# ✅ BON : Docstring claire et utile
def calculate_generation(sosa_number: int) -> int:
    """
    Calculate generation number from Sosa number.

    Sosa numbering: 1=root, 2-3=parents, 4-7=grandparents, etc.
    Generation = floor(log2(sosa)) + 1

    Args:
        sosa_number: Sosa number (must be positive)

    Returns:
        Generation number (1-based)
    """
    return sosa_number.bit_length()

# ❌ MAUVAIS : Commentaire inutile
def add(a, b):
    # Add a and b  <- INUTILE, le nom de fonction est clair
    return a + b

# ✅ BON : Commentaire pour logique complexe
def optimize_family_tree(tree):
    # Use AVL tree for O(log n) lookup instead of linear search
    # This is critical for performance with >10k persons
    return AVLTree(tree)
```

---

## Résolution de problèmes

### Tests qui échouent

```bash
# 1. Lancer le test spécifique en mode verbose
pytest tests/unit/test_example.py::TestMyClass::test_my_method -v

# 2. Voir les détails de l'échec
pytest tests/unit/test_example.py -v --tb=short

# 3. Débugger avec pdb
pytest tests/unit/test_example.py --pdb

# 4. Voir la sortie print
pytest tests/unit/test_example.py -s
```

### Problèmes de couverture

```bash
# Voir quelles lignes ne sont pas couvertes
make coverage
# Ouvrir htmlcov/index.html
# Cliquer sur le fichier pour voir les lignes en rouge

# Générer un rapport dans le terminal
pytest --cov=src --cov-report=term-missing
```

### Pre-commit hooks bloquent

```bash
# Voir ce qui bloque
git commit -m "test"

# Black a reformaté des fichiers
git add .
git commit -m "test"

# Erreur flake8 à corriger
# Corriger le code puis recommiter
```

### Conflits de dépendances

```bash
# Réinstaller l'environnement proprement
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

---

## Makefile - Commandes utiles

```bash
# Développement
make dev-setup      # Setup complet de l'environnement
make install        # Installer le package en mode dev

# Tests
make test          # Tous les tests
make test-fast     # Tests rapides (sans E2E)
make test-unit     # Tests unitaires uniquement
make test-watch    # Mode watch (auto-reload)
make coverage      # Rapport de couverture HTML

# Qualité de code
make format        # Formater avec black et isort
make lint          # Vérifier avec flake8
make type-check    # Vérifier les types avec mypy
make quality       # Tout : format + lint + type-check

# CI/CD
make ci-test       # Tests pour CI
make ci-quality    # Quality checks pour CI

# Nettoyage
make clean         # Nettoyer les fichiers temporaires
```

---

## Ressources supplémentaires

### Documentation officielle
- [Guide TDD complet](docs/TDD_GUIDE.md)
- [Standards de sécurité](SECURITY.md)
- [Guide API](docs/API/)

### Liens utiles
- [pytest documentation](https://docs.pytest.org/)
- [Black code style](https://black.readthedocs.io/)
- [Pydantic validation](https://docs.pydantic.dev/)
- [FastAPI](https://fastapi.tiangolo.com/)

### Obtenir de l'aide

1. Lire ce guide en premier
2. Consulter les exemples dans `tests/`
3. Chercher dans les issues GitHub
4. Demander sur le canal de développement

---

## Checklist avant Pull Request

- [ ] Tous les tests passent (`make test`)
- [ ] Couverture >= 90% pour les nouveaux fichiers
- [ ] Code formaté (`make format`)
- [ ] Pas d'erreurs de lint (`make lint`)
- [ ] Types vérifiés (`make type-check`)
- [ ] Documentation à jour (docstrings, README si nécessaire)
- [ ] Pas de `print()` ou `console.log()` oubliés
- [ ] Pas de `TODO` ou `FIXME` non tracés en issue
- [ ] Commit messages clairs (feat:, fix:, docs:, etc.)
- [ ] Branche à jour avec main

---

**Bon développement ! 🚀**

*Pour toute question, consultez les autres développeurs ou créez une issue.*
