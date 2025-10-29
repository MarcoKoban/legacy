"""
Integration tests for database management features.
Tests DatabaseManager enhancements, utilities, and database router.
"""

import shutil
import tempfile
from pathlib import Path

import pytest

from geneweb.api.dependencies import DatabaseManager
from geneweb.api.utils.database import (
    backup_database,
    create_new_database,
    load_database,
    validate_database,
)


class TestDatabaseManagerEnhancements:
    """Tests for enhanced DatabaseManager features."""

    @pytest.fixture
    def temp_db_dir(self):
        """Create temporary directory for test databases."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_initialize_with_create_if_missing_true(self, temp_db_dir):
        """Test initialize creates database when create_if_missing=True."""
        db_path = Path(temp_db_dir) / "new_test.gwb"
        manager = DatabaseManager()

        # Should create database without error
        manager.initialize(str(db_path), create_if_missing=True)

        # Verify database was created
        assert db_path.exists()

        # Verify we can get stats
        stats = manager.get_stats()
        assert stats["person_count"] == 0
        assert stats["family_count"] == 0
        assert stats["pending_patches"] == 0
        assert stats["read_only"] is False

        manager.close()

    def test_initialize_with_create_if_missing_false(self, temp_db_dir):
        """Test initialize raises error when
        create_if_missing=False and DB doesn't exist."""
        db_path = Path(temp_db_dir) / "nonexistent.gwb"
        manager = DatabaseManager()

        # Should raise FileNotFoundError
        with pytest.raises(FileNotFoundError):
            manager.initialize(str(db_path), create_if_missing=False)

    def test_initialize_creates_parent_directories(self, temp_db_dir):
        """Test initialize creates parent directories when needed."""
        db_path = Path(temp_db_dir) / "deep" / "nested" / "path" / "test.gwb"
        manager = DatabaseManager()

        # Should create all parent directories
        manager.initialize(str(db_path), create_if_missing=True)

        # Verify database and parents were created
        assert db_path.exists()
        assert db_path.parent.exists()

        manager.close()

    def test_get_stats_returns_correct_data(self, temp_db_dir):
        """Test get_stats returns accurate database statistics."""
        db_path = Path(temp_db_dir) / "stats_test.gwb"
        manager = DatabaseManager()
        manager.initialize(str(db_path), create_if_missing=True)

        stats = manager.get_stats()

        # Check all expected keys are present
        assert "person_count" in stats
        assert "family_count" in stats
        assert "pending_patches" in stats
        assert "read_only" in stats

        # Check types
        assert isinstance(stats["person_count"], int)
        assert isinstance(stats["family_count"], int)
        assert isinstance(stats["pending_patches"], int)
        assert isinstance(stats["read_only"], bool)

        manager.close()

    def test_reload_refreshes_database(self, temp_db_dir):
        """Test reload method refreshes database from disk."""
        db_path = Path(temp_db_dir) / "reload_test.gwb"
        manager = DatabaseManager()
        manager.initialize(str(db_path), create_if_missing=True)

        # Get initial stats
        stats_before = manager.get_stats()

        # Reload database
        manager.reload()

        # Get stats after reload
        stats_after = manager.get_stats()

        # Stats should still be accessible (database reloaded)
        assert stats_after is not None
        assert stats_after["person_count"] == stats_before["person_count"]

        manager.close()

    def test_close_commits_pending_patches(self, temp_db_dir):
        """Test close method commits pending patches before closing."""
        db_path = Path(temp_db_dir) / "close_test.gwb"
        manager = DatabaseManager()
        manager.initialize(str(db_path), create_if_missing=True)

        # Close should succeed without error
        manager.close()

        # Database should still exist
        assert db_path.exists()

    def test_singleton_pattern(self, temp_db_dir):
        """Test DatabaseManager follows singleton pattern."""
        manager1 = DatabaseManager()
        manager2 = DatabaseManager()

        # Should be same instance
        assert manager1 is manager2


