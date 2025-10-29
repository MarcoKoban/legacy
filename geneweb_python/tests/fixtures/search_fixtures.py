"""
Test fixtures for search and genealogy tests.

Provides reusable test data including:
- Deceased persons
- Living persons
- Multi-generation families
- Complex family trees
"""

from unittest.mock import Mock

import pytest

from geneweb.core.person import Person
from geneweb.db.database import Database


@pytest.fixture
def deceased_person():
    """Create a deceased person for testing."""
    person = Mock(spec=Person)
    person.first_name = "Jean"
    person.surname = "Dupont"
    person.sex = 1  # Male
    person.birth = Mock()
    person.birth.year = 1920
    person.birth.month = 5
    person.birth.day = 15
    person.birth.place = "Paris, France"
    person.death = Mock()
    person.death.year = 1990
    person.death.month = 8
    person.death.day = 20
    person.death.place = "Lyon, France"
    person.occupation = "Engineer"
    person.notes = "Decorated war veteran"
    person.get_id.return_value = "person_deceased_1"
    person.get_father.return_value = None
    person.get_mother.return_value = None
    person.get_children.return_value = []
    return person


@pytest.fixture
def living_person_young():
    """Create a young living person for testing."""
    person = Mock(spec=Person)
    person.first_name = "Marie"
    person.surname = "Martin"
    person.sex = 2  # Female
    person.birth = Mock()
    person.birth.year = 2000
    person.birth.month = 3
    person.birth.day = 10
    person.birth.place = "Marseille, France"
    person.death = None
    person.occupation = "Doctor"
    person.notes = "Private medical information"
    person.get_id.return_value = "person_living_young"
    person.get_father.return_value = None
    person.get_mother.return_value = None
    person.get_children.return_value = []
    return person


@pytest.fixture
def living_person_old():
    """Create an old living person (>100 years, should be treated as deceased)."""
    person = Mock(spec=Person)
    person.first_name = "Pierre"
    person.surname = "Durand"
    person.sex = 1
    person.birth = Mock()
    person.birth.year = 1910
    person.birth.month = 1
    person.birth.day = 1
    person.birth.place = "Bordeaux, France"
    person.death = None
    person.occupation = "Retired Teacher"
    person.notes = "Centenarian"
    person.get_id.return_value = "person_living_old"
    person.get_father.return_value = None
    person.get_mother.return_value = None
    person.get_children.return_value = []
    return person


@pytest.fixture
def person_unknown_birth():
    """Create a person with unknown birth date."""
    person = Mock(spec=Person)
    person.first_name = "Unknown"
    person.surname = "Birth"
    person.sex = 1
    person.birth = None
    person.death = None
    person.occupation = None
    person.notes = "Found as orphan, no records"
    person.get_id.return_value = "person_unknown"
    person.get_father.return_value = None
    person.get_mother.return_value = None
    person.get_children.return_value = []
    return person


@pytest.fixture
def family_two_generations(deceased_person):
    """Create a two-generation family."""
    # Father (deceased)
    father = Mock(spec=Person)
    father.first_name = "Paul"
    father.surname = "Dupont"
    father.sex = 1
    father.birth = Mock()
    father.birth.year = 1890
    father.death = Mock()
    father.death.year = 1960
    father.get_id.return_value = "father_1"
    father.get_father.return_value = None
    father.get_mother.return_value = None

    # Mother (deceased)
    mother = Mock(spec=Person)
    mother.first_name = "Anne"
    mother.surname = "Bernard"
    mother.sex = 2
    mother.birth = Mock()
    mother.birth.year = 1895
    mother.death = Mock()
    mother.death.year = 1965
    mother.get_id.return_value = "mother_1"
    mother.get_father.return_value = None
    mother.get_mother.return_value = None

    # Setup relationships
    deceased_person.get_father.return_value = father
    deceased_person.get_mother.return_value = mother

    father.get_children.return_value = [deceased_person]
    mother.get_children.return_value = [deceased_person]

    return {"child": deceased_person, "father": father, "mother": mother}


