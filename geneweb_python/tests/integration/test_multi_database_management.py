"""
Integration tests for multi-database management features.
Tests DatabaseManager multi-DB capabilities and database router endpoints.
"""

import os

# Disable rate limiting for tests
os.environ["TESTING"] = "1"

# isort: split
# The above environment variable MUST be set before importing app
# to disable rate limiting in tests. Do not reorder these imports.

import shutil  # noqa: E402
import tempfile  # noqa: E402
from pathlib import Path  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from geneweb.api.dependencies import db_manager  # noqa: E402
from geneweb.api.main import app  # noqa: E402


class TestMultiDatabaseManager:
    """Tests for multi-database DatabaseManager features."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Setup and teardown for each test."""
        # Create temp directory
        self.temp_dir = tempfile.mkdtemp()

        # Reset database manager
        db_manager._databases = {}
        db_manager._active_db_name = None
        db_manager._databases_dir = self.temp_dir

        yield

        # Cleanup
        db_manager.close_all()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_create_multiple_databases(self):
        """Test creating multiple databases."""
        # Create first database
        name1 = db_manager.create_database("db1", set_active=True)
        assert name1 == "db1"
        assert db_manager.get_active_database_name() == "db1"

        # Create second database
        name2 = db_manager.create_database("db2", set_active=False)
        assert name2 == "db2"
        assert db_manager.get_active_database_name() == "db1"  # Still db1

        # Create third and set as active
        name3 = db_manager.create_database("db3", set_active=True)
        assert name3 == "db3"
        assert db_manager.get_active_database_name() == "db3"

        # Verify all databases exist
        databases = db_manager.list_databases()
        assert len(databases) == 3
        assert {db["name"] for db in databases} == {"db1", "db2", "db3"}

    def test_get_database_by_name(self):
        """Test getting specific database by name."""
        db_manager.create_database("test_db1")
        db_manager.create_database("test_db2")

        # Get specific databases
        db1 = db_manager.get_database("test_db1")
        db2 = db_manager.get_database("test_db2")

        assert db1 is not None
        assert db2 is not None
        assert db1 != db2

    def test_get_active_database(self):
        """Test getting active database without specifying name."""
        db_manager.create_database("active_db", set_active=True)

        # Get without name should return active
        db = db_manager.get_database()
        assert db is not None

    def test_set_active_database(self):
        """Test switching active database."""
        db_manager.create_database("db1", set_active=True)
        db_manager.create_database("db2")

        assert db_manager.get_active_database_name() == "db1"

        # Switch to db2
        db_manager.set_active_database("db2")
        assert db_manager.get_active_database_name() == "db2"

        # Verify active flag in list
        databases = db_manager.list_databases()
        db2_info = next(db for db in databases if db["name"] == "db2")
        assert db2_info["active"] is True

    def test_set_active_database_not_found(self):
        """Test error when setting non-existent database as active."""
        db_manager.create_database("db1")

        with pytest.raises(ValueError, match="not found"):
            db_manager.set_active_database("nonexistent")

    def test_list_databases(self):
        """Test listing all databases."""
        # Create databases with data
        db_manager.create_database("db1", set_active=True)
        db1 = db_manager.get_database("db1")
        db1.data["persons"] = [{"id": 1}, {"id": 2}]

        db_manager.create_database("db2")

        databases = db_manager.list_databases()

        assert len(databases) == 2
        assert all("name" in db for db in databases)
        assert all("path" in db for db in databases)
        assert all("active" in db for db in databases)
        assert all("person_count" in db for db in databases)

        # Check db1 has 2 persons
        db1_info = next(db for db in databases if db["name"] == "db1")
        assert db1_info["person_count"] == 2
        assert db1_info["active"] is True

    def test_delete_database_not_active(self):
        """Test deleting a non-active database."""
        db_manager.create_database("keep", set_active=True)
        db_manager.create_database("delete_me")

        assert len(db_manager.list_databases()) == 2

        # Delete non-active database
        db_manager.delete_database("delete_me", delete_files=False)

        assert len(db_manager.list_databases()) == 1
        assert db_manager.get_active_database_name() == "keep"

    def test_delete_active_database_raises_error(self):
        """Test that deleting active database raises error."""
        db_manager.create_database("active", set_active=True)

        with pytest.raises(ValueError, match="Cannot delete active database"):
            db_manager.delete_database("active")

    def test_delete_database_with_files(self):
        """Test deleting database and its files from disk."""
        db_name = "delete_with_files"
        db_manager.create_database(db_name)
        db_manager.create_database("keep", set_active=True)

        # Verify files exist
        db_path = Path(self.temp_dir) / f"{db_name}.gwb"
        assert db_path.exists()

        # Delete with files
        db_manager.delete_database(db_name, delete_files=True)

        # Verify files are gone
        assert not db_path.exists()

    def test_delete_database_not_found(self):
        """Test error when deleting non-existent database."""
        with pytest.raises(ValueError, match="not found"):
            db_manager.delete_database("nonexistent")

    def test_rename_database(self):
        """Test renaming a database in memory."""
        db_manager.create_database("old_name", set_active=True)
        db_manager.create_database("other_db")

        # Rename the database
        new_name = db_manager.rename_database(
            "old_name", "new_name", rename_files=False
        )

        assert new_name == "new_name"
        assert "new_name" in db_manager._databases
        assert "old_name" not in db_manager._databases
        assert db_manager.get_active_database_name() == "new_name"

        # Verify we can still access it
        db = db_manager.get_database("new_name")
        assert db is not None

    def test_rename_database_with_files(self):
        """Test renaming database and its files on disk."""
        db_name = "old_db_name"
        new_name = "new_db_name"

        db_manager.create_database(db_name, set_active=True)

        # Verify old files exist
        old_path = Path(self.temp_dir) / f"{db_name}.gwb"
        assert old_path.exists()

        # Rename with files
        result = db_manager.rename_database(db_name, new_name, rename_files=True)

        assert result == new_name

        # Verify new files exist and old files are gone
        new_path = Path(self.temp_dir) / f"{new_name}.gwb"
        assert new_path.exists()
        assert not old_path.exists()

    def test_rename_database_not_found(self):
        """Test error when renaming non-existent database."""
        with pytest.raises(ValueError, match="not found"):
            db_manager.rename_database("nonexistent", "new_name")

    def test_rename_database_name_already_exists(self):
        """Test error when new name already exists."""
        db_manager.create_database("db1")
        db_manager.create_database("db2")

        with pytest.raises(ValueError, match="already exists"):
            db_manager.rename_database("db1", "db2")

    def test_rename_database_empty_name(self):
        """Test error when new name is empty."""
        db_manager.create_database("db1")

        with pytest.raises(ValueError, match="cannot be empty"):
            db_manager.rename_database("db1", "")

    def test_close_specific_database(self):
        """Test closing a specific database."""
        db_manager.create_database("db1", set_active=True)
        db_manager.create_database("db2")

        assert len(db_manager.list_databases()) == 2

        # Close db2
        db_manager.close("db2")

        assert len(db_manager.list_databases()) == 1
        assert db_manager.get_active_database_name() == "db1"

    def test_close_active_database_switches_active(self):
        """Test that closing active database switches to another."""
        db_manager.create_database("db1", set_active=True)
        db_manager.create_database("db2")

        # Close active database
        db_manager.close("db1")

        # Should switch to db2
        assert db_manager.get_active_database_name() == "db2"

    def test_close_all_databases(self):
        """Test closing all databases."""
        db_manager.create_database("db1")
        db_manager.create_database("db2")
        db_manager.create_database("db3")

        assert len(db_manager.list_databases()) == 3

        db_manager.close_all()

        assert len(db_manager.list_databases()) == 0
        assert db_manager.get_active_database_name() is None

    def test_reload_specific_database(self):
        """Test reloading a specific database."""
        db_manager.create_database("reload_test", set_active=True)
        db = db_manager.get_database("reload_test")

        # Modify in memory (using base data which is actually saved/loaded)
        db.data["base"] = {"test_key": "value1"}
        assert db.data["base"]["test_key"] == "value1"

        # Save
        db.save()

        # Modify again without saving
        db.data["base"]["test_key"] = "value2"
        assert db.data["base"]["test_key"] == "value2"

        # Reload should discard unsaved changes
        db_manager.reload("reload_test")

        # After reload, the data should be restored to saved state
        assert db.data["base"]["test_key"] == "value1"

    def test_get_stats_for_specific_database(self):
        """Test getting stats for a specific database."""
        db_manager.create_database("stats_test", set_active=True)
        db = db_manager.get_database("stats_test")
        db.data["persons"] = [{"id": 1}, {"id": 2}, {"id": 3}]

        stats = db_manager.get_stats("stats_test")

        assert stats["name"] == "stats_test"
        assert stats["person_count"] == 3
        assert stats["active"] is True

    def test_backward_compatibility_initialize(self):
        """Test that old initialize() method still works."""
        # Old usage pattern
        db_path = str(Path(self.temp_dir) / "legacy_db")
        db_name = db_manager.initialize(db_path, create_if_missing=True)

        assert db_name == "legacy_db"
        assert db_manager.get_active_database_name() == "legacy_db"

        # Should be able to get database without name
        db = db_manager.get_database()
        assert db is not None