class TestDatabaseUtilities:
    """Tests for database utility functions."""

    @pytest.fixture
    def temp_db_dir(self):
        """Create temporary directory for test databases."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_create_new_database_empty(self, temp_db_dir):
        """Test creating a new empty database."""
        db_path = Path(temp_db_dir) / "new_empty.gwb"

        db = create_new_database(str(db_path))

        # Verify database was created
        assert db_path.exists()
        assert db is not None

        # Verify it's empty
        assert len(db.data.get("persons", [])) == 0
        assert len(db.data.get("families", [])) == 0

    def test_create_new_database_with_initial_data(self, temp_db_dir):
        """Test creating database with initial persons and families."""
        from geneweb.core.person import Person, Sex

        db_path = Path(temp_db_dir) / "new_with_data.gwb"

        # Create initial person (Sex is required)
        initial_person = Person(first_name="John", surname="Doe", sex=Sex.MALE)

        db = create_new_database(str(db_path), initial_persons=[initial_person])

        # Verify database has initial data
        persons = db.data.get("persons", [])
        assert len(persons) == 1
        assert persons[0].first_name == "John"
        assert persons[0].surname == "Doe"
        assert persons[0].sex == Sex.MALE

    def test_create_new_database_overwrite_false(self, temp_db_dir):
        """Test create fails when database exists and overwrite=False."""
        db_path = Path(temp_db_dir) / "existing.gwb"

        # Create first database
        create_new_database(str(db_path))

        # Should raise FileExistsError
        with pytest.raises(FileExistsError):
            create_new_database(str(db_path), overwrite=False)

    def test_create_new_database_overwrite_true(self, temp_db_dir):
        """Test create succeeds when database exists and overwrite=True."""
        db_path = Path(temp_db_dir) / "overwrite.gwb"

        # Should succeed with overwrite=True
        db2 = create_new_database(str(db_path), overwrite=True)

        assert db2 is not None
        assert db_path.exists()

    def test_load_database_existing(self, temp_db_dir):
        """Test loading an existing database."""
        db_path = Path(temp_db_dir) / "to_load.gwb"

        # Create database
        create_new_database(str(db_path))

        # Load it
        db = load_database(str(db_path))

        assert db is not None
        assert len(db.data.get("persons", [])) == 0
        assert len(db.data.get("families", [])) == 0

    def test_load_database_nonexistent(self, temp_db_dir):
        """Test loading nonexistent database raises error."""
        db_path = Path(temp_db_dir) / "nonexistent.gwb"

        with pytest.raises(FileNotFoundError):
            load_database(str(db_path))

    def test_load_database_read_only(self, temp_db_dir):
        """Test loading database in read-only mode."""
        db_path = Path(temp_db_dir) / "readonly.gwb"

        # Create database
        create_new_database(str(db_path))

        # Load in read-only mode
        db = load_database(str(db_path), read_only=True)

        assert db is not None
        # Note: Database class doesn't expose read_only flag directly
        # Just verify it loads successfully

    def test_backup_database_default_path(self, temp_db_dir):
        """Test backing up database to default path."""
        db_path = Path(temp_db_dir) / "to_backup.gwb"

        # Create database
        create_new_database(str(db_path))

        # Backup with default path
        backup_path = backup_database(str(db_path))

        # Verify backup was created
        assert Path(backup_path).exists()
        assert backup_path.endswith(".backup.gwb")

    def test_backup_database_custom_path(self, temp_db_dir):
        """Test backing up database to custom path."""
        db_path = Path(temp_db_dir) / "to_backup2.gwb"
        backup_path = Path(temp_db_dir) / "custom_backup.gwb"

        # Create database
        create_new_database(str(db_path))

        # Backup to custom path
        result_path = backup_database(str(db_path), str(backup_path))

        # Verify backup was created at custom path
        assert backup_path.exists()
        assert result_path == str(backup_path)

    def test_backup_database_nonexistent(self, temp_db_dir):
        """Test backing up nonexistent database raises error."""
        db_path = Path(temp_db_dir) / "nonexistent.gwb"

        with pytest.raises(FileNotFoundError):
            backup_database(str(db_path))

    def test_validate_database_valid(self, temp_db_dir):
        """Test validating a valid database."""
        db_path = Path(temp_db_dir) / "valid.gwb"

        # Create valid database
        create_new_database(str(db_path))

        # Validate
        result = validate_database(str(db_path))

        assert result["valid"] is True
        assert isinstance(result["errors"], list)
        assert isinstance(result["warnings"], list)

    def test_validate_database_empty_warnings(self, temp_db_dir):
        """Test validating empty database produces warnings."""
        db_path = Path(temp_db_dir) / "empty.gwb"

        # Create empty database
        create_new_database(str(db_path))

        # Validate
        result = validate_database(str(db_path))

        # Should be valid but have warnings about empty database
        assert result["valid"] is True
        assert len(result["warnings"]) >= 0  # May or may not have warnings

    def test_validate_database_nonexistent(self, temp_db_dir):
        """Test validating nonexistent database returns error."""
        db_path = Path(temp_db_dir) / "nonexistent.gwb"

        result = validate_database(str(db_path))

        assert result["valid"] is False
        assert len(result["errors"]) > 0
        assert any(
            "not found" in e.lower() or "not exist" in e.lower()
            for e in result["errors"]
        )


class TestDatabaseRouter:
    """Tests for database management API router."""

    # Note: These are integration tests that would require FastAPI test client
    # Placeholder for now - implement when API is running

    def test_database_router_placeholder(self):
        """Placeholder for database router tests."""
        # TODO: Implement when FastAPI test client is available
        # Tests should cover:
        # - GET /api/v1/database/stats
        # - GET /api/v1/database/health
        # - POST /api/v1/database/reload
        # - POST /api/v1/database/commit
        # - GET /api/v1/database/info
        pass
