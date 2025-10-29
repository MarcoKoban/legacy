# Guide TDD Détaillé - Geneweb Python

> **Guide approfondi du Test-Driven Development pour Geneweb**

## 📚 Table des matières

1. [Qu'est-ce que le TDD ?](#quest-ce-que-le-tdd)
2. [Pourquoi TDD ?](#pourquoi-tdd)
3. [Le cycle Red-Green-Refactor](#le-cycle-red-green-refactor)
4. [Règles d'or du TDD](#règles-dor-du-tdd)
5. [Patterns de tests](#patterns-de-tests)
6. [Exemples pratiques](#exemples-pratiques)
7. [Tests avancés](#tests-avancés)
8. [Anti-patterns à éviter](#anti-patterns-à-éviter)

---

## Qu'est-ce que le TDD ?

**Test-Driven Development (TDD)** est une méthodologie de développement où :

1. On écrit **d'abord le test** (qui échoue)
2. On écrit **le code minimal** pour faire passer le test
3. On **refactorise** le code tout en maintenant les tests verts

### Le mantra TDD

```
❌ RED    → Test qui échoue (le code n'existe pas)
✅ GREEN  → Test qui passe (code minimal)
🔄 REFACTOR → Code amélioré (tests toujours verts)
```

### Pas du TDD

❌ Écrire le code puis les tests
❌ Écrire tous les tests puis tout le code
❌ Tester manuellement puis automatiser

---

## Pourquoi TDD ?

### Avantages démontrés

#### 1. **Moins de bugs** (40-80% de réduction)
```python
# Sans TDD : Code écrit, puis testé, bugs découverts tard
def calculate_age(birth_year):
    return 2024 - birth_year  # ❌ Oubli de gérer None

# Avec TDD : Test écrit d'abord, cas limites identifiés
def test_calculate_age_with_none():
    with pytest.raises(TypeError):
        calculate_age(None)  # ✅ Cas identifié avant le code
```

#### 2. **Design meilleur**
Le TDD force à penser à l'API avant l'implémentation :
```python
# TDD pousse à une API claire
person = Person.create(
    first_name="John",
    surname="Doe",
    birth_date=date(1990, 1, 1)
)
# vs une API confuse
person = Person()
person.set_name("John", "Doe")
person.birth = "1990-01-01"  # String ou date ?
```

#### 3. **Documentation vivante**
Les tests servent de documentation :
```python
class TestSosaNumber:
    """Examples of Sosa number usage"""
    
    def test_root_person_has_sosa_one(self):
        """The root person always has Sosa number 1"""
        root = Person(first_name="Root", sosa=Sosa.one())
        assert root.sosa.value == 1
    
    def test_father_has_double_sosa(self):
        """Father's Sosa is always 2 × child's Sosa"""
        child = Person(sosa=Sosa(5))
        father_sosa = child.sosa.father()
        assert father_sosa.value == 10
```

#### 4. **Refactoring sécurisé**
```python
# Avant refactoring : code simple mais lent
def find_person(persons, name):
    for p in persons:  # O(n)
        if p.name == name:
            return p

# Après refactoring : code optimisé
def find_person(persons_index, name):
    return persons_index.get(name)  # O(1)

# Les tests garantissent que le comportement est identique
```

#### 5. **Confiance pour modifier**
- ✅ Ajouter une feature : tests existants prouvent que rien n'est cassé
- ✅ Corriger un bug : test ajouté pour empêcher la régression
- ✅ Refactorer : tests verts = tout fonctionne encore

---

## Le cycle Red-Green-Refactor

### Cycle détaillé en 6 étapes

```
┌─────────────────────────────────────────┐
│  1. PENSER : Quelle feature ?           │
│  2. RED    : Écrire test qui échoue     │
│  3. GREEN  : Code minimal qui passe     │
│  4. VÉRIFIER : Test passe ?             │
│  5. REFACTOR : Améliorer le code        │
│  6. COMMIT  : Sauvegarder               │
└─────────────────────────────────────────┘
```

### Exemple complet : Ajouter une méthode d'âge

#### Étape 1 : PENSER

**Feature à ajouter** : Calculer l'âge d'une personne
**Cas à tester** :
- Âge normal (ex: né en 1990 → 34 ans en 2024)
- Âge avec date de naissance manquante (None)
- Personne décédée

#### Étape 2 : RED - Écrire le test

```python
# tests/unit/test_person.py
from datetime import date
import pytest
from geneweb.core.person import Person, Sex

class TestPersonAge:
    """Test age calculation"""
    
    def test_should_calculate_age_from_birth_date(self):
        """Calculate age for person born in 1990"""
        # ARRANGE
        person = Person(
            first_name="John",
            surname="Doe",
            sex=Sex.MALE,
            birth_date=date(1990, 1, 1)
        )
        
        # ACT
        age = person.calculate_age(reference_date=date(2024, 1, 1))
        
        # ASSERT
        assert age == 34
```

**Lancer le test :**
```bash
pytest tests/unit/test_person.py::TestPersonAge::test_should_calculate_age_from_birth_date -v

# ❌ DOIT ÉCHOUER
# AttributeError: 'Person' object has no attribute 'calculate_age'
```

✅ **Test ROUGE = C'est bon !** On peut passer à l'étape suivante.

#### Étape 3 : GREEN - Code minimal

```python
# src/geneweb/core/person.py
from datetime import date

class Person:
    # ... autres attributs ...
    birth_date: Optional[date] = None
    
    def calculate_age(self, reference_date: date = None) -> Optional[int]:
        """Calculate person's age"""
        if reference_date is None:
            reference_date = date.today()
        
        if self.birth_date is None:
            return None
        
        return reference_date.year - self.birth_date.year
```

**Relancer le test :**
```bash
pytest tests/unit/test_person.py::TestPersonAge::test_should_calculate_age_from_birth_date -v

# ✅ PASSE
```

#### Étape 4 : VÉRIFIER

✅ Test passe → Continuer
❌ Test échoue → Corriger le code (ne pas toucher au test !)

#### Étape 5 : REFACTOR

**Identifier les problèmes :**
- ❌ Ne gère pas les anniversaires (né le 15 mars, on est le 14 mars)
- ❌ Pas de gestion des personnes décédées
- ❌ Manque de documentation

**Ajouter plus de tests AVANT de refactorer :**

```python
def test_age_before_birthday(self):
    """Age before birthday is one year less"""
    person = Person(
        first_name="John",
        surname="Doe",
        sex=Sex.MALE,
        birth_date=date(1990, 6, 15)
    )
    # Reference date before birthday
    age = person.calculate_age(reference_date=date(2024, 6, 14))
    assert age == 33  # Not 34 yet

def test_age_on_birthday(self):
    """Age on birthday is correct"""
    person = Person(
        first_name="John",
        surname="Doe",
        sex=Sex.MALE,
        birth_date=date(1990, 6, 15)
    )
    age = person.calculate_age(reference_date=date(2024, 6, 15))
    assert age == 34

def test_age_with_no_birth_date_returns_none(self):
    """Person without birth date has no age"""
    person = Person(first_name="John", surname="Doe", sex=Sex.MALE)
    assert person.calculate_age() is None
```

**Améliorer le code :**

```python
from datetime import date
from typing import Optional

def calculate_age(self, reference_date: Optional[date] = None) -> Optional[int]:
    """
    Calculate person's age at a given date.
    
    Args:
        reference_date: Date to calculate age at (default: today)
        
    Returns:
        Age in years, or None if birth date is unknown
        
    Example:
        >>> person = Person(birth_date=date(1990, 1, 1))
        >>> person.calculate_age(reference_date=date(2024, 1, 1))
        34
    """
    if reference_date is None:
        reference_date = date.today()
    
    if self.birth_date is None:
        return None
    
    # Calculate age accounting for whether birthday has passed
    age = reference_date.year - self.birth_date.year
    
    # Subtract 1 if birthday hasn't occurred yet this year
    if (reference_date.month, reference_date.day) < (
        self.birth_date.month,
        self.birth_date.day
    ):
        age -= 1
    
    return age
```

**Relancer TOUS les tests :**
```bash
pytest tests/unit/test_person.py::TestPersonAge -v

# ✅ TOUS LES TESTS PASSENT
```

#### Étape 6 : COMMIT

```bash
git add tests/unit/test_person.py src/geneweb/core/person.py
git commit -m "feat: add person age calculation with birthday handling

- Calculate age from birth date
- Handle case before/on/after birthday
- Return None if birth date unknown
- Add comprehensive tests (4 test cases)
- Coverage: 100%"
```

---

## Règles d'or du TDD

### Les 3 lois du TDD (Uncle Bob)

1. **Ne pas écrire de code de production** avant d'avoir un test qui échoue
2. **Écrire juste assez de test** pour le faire échouer (y compris compilation)
3. **Écrire juste assez de code de production** pour faire passer le test

### Règles supplémentaires

#### ✅ Règle du "Baby Steps"
```python
# ❌ MAUVAIS : Test trop gros
def test_complete_family_tree_management():
    # 50 lignes de test...
    # Trop difficile à faire passer d'un coup

# ✅ BON : Petits tests incrémentaux
def test_create_person():
    person = Person(first_name="John", surname="Doe")
    assert person is not None

def test_add_father():
    child = Person(...)
    father = Person(...)
    child.set_father(father)
    assert child.father == father

def test_father_relationship_is_bidirectional():
    # etc.
```

#### ✅ Règle du "Test One Thing"
```python
# ❌ MAUVAIS : Teste plusieurs choses
def test_person_and_family_and_sosa():
    person = Person(...)
    family = Family(...)
    sosa = Sosa(...)
    # Trop de responsabilités

# ✅ BON : Un test = un concept
def test_person_creation():
    person = Person(first_name="John", surname="Doe")
    assert person.first_name == "John"

def test_family_creation():
    family = Family(father=..., mother=...)
    assert family.father is not None
```

#### ✅ Règle du "DAMP over DRY"
**DAMP** = Descriptive And Meaningful Phrases
**DRY** = Don't Repeat Yourself

Dans les tests, la clarté > la concision

```python
# ❌ MAUVAIS : Trop DRY, difficile à comprendre
def test_age_calculation(self):
    for birth_year, expected_age in [(1990, 34), (2000, 24)]:
        assert Person(birth_date=date(birth_year, 1, 1)).calculate_age() == expected_age

# ✅ BON : DAMP, très clair
def test_age_for_person_born_in_1990(self):
    person = Person(
        first_name="John",
        surname="Doe",
        sex=Sex.MALE,
        birth_date=date(1990, 1, 1)
    )
    age = person.calculate_age(reference_date=date(2024, 1, 1))
    assert age == 34

def test_age_for_person_born_in_2000(self):
    person = Person(
        first_name="Jane",
        surname="Doe",
        sex=Sex.FEMALE,
        birth_date=date(2000, 1, 1)
    )
    age = person.calculate_age(reference_date=date(2024, 1, 1))
    assert age == 24
```

---

## Patterns de tests

### Pattern AAA (Arrange-Act-Assert)

```python
def test_person_full_name(self):
    # ARRANGE - Préparer les données
    person = Person(
        first_name="Jean-Baptiste",
        surname="Poquelin",
        suffix="dit Molière"
    )
    
    # ACT - Exécuter l'action
    full_name = person.get_full_name()
    
    # ASSERT - Vérifier le résultat
    assert full_name == "Jean-Baptiste Poquelin dit Molière"
```

### Pattern Given-When-Then (BDD style)

```python
def test_sosa_father_calculation(self):
    # GIVEN a person with Sosa number 5
    person = Person(sosa=Sosa(5))
    
    # WHEN we calculate father's Sosa
    father_sosa = person.sosa.father()
    
    # THEN father's Sosa should be 10 (5 × 2)
    assert father_sosa.value == 10
```

### Pattern de Fixtures

```python
# tests/conftest.py
@pytest.fixture
def sample_family():
    """Create a standard three-generation family"""
    # Grandparents
    grandfather = Person(first_name="Grand", surname="Father", sex=Sex.MALE, sosa=Sosa(4))
    grandmother = Person(first_name="Grand", surname="Mother", sex=Sex.FEMALE, sosa=Sosa(5))
    
    # Parents
    father = Person(first_name="Dad", surname="Father", sex=Sex.MALE, sosa=Sosa(2))
    mother = Person(first_name="Mom", surname="Mother", sex=Sex.FEMALE, sosa=Sosa(3))
    
    # Child (root)
    child = Person(first_name="Root", surname="Child", sex=Sex.MALE, sosa=Sosa(1))
    
    # Set relationships
    child.set_father(father)
    child.set_mother(mother)
    father.set_father(grandfather)
    father.set_mother(grandmother)
    
    return {
        'child': child,
        'father': father,
        'mother': mother,
        'grandfather': grandfather,
        'grandmother': grandmother
    }

# Utilisation
def test_family_tree_navigation(sample_family):
    """Navigate through family tree"""
    child = sample_family['child']
    assert child.father.father == sample_family['grandfather']
```

### Pattern Paramétré

```python
import pytest

@pytest.mark.parametrize("sosa,expected_generation", [
    (1, 1),      # Root
    (2, 2),      # Father
    (3, 2),      # Mother
    (4, 3),      # Paternal grandfather
    (7, 3),      # Maternal grandmother
    (16, 5),     # Great-great-grandfather
])
def test_sosa_generation_calculation(sosa, expected_generation):
    """Test generation calculation for various Sosa numbers"""
    sosa_number = Sosa(sosa)
    assert sosa_number.generation() == expected_generation
```

---

## Exemples pratiques

### Exemple 1 : Validation de données

**Feature** : Valider qu'un nom de famille n'est pas vide

```python
# 1. RED - Test
def test_surname_cannot_be_empty(self):
    """Surname validation should reject empty string"""
    with pytest.raises(ValueError, match="Surname cannot be empty"):
        Person(first_name="John", surname="", sex=Sex.MALE)

# 2. GREEN - Code minimal
@dataclass
class Person:
    first_name: str
    surname: str
    sex: Sex
    
    def __post_init__(self):
        if not self.surname.strip():
            raise ValueError("Surname cannot be empty")

# 3. REFACTOR - Plus de tests et amélioration
def test_surname_cannot_be_whitespace(self):
    """Surname with only whitespace should be rejected"""
    with pytest.raises(ValueError):
        Person(first_name="John", surname="   ", sex=Sex.MALE)

def test_surname_can_have_spaces(self):
    """Surname can contain spaces (e.g., 'Van der Berg')"""
    person = Person(first_name="Jan", surname="Van der Berg", sex=Sex.MALE)
    assert person.surname == "Van der Berg"
```

### Exemple 2 : Calcul complexe (Sosa)

**Feature** : Calculer le numéro Sosa du père

```python
# 1. RED - Test
def test_father_sosa_is_double(self):
    """Father's Sosa number is 2× child's Sosa"""
    child_sosa = Sosa(5)
    father_sosa = child_sosa.father()
    assert father_sosa.value == 10

# 2. GREEN - Code minimal
class Sosa:
    def __init__(self, value: int):
        self.value = value
    
    def father(self) -> 'Sosa':
        return Sosa(self.value * 2)

# 3. REFACTOR - Plus de cas et optimisation
def test_mother_sosa_is_double_plus_one(self):
    child_sosa = Sosa(5)
    mother_sosa = child_sosa.mother()
    assert mother_sosa.value == 11

def test_parent_calculation_for_large_numbers(self):
    """Test with large Sosa numbers (generation 10+)"""
    child_sosa = Sosa(1024)  # Generation 11
    father_sosa = child_sosa.father()
    assert father_sosa.value == 2048
```

### Exemple 3 : API REST

**Feature** : Endpoint pour récupérer une personne

```python
# 1. RED - Test
@pytest.mark.asyncio
async def test_get_person_returns_200(client):
    """GET /persons/{id} returns person data"""
    response = await client.get("/api/v1/persons/123")
    assert response.status_code == 200
    assert response.json()["first_name"] == "John"

# 2. GREEN - Code minimal
@router.get("/api/v1/persons/{person_id}")
async def get_person(person_id: str):
    person = {"first_name": "John", "surname": "Doe"}
    return person

# 3. REFACTOR - Vraie logique
@router.get("/api/v1/persons/{person_id}")
async def get_person(
    person_id: UUID,
    person_service: PersonService = Depends()
):
    """Get person by ID"""
    person = await person_service.get_person(person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return person
```

---

## Tests avancés

### Mocking

```python
from unittest.mock import Mock, patch

def test_person_creation_logs_audit_event():
    """Test that creating person logs audit event"""
    # ARRANGE
    mock_audit = Mock()
    
    # ACT
    with patch('geneweb.api.security.audit.audit_logger', mock_audit):
        person = create_person_with_audit(
            first_name="John",
            surname="Doe"
        )
    
    # ASSERT
    mock_audit.log_person_created.assert_called_once()
    call_args = mock_audit.log_person_created.call_args
    assert call_args[1]['person_id'] == person.id
```

### Tests asynchrones

```python
import pytest

@pytest.mark.asyncio
async def test_async_person_save():
    """Test async person save to database"""
    # ARRANGE
    person = Person(first_name="John", surname="Doe")
    repo = PersonRepository()
    
    # ACT
    saved_person = await repo.save(person)
    
    # ASSERT
    assert saved_person.id is not None
    
    # CLEANUP
    await repo.delete(saved_person.id)
```

### Tests de performance

```python
import time

def test_sosa_calculation_performance():
    """Sosa calculation should be O(1)"""
    start = time.perf_counter()
    
    for i in range(10000):
        sosa = Sosa(i + 1)
        _ = sosa.generation()
    
    elapsed = time.perf_counter() - start
    
    # Should complete in less than 100ms
    assert elapsed < 0.1
```

---

## Anti-patterns à éviter

### ❌ Anti-pattern 1 : Tests dépendants

```python
# ❌ MAUVAIS : Tests dépendent les uns des autres
class TestPersonWorkflow:
    person = None
    
    def test_1_create_person(self):
        self.person = Person(...)
        assert self.person is not None
    
    def test_2_add_father(self):
        # ❌ Dépend du test 1
        self.person.set_father(...)

# ✅ BON : Tests indépendants
class TestPersonWorkflow:
    @pytest.fixture
    def person(self):
        return Person(first_name="John", surname="Doe")
    
    def test_create_person(self):
        person = Person(...)
        assert person is not None
    
    def test_add_father(self, person):
        # ✅ Utilise la fixture
        person.set_father(...)
```

### ❌ Anti-pattern 2 : Tests qui testent l'implémentation

```python
# ❌ MAUVAIS : Teste l'implémentation interne
def test_person_uses_dictionary_internally(self):
    person = Person(...)
    assert isinstance(person._data, dict)  # ❌ Teste l'impl

# ✅ BON : Teste le comportement
def test_person_stores_and_retrieves_name(self):
    person = Person(first_name="John", surname="Doe")
    assert person.first_name == "John"  # ✅ Teste le comportement
```

### ❌ Anti-pattern 3 : Tests trop complexes

```python
# ❌ MAUVAIS : Test avec logique complexe
def test_complex_family_tree(self):
    persons = []
    for i in range(10):
        person = Person(...)
        if i % 2 == 0:
            person.set_father(persons[i-1])
        else:
            person.set_mother(persons[i-1])
        persons.append(person)
    # Trop complexe à comprendre

# ✅ BON : Tests simples et clairs
def test_child_has_father(self):
    child = Person(...)
    father = Person(...)
    child.set_father(father)
    assert child.father == father
```

### ❌ Anti-pattern 4 : Pas de test pour les cas limites

```python
# ❌ MAUVAIS : Seulement le cas normal
def test_divide(self):
    assert divide(10, 2) == 5

# ✅ BON : Tous les cas
def test_divide_normal_case(self):
    assert divide(10, 2) == 5

def test_divide_by_zero_raises_error(self):
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)

def test_divide_negative_numbers(self):
    assert divide(-10, 2) == -5

def test_divide_floats(self):
    assert divide(5, 2) == 2.5
```

---

## Métriques de qualité

### Couverture de code

```bash
# Générer rapport de couverture
pytest --cov=src --cov-report=html

# Objectifs :
# - Core modules : >= 95%
# - API modules : >= 90%
# - Database : >= 90%
# - Global : >= 90%
```

### Mutation testing

Le mutation testing vérifie que vos tests détectent vraiment les bugs :

```bash
# Installer mutmut
pip install mutmut

# Lancer mutation testing
mutmut run

# Voir les résultats
mutmut results
mutmut show
```

---

## Ressources

### Livres recommandés
- **Test Driven Development: By Example** - Kent Beck
- **Growing Object-Oriented Software, Guided by Tests** - Freeman & Pryce
- **Clean Code** - Robert C. Martin

### Vidéos
- [TDD by Uncle Bob](https://www.youtube.com/watch?v=qkblc5WRn-U)
- [The Three Laws of TDD](https://www.youtube.com/watch?v=AoIfc5NwRks)

### Articles
- [Martin Fowler on TDD](https://martinfowler.com/bliki/TestDrivenDevelopment.html)
- [pytest best practices](https://docs.pytest.org/en/stable/goodpractices.html)

---

**Happy TDD! 🧪✅**

*N'oubliez pas : Red → Green → Refactor*