@pytest.fixture
def family_three_generations():
    """Create a three-generation family with living members."""
    # Grandparents (deceased)
    grandfather = Mock(spec=Person)
    grandfather.first_name = "Jacques"
    grandfather.surname = "Dupont"
    grandfather.sex = 1
    grandfather.birth = Mock()
    grandfather.birth.year = 1890
    grandfather.death = Mock()
    grandfather.death.year = 1970
    grandfather.get_id.return_value = "grandfather_1"
    grandfather.get_father.return_value = None
    grandfather.get_mother.return_value = None

    grandmother = Mock(spec=Person)
    grandmother.first_name = "Marie"
    grandmother.surname = "Dubois"
    grandmother.sex = 2
    grandmother.birth = Mock()
    grandmother.birth.year = 1895
    grandmother.death = Mock()
    grandmother.death.year = 1975
    grandmother.get_id.return_value = "grandmother_1"
    grandmother.get_father.return_value = None
    grandmother.get_mother.return_value = None

    # Parents (deceased)
    father = Mock(spec=Person)
    father.first_name = "Paul"
    father.surname = "Dupont"
    father.sex = 1
    father.birth = Mock()
    father.birth.year = 1920
    father.death = Mock()
    father.death.year = 1995
    father.get_id.return_value = "father_1"
    father.get_father.return_value = grandfather
    father.get_mother.return_value = grandmother

    mother = Mock(spec=Person)
    mother.first_name = "Sophie"
    mother.surname = "Martin"
    mother.sex = 2
    mother.birth = Mock()
    mother.birth.year = 1925
    mother.death = Mock()
    mother.death.year = 2000
    mother.get_id.return_value = "mother_1"
    mother.get_father.return_value = None
    mother.get_mother.return_value = None

    # Children (living)
    son = Mock(spec=Person)
    son.first_name = "Jean"
    son.surname = "Dupont"
    son.sex = 1
    son.birth = Mock()
    son.birth.year = 1950
    son.death = None  # Living
    son.get_id.return_value = "son_1"
    son.get_father.return_value = father
    son.get_mother.return_value = mother

    daughter = Mock(spec=Person)
    daughter.first_name = "Claire"
    daughter.surname = "Dupont"
    daughter.sex = 2
    daughter.birth = Mock()
    daughter.birth.year = 1955
    daughter.death = None  # Living
    daughter.get_id.return_value = "daughter_1"
    daughter.get_father.return_value = father
    daughter.get_mother.return_value = mother

    # Setup children relationships
    grandfather.get_children.return_value = [father]
    grandmother.get_children.return_value = [father]
    father.get_children.return_value = [son, daughter]
    mother.get_children.return_value = [son, daughter]
    son.get_children.return_value = []
    daughter.get_children.return_value = []

    return {
        "grandfather": grandfather,
        "grandmother": grandmother,
        "father": father,
        "mother": mother,
        "son": son,
        "daughter": daughter,
    }


@pytest.fixture
def family_four_generations():
    """Create a four-generation family with mix of living and deceased."""
    # Great-grandparents (deceased)
    gg_father = Mock(spec=Person)
    gg_father.first_name = "François"
    gg_father.surname = "Dupont"
    gg_father.sex = 1
    gg_father.birth = Mock()
    gg_father.birth.year = 1860
    gg_father.death = Mock()
    gg_father.death.year = 1940
    gg_father.get_id.return_value = "gg_father"
    gg_father.get_father.return_value = None
    gg_father.get_mother.return_value = None

    # Grandfather
    grandfather = Mock(spec=Person)
    grandfather.first_name = "Jacques"
    grandfather.surname = "Dupont"
    grandfather.sex = 1
    grandfather.birth = Mock()
    grandfather.birth.year = 1890
    grandfather.death = Mock()
    grandfather.death.year = 1970
    grandfather.get_id.return_value = "grandfather"
    grandfather.get_father.return_value = gg_father
    grandfather.get_mother.return_value = None

    # Father
    father = Mock(spec=Person)
    father.first_name = "Paul"
    father.surname = "Dupont"
    father.sex = 1
    father.birth = Mock()
    father.birth.year = 1920
    father.death = Mock()
    father.death.year = 1995
    father.get_id.return_value = "father"
    father.get_father.return_value = grandfather
    father.get_mother.return_value = None

    # Son (living)
    son = Mock(spec=Person)
    son.first_name = "Marc"
    son.surname = "Dupont"
    son.sex = 1
    son.birth = Mock()
    son.birth.year = 1950
    son.death = None
    son.get_id.return_value = "son"
    son.get_father.return_value = father
    son.get_mother.return_value = None

    # Grandson (living)
    grandson = Mock(spec=Person)
    grandson.first_name = "Thomas"
    grandson.surname = "Dupont"
    grandson.sex = 1
    grandson.birth = Mock()
    grandson.birth.year = 1980
    grandson.death = None
    grandson.get_id.return_value = "grandson"
    grandson.get_father.return_value = son
    grandson.get_mother.return_value = None

    # Great-grandson (living, minor)
    great_grandson = Mock(spec=Person)
    great_grandson.first_name = "Louis"
    great_grandson.surname = "Dupont"
    great_grandson.sex = 1
    great_grandson.birth = Mock()
    great_grandson.birth.year = 2010
    great_grandson.death = None
    great_grandson.get_id.return_value = "great_grandson"
    great_grandson.get_father.return_value = grandson
    great_grandson.get_mother.return_value = None

    # Setup children relationships
    gg_father.get_children.return_value = [grandfather]
    grandfather.get_children.return_value = [father]
    father.get_children.return_value = [son]
    son.get_children.return_value = [grandson]
    grandson.get_children.return_value = [great_grandson]
    great_grandson.get_children.return_value = []

    return {
        "great_great_grandfather": gg_father,
        "grandfather": grandfather,
        "father": father,
        "son": son,
        "grandson": grandson,
        "great_grandson": great_grandson,
    }


