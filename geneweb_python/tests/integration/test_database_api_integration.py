"""
Integration tests for Database and API connection.
"""

import os
import tempfile
from unittest.mock import patch
from uuid import uuid4

import pytest

from geneweb.api.adapters.person_adapter import PersonAdapter
from geneweb.api.services.person_service import PersonService
from geneweb.core.person import Person as DBPerson
from geneweb.core.person import Sex as DBSex
from geneweb.db.database import Database


@pytest.fixture(autouse=True)
def mock_encryption():
    """Mock encryption functions to avoid requiring master key."""
    with patch(
        "geneweb.api.services.person_service.encrypt_sensitive_data",
        side_effect=lambda x: x,
    ):
        with patch(
            "geneweb.api.services.person_service.decrypt_sensitive_data",
            side_effect=lambda x: x,
        ):
            yield


class MockSecurityContext:
    """Mock security context for testing."""

    def __init__(self):
        self.user = MockUser()
        self.ip_address = "127.0.0.1"
        self.user_agent = "test"


class MockUser:
    """Mock user for testing."""

    def __init__(self):
        self.user_id = uuid4()
        self.role = MockRole()
        self.family_person_id = None
        self.related_person_ids = []


class MockRole:
    """Mock role for testing."""

    def __init__(self):
        self.value = "admin"


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_db")
        db = Database(db_path)
        yield db


@pytest.fixture
def person_service(temp_db):
    """Create a PersonService with temp database."""
    return PersonService(database=temp_db)


def test_database_person_service_integration(person_service):
    """Test that PersonService correctly integrates with Database."""
    # Check service has database
    assert person_service.database is not None
    assert isinstance(person_service.database, Database)


@pytest.mark.asyncio
async def test_create_person_stores_in_database(person_service):
    """Test that creating a person through API stores it in Database."""
    # Create person data
    person_data = {
        "first_name": "Jean",
        "last_name": "Dupont",
        "sex": "male",
        "birth_date": "1950-01-15",
        "birth_place": "Paris, France",
        "occupation": "Engineer",
        "notes": "Test person",
        "visibility_level": "family",
        "gdpr_consents": [],
    }

    # Create mock security context
    security_context = MockSecurityContext()

    # Create person through service
    person_response = await person_service.create_person(
        person_data=person_data,
        created_by=security_context.user.user_id,
        security_context=security_context,
    )

    # Verify response
    assert person_response is not None
    assert person_response.first_name == "Jean"
    assert person_response.last_name == "Dupont"
    assert person_response.id is not None

    # Verify person exists in collection
    person_id = person_response.id
    assert person_id in person_service._uuid_to_index

    person_index = person_service._uuid_to_index[person_id]
    db_person = person_service._persons_collection[person_index]

    assert db_person is not None
    # db_person is currently a dict (encrypted_record)
    assert db_person["first_name"] == "Jean"
    assert db_person["last_name"] == "Dupont"


@pytest.mark.asyncio
async def test_get_person_retrieves_from_database(person_service):
    """Test that getting a person retrieves data from Database."""
    # First create a person
    person_data = {
        "first_name": "Marie",
        "last_name": "Martin",
        "sex": "female",
        "birth_date": "1960-05-20",
        "visibility_level": "family",
        "gdpr_consents": [],
    }

    security_context = MockSecurityContext()

    created_person = await person_service.create_person(
        person_data=person_data,
        created_by=security_context.user.user_id,
        security_context=security_context,
    )

    person_id = created_person.id

    # Now retrieve the person
    retrieved_person = await person_service.get_person(
        person_id=person_id, security_context=security_context
    )

    # Verify data matches
    assert retrieved_person is not None
    assert retrieved_person.id == person_id
    assert retrieved_person.first_name == "Marie"
    assert retrieved_person.last_name == "Martin"


