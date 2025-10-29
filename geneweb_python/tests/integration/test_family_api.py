"""Integration tests for Family API endpoints."""

import os

# Disable rate limiting for tests (must be before app import)
os.environ["TESTING"] = "1"

# isort: split
# The above environment variable MUST be set before importing app
# to disable rate limiting in tests. Do not reorder these imports.

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from geneweb.api.dependencies import db_manager  # noqa: E402
from geneweb.api.main import app  # noqa: E402
from geneweb.api.services.family_service import _FAMILIES_STORAGE  # noqa: E402
from geneweb.core.person import Person, Sex  # noqa: E402


@pytest.fixture
def client():
    """Create test client with fresh database."""
    # Clear any existing databases
    db_manager._databases = {}
    db_manager._active_db_name = None

    # Clear families storage
    _FAMILIES_STORAGE.clear()

    # Initialize test database
    db_manager.initialize(create_if_missing=True)

    # Create test client
    with TestClient(app) as test_client:
        yield test_client

    # Cleanup
    _FAMILIES_STORAGE.clear()
    db_manager.close()
    db_manager._databases = {}
    db_manager._active_db_name = None


@pytest.fixture
def sample_persons(client):
    """Create sample persons for testing families."""
    # Get database from db_manager
    db_name = db_manager.get_active_database_name()
    db = db_manager.get_database(db_name)

    # Create father
    father = Person(
        first_name="Jean",
        surname="Dupont",
        sex=Sex.MALE,
        occ=0,
    )
    father_id = db.add_person(father)

    # Create mother
    mother = Person(
        first_name="Marie",
        surname="Martin",
        sex=Sex.FEMALE,
        occ=0,
    )
    mother_id = db.add_person(mother)

    # Create children
    child1 = Person(
        first_name="Sophie",
        surname="Dupont",
        sex=Sex.FEMALE,
        occ=0,
    )
    child1_id = db.add_person(child1)

    child2 = Person(
        first_name="Pierre",
        surname="Dupont",
        sex=Sex.MALE,
        occ=0,
    )
    child2_id = db.add_person(child2)

    # Create witness
    witness = Person(
        first_name="Jacques",
        surname="Bernard",
        sex=Sex.MALE,
        occ=0,
    )
    witness_id = db.add_person(witness)

    db.commit_patches()

    return {
        "father_id": str(father_id),
        "mother_id": str(mother_id),
        "child1_id": str(child1_id),
        "child2_id": str(child2_id),
        "witness_id": str(witness_id),
    }


