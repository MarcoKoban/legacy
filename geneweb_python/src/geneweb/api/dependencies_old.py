"""
Dependency injection for API services with database connection.
"""

import os
from typing import Dict, Optional

import structlog

from ..db.database import Database

logger = structlog.get_logger(__name__)


class DatabaseManager:
    """Singleton manager for multiple database connections."""

    _instance: Optional["DatabaseManager"] = None
    _databases: Dict[str, Database] = {}
    _active_db_name: Optional[str] = None
    _databases_dir: str = ""

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._databases = {}
            cls._instance._active_db_name = None
        return cls._instance

    def initialize(self, db_path: Optional[str] = None, create_if_missing: bool = True):
        """
        Initialize database connection.

        Args:
            db_path: Path to database directory (without .gwb extension)
            create_if_missing: If True, create a new empty database if it doesn't exist

        Raises:
            FileNotFoundError: If database doesn't exist and create_if_missing is False
            RuntimeError: If database is already initialized
        """
        if self._database is not None:
            logger.warning("Database already initialized")
            return

        if db_path is None:
            # Default to data directory in project root
            db_path = os.environ.get(
                "GENEWEB_DB_PATH",
                os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                    "data",
                    "geneweb_db",
                ),
            )

        # Check if database exists
        db_full_path = db_path if db_path.endswith(".gwb") else db_path + ".gwb"
        db_exists = os.path.exists(db_full_path)

        if not db_exists and not create_if_missing:
            raise FileNotFoundError(
                f"Database not found at {db_full_path}. "
                f"Set create_if_missing=True to create a new database."
            )

        # Create parent directory if needed
        parent_dir = os.path.dirname(db_path)
        if parent_dir and not os.path.exists(parent_dir):
            logger.info("Creating parent directory", parent_dir=parent_dir)
            os.makedirs(parent_dir, exist_ok=True)

        logger.info(
            "Initializing GeneWeb database",
            db_path=db_path,
            exists=db_exists,
            creating_new=not db_exists and create_if_missing,
        )

        # Create Database instance (will create structure automatically)
        self._database = Database(db_path)

        # If new database, initialize with empty data and save
        if not db_exists and create_if_missing:
            logger.info("Creating new empty database")
            self._database.data["persons"] = []
            self._database.data["families"] = []
            self._database.data["unions"] = []
            self._database.data["couples"] = []
            self._database.data["descends"] = []
            self._database.save()
            logger.info("New database created successfully", db_path=db_full_path)

    def get_database(self) -> Database:
        """Get database instance."""
        if self._database is None:
            raise RuntimeError(
                "Database not initialized. Call initialize() first during app startup."
            )
        return self._database

    def close(self):
        """Close database connection and commit pending changes."""
        if self._database is not None:
            logger.info("Closing database connection")
            # Commit any pending patches
            try:
                if self._database.patch_manager.person_patches:
                    logger.info(
                        "Committing pending patches",
                        pending_persons=len(
                            self._database.patch_manager.person_patches
                        ),
                    )
                    self._database.commit_patches()
            except Exception as e:
                logger.warning("Error committing patches on close", error=str(e))
            self._database = None
            logger.info("Database connection closed")

    def reload(self):
        """Reload database from disk."""
        if self._database is not None:
            logger.info("Reloading database from disk")
            self._database.load()
            logger.info("Database reloaded successfully")
        else:
            raise RuntimeError("Database not initialized")

    def get_stats(self) -> dict:
        """
        Get database statistics.

        Returns:
            Dictionary with database stats (person count, family count, etc.)
        """
        if self._database is None:
            raise RuntimeError("Database not initialized")

        return {
            "db_path": self._database.dbdir,
            "person_count": len(self._database.data.get("persons", [])),
            "family_count": len(self._database.data.get("families", [])),
            "union_count": len(self._database.data.get("unions", [])),
            "couple_count": len(self._database.data.get("couples", [])),
            "descend_count": len(self._database.data.get("descends", [])),
            "pending_patches": len(self._database.patch_manager.person_patches),
            "read_only": self._database.read_only,
        }


# Global instance
db_manager = DatabaseManager()


def get_database() -> Database:
    """
    FastAPI dependency to get database instance.

    Usage in endpoints:
        @router.get("/persons")
        async def list_persons(db: Database = Depends(get_database)):
            persons = db.persons.get_all()
            ...
    """
    return db_manager.get_database()