class TestMultiDatabaseAPI:
    """Tests for database router endpoints."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Setup and teardown for each test."""
        # Create temp directory
        self.temp_dir = tempfile.mkdtemp()

        # Reset database manager BEFORE creating TestClient
        db_manager._databases = {}
        db_manager._active_db_name = None
        db_manager._databases_dir = self.temp_dir

        # Create a default test database explicitly
        db_manager.create_database("default_test_db", set_active=True)

        yield

        # Cleanup
        db_manager.close_all()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @pytest.fixture
    def client(self):
        """Create a TestClient for API tests."""
        from uuid import UUID

        from geneweb.api.routers.database import get_security_context
        from geneweb.api.routers.persons import (
            get_security_context as get_security_context_persons,
        )
        from geneweb.api.security.auth import (
            Permission,
            SecurityContext,
            TokenData,
            UserRole,
        )

        # Mock security context for tests - bypass authentication
        def mock_get_security_context():
            return SecurityContext(
                user=TokenData(
                    user_id=UUID("00000000-0000-0000-0000-000000000001"),
                    username="test_admin",
                    role=UserRole.ADMIN,
                    permissions=[
                        Permission.VIEW_PUBLIC_PERSONS,
                        Permission.VIEW_FAMILY_PERSONS,
                        Permission.VIEW_ALL_PERSONS,
                        Permission.CREATE_PERSON,
                        Permission.UPDATE_ANY_PERSON,
                        Permission.DELETE_PERSON,
                        Permission.MANAGE_USERS,
                        Permission.SYSTEM_ADMIN,
                    ],
                ),
                ip_address="127.0.0.1",
                user_agent="TestClient",
            )

        # Override authentication dependencies
        app.dependency_overrides[get_security_context] = mock_get_security_context
        app.dependency_overrides[get_security_context_persons] = (
            mock_get_security_context
        )

        # Database is already initialized by setup_teardown
        # TestClient will use the existing database
        with TestClient(app) as test_client:
            yield test_client

        # Clean up overrides
        app.dependency_overrides.clear()

    def test_list_databases_endpoint(self, client):
        """Test GET /api/v1/database/databases endpoint."""
        response = client.get("/api/v1/database/databases")

        assert response.status_code == 200
        data = response.json()
        assert "databases" in data
        assert "active_database" in data
        assert isinstance(data["databases"], list)

    def test_get_active_database_endpoint(self, client):
        """Test GET /api/v1/database/databases/active endpoint."""
        response = client.get("/api/v1/database/databases/active")

        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "path" in data
        assert "active" in data
        assert data["active"] is True

    def test_create_database_endpoint(self, client):
        """Test POST /api/v1/database/databases endpoint."""
        payload = {"name": "new_test_db", "set_active": False}

        response = client.post("/api/v1/database/databases", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["database"]["name"] == "new_test_db"
        assert data["database"]["active"] is False

    def test_create_database_and_set_active_endpoint(self, client):
        """Test creating database and setting it as active."""
        payload = {"name": "active_db", "set_active": True}

        response = client.post("/api/v1/database/databases", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["database"]["active"] is True

        # Verify it's active
        response = client.get("/api/v1/database/databases/active")
        assert response.json()["name"] == "active_db"

    def test_activate_database_endpoint(self, client):
        """Test POST /api/v1/database/databases/{name}/activate endpoint."""
        # Create a database
        db_manager.create_database("switch_to_me")

        response = client.post("/api/v1/database/databases/switch_to_me/activate")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["active_database"] == "switch_to_me"

    def test_activate_nonexistent_database_endpoint(self, client):
        """Test activating non-existent database returns 404."""
        response = client.post("/api/v1/database/databases/nonexistent/activate")

        assert response.status_code == 404

    def test_rename_database_endpoint(self, client):
        """Test PUT /api/v1/database/databases/{name}/rename endpoint."""
        # Create a database to rename
        db_manager.create_database("old_name")

        payload = {"new_name": "renamed_db", "rename_files": False}
        response = client.put(
            "/api/v1/database/databases/old_name/rename", json=payload
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["old_name"] == "old_name"
        assert data["new_name"] == "renamed_db"
        assert data["files_renamed"] is False
        assert data["database"]["name"] == "renamed_db"

        # Verify old name no longer exists
        response = client.post("/api/v1/database/databases/old_name/activate")
        assert response.status_code == 404

        # Verify new name exists
        response = client.post("/api/v1/database/databases/renamed_db/activate")
        assert response.status_code == 200

    def test_rename_database_with_files_endpoint(self, client):
        """Test renaming database with files."""
        # Create a database to rename
        db_manager.create_database("file_db")
        db_manager.create_database("keep_active", set_active=True)

        payload = {"new_name": "renamed_file_db", "rename_files": True}
        response = client.put("/api/v1/database/databases/file_db/rename", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["files_renamed"] is True

    def test_rename_database_already_exists_endpoint(self, client):
        """Test renaming to an existing name returns 400."""
        db_manager.create_database("db1")
        db_manager.create_database("db2")

        payload = {"new_name": "db2", "rename_files": False}
        response = client.put("/api/v1/database/databases/db1/rename", json=payload)

        assert response.status_code == 400

    def test_rename_nonexistent_database_endpoint(self, client):
        """Test renaming non-existent database returns 404."""
        payload = {"new_name": "new_name", "rename_files": False}
        response = client.put(
            "/api/v1/database/databases/nonexistent/rename", json=payload
        )

        assert response.status_code == 404

    def test_delete_database_endpoint(self, client):
        """Test DELETE /api/v1/database/databases/{name} endpoint."""
        # Create database to delete
        db_manager.create_database("to_delete")

        response = client.delete(
            "/api/v1/database/databases/to_delete?delete_files=false"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["deleted_files"] is False

    def test_delete_active_database_endpoint_fails(self, client):
        """Test that deleting active database returns 400."""
        active_name = db_manager.get_active_database_name()

        response = client.delete(f"/api/v1/database/databases/{active_name}")

        assert response.status_code == 400

    def test_delete_database_with_files_endpoint(self, client):
        """Test deleting database with files."""
        # Create database to delete
        db_manager.create_database("delete_with_files")
        db_manager.create_database("keep_active", set_active=True)

        response = client.delete(
            "/api/v1/database/databases/delete_with_files?delete_files=true"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["deleted_files"] is True


class TestDatabaseUtilities:
    """Tests for database utility functions."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Setup and teardown for each test."""
        self.temp_dir = tempfile.mkdtemp()
        yield
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_list_available_databases(self):
        """Test listing available databases in a directory."""
        from geneweb.api.utils.database import list_available_databases

        # Create some databases
        db_manager._databases_dir = self.temp_dir
        db_manager.create_database("db1")
        db_manager.create_database("db2")
        db_manager.close_all()

        # List available
        available = list_available_databases(self.temp_dir)

        assert len(available) >= 2
        names = {db["name"] for db in available}
        assert "db1" in names
        assert "db2" in names

    def test_get_database_metadata(self):
        """Test getting database metadata."""
        from geneweb.api.utils.database import (
            create_new_database,
            get_database_metadata,
        )

        db_path = str(Path(self.temp_dir) / "meta_test")
        create_new_database(db_path)

        metadata = get_database_metadata(db_path)

        assert metadata["name"] == "meta_test"
        assert "size_bytes" in metadata
        assert "size_mb" in metadata
        assert metadata["exists"] is True

    def test_delete_database_files_utility(self):
        """Test deleting database files utility."""
        from geneweb.api.utils.database import (
            create_new_database,
            delete_database_files,
        )

        db_path = str(Path(self.temp_dir) / "to_delete")
        create_new_database(db_path)

        db_full_path = Path(f"{db_path}.gwb")
        assert db_full_path.exists()

        # Delete
        delete_database_files(db_path)

        assert not db_full_path.exists()