@pytest.mark.asyncio
async def test_update_person_modifies_database(person_service):
    """Test that updating a person modifies the Database."""
    # Create initial person
    person_data = {
        "first_name": "Pierre",
        "last_name": "Bernard",
        "sex": "male",
        "occupation": "Teacher",
        "visibility_level": "family",
        "gdpr_consents": [],
    }

    security_context = MockSecurityContext()

    created_person = await person_service.create_person(
        person_data=person_data,
        created_by=security_context.user.user_id,
        security_context=security_context,
    )

    person_id = created_person.id

    # Update person
    update_data = {
        "occupation": "Professor",
        "notes": "Promoted to Professor",
    }

    updated_person = await person_service.update_person(
        person_id=person_id,
        update_data=update_data,
        updated_by=security_context.user.user_id,
        security_context=security_context,
    )

    # Verify update
    assert updated_person.occupation == "Professor"
    assert updated_person.notes == "Promoted to Professor"

    # Verify in collection
    person_index = person_service._uuid_to_index[person_id]
    db_person = person_service._persons_collection[person_index]
    # db_person is currently a dict (encrypted_record)
    assert db_person["occupation"] == "Professor"
    assert db_person["notes"] == "Promoted to Professor"


@pytest.mark.asyncio
async def test_list_persons_from_database(person_service):
    """Test that listing persons retrieves from Database."""
    security_context = MockSecurityContext()

    # Create multiple persons
    persons_data = [
        {
            "first_name": "Alice",
            "last_name": "Durand",
            "sex": "female",
            "visibility_level": "family",
            "gdpr_consents": [],
        },
        {
            "first_name": "Bob",
            "last_name": "Robert",
            "sex": "male",
            "visibility_level": "family",
            "gdpr_consents": [],
        },
        {
            "first_name": "Claire",
            "last_name": "Petit",
            "sex": "female",
            "visibility_level": "family",
            "gdpr_consents": [],
        },
    ]

    for person_data in persons_data:
        await person_service.create_person(
            person_data=person_data,
            created_by=security_context.user.user_id,
            security_context=security_context,
        )

    # List all persons
    from geneweb.api.models.person import PersonSearchFilters

    filters = PersonSearchFilters(page=1, page_size=10)
    result = await person_service.list_persons(
        filters=filters, security_context=security_context
    )

    # Verify result
    assert result.total >= 3
    assert len(result.items) >= 3

    # Check that persons are from database
    first_names = [item.first_name for item in result.items]
    assert "Alice" in first_names
    assert "Bob" in first_names
    assert "Claire" in first_names


def test_adapter_conversions():
    """Test PersonAdapter conversions between DB and API models."""
    adapter = PersonAdapter()

    # Test DB to API conversion
    from geneweb.core.calendar import CalendarDate, CalendarType
    from geneweb.core.event import Event
    from geneweb.core.place import Place

    birth_event = Event(place=Place("Paris"))
    birth_event.calendar_date = CalendarDate(
        year=1980, month=5, day=15, calendar_type=CalendarType.GREGORIAN
    )

    db_person = DBPerson(
        first_name="Test",
        surname="Person",
        sex=DBSex.MALE,
        birth=birth_event,
        occupation="Developer",
        notes="Test notes",
    )

    api_response = adapter.db_person_to_api_response(db_person)

    assert api_response.first_name == "Test"
    assert api_response.last_name == "Person"
    assert api_response.sex == "male"  # use_enum_values=True in model config
    assert api_response.birth_place == "Paris"
    assert api_response.occupation == "Developer"

    # Test API to DB conversion
    api_data = {
        "first_name": "Another",
        "last_name": "Person",
        "sex": "female",
        "birth_date": "1990-01-01",
        "birth_place": "Lyon",
        "occupation": "Designer",
        "notes": "Another test",
        "visibility_level": "family",
    }

    db_person_converted = adapter.api_create_to_db_person(api_data)

    assert db_person_converted.first_name == "Another"
    assert db_person_converted.surname == "Person"
    assert db_person_converted.sex == DBSex.FEMALE
    assert db_person_converted.occupation == "Designer"