class TestFamilyAPI:
    """Test Family API endpoints."""

    def test_create_family_minimal(self, client, sample_persons):
        """Test creating a family with minimal data."""
        response = client.post(
            "/api/v1/families/",
            json={
                "father_ids": [sample_persons["father_id"]],
                "mother_ids": [sample_persons["mother_id"]],
                "relation": "married",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "family" in data
        assert data["family"]["father_ids"] == [sample_persons["father_id"]]
        assert data["family"]["mother_ids"] == [sample_persons["mother_id"]]
        assert data["family"]["relation"] == "married"

    def test_create_family_complete(self, client, sample_persons):
        """Test creating a family with complete data."""
        response = client.post(
            "/api/v1/families/",
            json={
                "father_ids": [sample_persons["father_id"]],
                "mother_ids": [sample_persons["mother_id"]],
                "children_ids": [
                    sample_persons["child1_id"],
                    sample_persons["child2_id"],
                ],
                "relation": "married",
                "marriage_date": "1995-06-15",
                "marriage_place": "Paris, France",
                "marriage_source": "Mairie de Paris",
                "comment": "Beautiful ceremony",
                "events": [
                    {
                        "event_name": "marriage",
                        "date": "1995-06-15",
                        "place": "Paris, France",
                        "source": "Marriage certificate",
                        "note": "Sunny day",
                        "witnesses": [
                            {
                                "person_id": sample_persons["witness_id"],
                                "witness_kind": "witness",
                            }
                        ],
                    }
                ],
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        family = data["family"]
        assert family["father_ids"] == [sample_persons["father_id"]]
        assert family["mother_ids"] == [sample_persons["mother_id"]]
        assert len(family["children_ids"]) == 2
        assert family["marriage_date"] == "1995-06-15"
        assert family["marriage_place"] == "Paris, France"
        assert family["comment"] == "Beautiful ceremony"
        assert len(family["events"]) >= 1

    def test_create_family_with_divorce(self, client, sample_persons):
        """Test creating a divorced family."""
        response = client.post(
            "/api/v1/families/",
            json={
                "father_ids": [sample_persons["father_id"]],
                "mother_ids": [sample_persons["mother_id"]],
                "relation": "married",
                "divorce_info": {
                    "divorce_status": "divorced",
                    "divorce_date": "2005-03-20",
                },
            },
        )

        assert response.status_code == 201
        data = response.json()
        family = data["family"]
        assert family["divorce_info"] is not None
        assert family["divorce_info"]["divorce_status"] == "divorced"
        assert family["divorce_info"]["divorce_date"] == "2005-03-20"

    def test_create_family_single_parent(self, client, sample_persons):
        """Test creating a single-parent family."""
        response = client.post(
            "/api/v1/families/",
            json={
                "mother_ids": [sample_persons["mother_id"]],
                "children_ids": [sample_persons["child1_id"]],
                "relation": "not_married",
            },
        )

        assert response.status_code == 201
        data = response.json()
        family = data["family"]
        assert family["mother_ids"] == [sample_persons["mother_id"]]
        assert len(family["father_ids"]) == 0
        assert len(family["children_ids"]) == 1

    def test_create_family_no_parents_fails(self, client):
        """Test that creating a family without parents fails."""
        response = client.post(
            "/api/v1/families/",
            json={
                "relation": "married",
            },
        )

        assert response.status_code == 400
        assert "at least one parent" in response.json()["detail"].lower()

    def test_get_family(self, client, sample_persons):
        """Test getting a family by ID."""
        # Create family first
        create_response = client.post(
            "/api/v1/families/",
            json={
                "father_ids": [sample_persons["father_id"]],
                "mother_ids": [sample_persons["mother_id"]],
                "relation": "married",
            },
        )
        family_id = create_response.json()["family"]["id"]

        # Get family
        response = client.get(f"/api/v1/families/{family_id}")

        assert response.status_code == 200
        family = response.json()
        assert family["id"] == family_id
        assert family["father_ids"] == [sample_persons["father_id"]]
        assert family["mother_ids"] == [sample_persons["mother_id"]]

    def test_get_family_not_found(self, client):
        """Test getting a non-existent family."""
        response = client.get("/api/v1/families/nonexistent")

        assert response.status_code == 404

    def test_list_families(self, client, sample_persons):
        """Test listing all families."""
        # Create multiple families
        for i in range(3):
            client.post(
                "/api/v1/families/",
                json={
                    "father_ids": [sample_persons["father_id"]],
                    "mother_ids": [sample_persons["mother_id"]],
                    "relation": "married",
                },
            )

        # List families
        response = client.get("/api/v1/families/")

        assert response.status_code == 200
        data = response.json()
        assert "families" in data
        assert data["total"] >= 3
        assert len(data["families"]) >= 3

    def test_list_families_pagination(self, client, sample_persons):
        """Test families list pagination."""
        # Create families
        for i in range(5):
            client.post(
                "/api/v1/families/",
                json={
                    "father_ids": [sample_persons["father_id"]],
                    "mother_ids": [sample_persons["mother_id"]],
                    "relation": "married",
                },
            )

        # Test pagination
        response = client.get("/api/v1/families/?offset=2&limit=2")

        assert response.status_code == 200
        data = response.json()
        assert data["offset"] == 2
        assert data["limit"] == 2
        assert len(data["families"]) <= 2

    def test_update_family(self, client, sample_persons):
        """Test updating a family."""
        # Create family
        create_response = client.post(
            "/api/v1/families/",
            json={
                "father_ids": [sample_persons["father_id"]],
                "mother_ids": [sample_persons["mother_id"]],
                "relation": "married",
            },
        )
        family_id = create_response.json()["family"]["id"]

        # Update family
        response = client.patch(
            f"/api/v1/families/{family_id}",
            json={
                "comment": "Updated comment",
                "relation": "not_married",
            },
        )

        assert response.status_code == 200
        family = response.json()
        assert family["comment"] == "Updated comment"
        assert family["relation"] == "not_married"

    def test_update_family_add_children(self, client, sample_persons):
        """Test adding children to a family."""
        # Create family without children
        create_response = client.post(
            "/api/v1/families/",
            json={
                "father_ids": [sample_persons["father_id"]],
                "mother_ids": [sample_persons["mother_id"]],
                "relation": "married",
            },
        )
        family_id = create_response.json()["family"]["id"]

        # Add children
        response = client.patch(
            f"/api/v1/families/{family_id}",
            json={
                "children_ids": [
                    sample_persons["child1_id"],
                    sample_persons["child2_id"],
                ],
            },
        )

        assert response.status_code == 200
        family = response.json()
        assert len(family["children_ids"]) == 2

    def test_update_family_not_found(self, client):
        """Test updating a non-existent family."""
        response = client.patch(
            "/api/v1/families/nonexistent",
            json={"comment": "Test"},
        )

        assert response.status_code == 404

    def test_delete_family(self, client, sample_persons):
        """Test deleting a family."""
        # Create family
        create_response = client.post(
            "/api/v1/families/",
            json={
                "father_ids": [sample_persons["father_id"]],
                "mother_ids": [sample_persons["mother_id"]],
                "relation": "married",
            },
        )
        family_id = create_response.json()["family"]["id"]

        # Delete family
        response = client.delete(f"/api/v1/families/{family_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["family_id"] == family_id

        # Verify family is deleted
        get_response = client.get(f"/api/v1/families/{family_id}")
        assert get_response.status_code == 404

    def test_delete_family_not_found(self, client):
        """Test deleting a non-existent family."""
        response = client.delete("/api/v1/families/nonexistent")

        assert response.status_code == 404

    def test_create_family_with_multiple_events(self, client, sample_persons):
        """Test creating a family with multiple events."""
        response = client.post(
            "/api/v1/families/",
            json={
                "father_ids": [sample_persons["father_id"]],
                "mother_ids": [sample_persons["mother_id"]],
                "relation": "married",
                "events": [
                    {
                        "event_name": "marriage",
                        "date": "1995-06-15",
                        "place": "Paris",
                    },
                    {
                        "event_name": "marriage_bann",
                        "date": "1995-06-01",
                        "place": "Paris",
                    },
                    {
                        "event_name": "divorce",
                        "date": "2005-03-20",
                        "place": "Lyon",
                    },
                ],
            },
        )

        assert response.status_code == 201
        family = response.json()["family"]
        assert len(family["events"]) >= 3