@pytest.fixture
def mock_database_simple(deceased_person, living_person_young):
    """Create a simple mock database with basic persons."""
    db = Mock(spec=Database)
    db.persons = {
        deceased_person.get_id(): deceased_person,
        living_person_young.get_id(): living_person_young,
    }
    db.get_person.side_effect = lambda pid: db.persons.get(pid)
    return db


@pytest.fixture
def mock_database_with_family(family_three_generations):
    """Create a mock database with a three-generation family."""
    db = Mock(spec=Database)
    family = family_three_generations
    db.persons = {
        family["grandfather"].get_id(): family["grandfather"],
        family["grandmother"].get_id(): family["grandmother"],
        family["father"].get_id(): family["father"],
        family["mother"].get_id(): family["mother"],
        family["son"].get_id(): family["son"],
        family["daughter"].get_id(): family["daughter"],
    }
    db.get_person.side_effect = lambda pid: db.persons.get(pid)
    return db


@pytest.fixture
def mock_database_complex(family_four_generations):
    """Create a complex mock database with four generations."""
    db = Mock(spec=Database)
    family = family_four_generations
    db.persons = {
        family["great_great_grandfather"].get_id(): family["great_great_grandfather"],
        family["grandfather"].get_id(): family["grandfather"],
        family["father"].get_id(): family["father"],
        family["son"].get_id(): family["son"],
        family["grandson"].get_id(): family["grandson"],
        family["great_grandson"].get_id(): family["great_grandson"],
    }
    db.get_person.side_effect = lambda pid: db.persons.get(pid)
    return db


@pytest.fixture
def sample_search_queries():
    """Provide sample search queries for testing."""
    return {
        "simple": {"query": "Dupont"},
        "with_first_name": {"query": "Jean", "filters": {"first_name": "Jean"}},
        "with_surname": {"query": "Dupont", "filters": {"surname": "Dupont"}},
        "with_birth_year": {"query": "", "filters": {"birth_year": 1920}},
        "with_sex": {"query": "", "filters": {"sex": "M"}},
        "complex": {
            "query": "Jean Dupont",
            "filters": {
                "first_name": "Jean",
                "surname": "Dupont",
                "birth_year": 1920,
                "birth_place": "Paris",
                "sex": "M",
            },
        },
        "paginated": {"query": "", "offset": 10, "limit": 20},
    }


@pytest.fixture
def sample_user_ids():
    """Provide sample user IDs for authorization testing."""
    return {
        "authorized_user": "user_family_123",
        "unauthorized_user": "user_stranger_456",
        "admin_user": "admin_789",
        "anonymous": None,
    }


@pytest.fixture
def expected_privacy_levels():
    """Provide expected privacy level mappings."""
    return {
        "deceased": "PUBLIC",
        "living_young": "ANONYMIZED",
        "living_old": "PUBLIC",  # >100 years
        "unknown_birth": "ANONYMIZED",  # Conservative approach
        "living_with_auth": "RESTRICTED",
    }


@pytest.fixture
def sosa_numbers():
    """Provide Sosa number mappings for testing."""
    return {
        1: {
            "name": "Root",
            "relationship": "Personne de référence (de cujus)",
            "generation": 0,
        },
        2: {"name": "Father", "relationship": "Père", "generation": 1},
        3: {"name": "Mother", "relationship": "Mère", "generation": 1},
        4: {
            "name": "Paternal Grandfather",
            "relationship": "Grand-père paternel",
            "generation": 2,
        },
        5: {
            "name": "Paternal Grandmother",
            "relationship": "Grand-mère paternelle",
            "generation": 2,
        },
        6: {
            "name": "Maternal Grandfather",
            "relationship": "Grand-père maternel",
            "generation": 2,
        },
        7: {
            "name": "Maternal Grandmother",
            "relationship": "Grand-mère maternelle",
            "generation": 2,
        },
        8: {
            "name": "GG-Grandfather (paternal)",
            "relationship": "Arrière-grand-père paternel",
            "generation": 3,
        },
    }
