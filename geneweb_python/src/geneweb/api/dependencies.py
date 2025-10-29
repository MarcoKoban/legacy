"""
Dependency injection for API services with multi-database connection support.
"""

import os
import shutil
from typing import Dict, List, Optional
from uuid import UUID

import structlog

from ..db.database import Database

logger = structlog.get_logger(__name__)


class DatabaseMetadata:
    """Metadata for a database including ownership."""

    def __init__(self, name: str, db: Database, owner_id: Optional[UUID] = None):
        self.name = name
        self.db = db
        self.owner_id = owner_id  # UUID of the user who owns this database


class DatabaseManager:
    """Singleton manager for multiple database connections."""

    _instance: Optional["DatabaseManager"] = None
    _databases: Dict[str, DatabaseMetadata] = {}
    _active_db_name: Optional[str] = None
    _databases_dir: str = ""

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._databases = {}
            cls._instance._active_db_name = None
        return cls._instance

    def initialize(
        self, db_path: Optional[str] = None, create_if_missing: bool = True
    ) -> str:
        """
        Initialize default database connection (backward compatible).

        Args:
            db_path: Path to database directory (without .gwb extension)
            create_if_missing: If True, create a new empty database if it doesn't exist

        Returns:
            Name of the initialized database

        Raises:
            FileNotFoundError: If database doesn't exist and create_if_missing is False
        """
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

        # Set databases directory
        self._databases_dir = os.path.dirname(db_path) or "."

        # Extract database name from path
        db_name = os.path.basename(db_path).replace(".gwb", "")

        # Create or load the database
        return self.create_database(
            db_name, db_path, create_if_missing=create_if_missing, set_active=True
        )

    def create_database(
        self,
        name: str,
        db_path: Optional[str] = None,
        create_if_missing: bool = True,
        set_active: bool = False,
        owner_id: Optional[UUID] = None,
    ) -> str:
        """
        Create or load a database.

        Args:
            name: Name of the database
            db_path: Optional specific path for the database
            create_if_missing: If True, create database if it doesn't exist
            set_active: If True, set this database as active
            owner_id: UUID of the user who owns this database

        Returns:
            Database name

        Raises:
            FileNotFoundError: If database doesn't exist and create_if_missing is False
            ValueError: If database with this name already exists
        """
        # Check if database already loaded
        if name in self._databases:
            logger.warning(f"Database '{name}' already loaded")
            if set_active:
                self._active_db_name = name
            return name

        # Determine database path
        if db_path is None:
            if not self._databases_dir:
                self._databases_dir = os.environ.get(
                    "GENEWEB_DB_PATH",
                    os.path.join(
                        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                        "data",
                    ),
                )
            db_path = os.path.join(self._databases_dir, name)

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
            "Loading GeneWeb database",
            name=name,
            db_path=db_path,
            exists=db_exists,
            creating_new=not db_exists and create_if_missing,
        )

        # Create Database instance
        db = Database(db_path)

        # If new database, initialize with empty data and save
        if not db_exists and create_if_missing:
            logger.info("Creating new empty database", name=name)
            db.data["persons"] = []
            db.data["families"] = []
            db.data["unions"] = []
            db.data["couples"] = []
            db.data["descends"] = []
            db.save()
            logger.info(
                "New database created successfully", name=name, db_path=db_full_path
            )

        # Store database with metadata
        metadata = DatabaseMetadata(name=name, db=db, owner_id=owner_id)
        self._databases[name] = metadata

        # Set as active if requested or if it's the first database
        if set_active or self._active_db_name is None:
            self._active_db_name = name
            logger.info(
                "Set active database",
                name=name,
                owner_id=str(owner_id) if owner_id else None,
            )

        return name

    def get_database(self, name: Optional[str] = None) -> Database:
        """
        Get database instance.

        Args:
            name: Name of database to get. If None, returns active database.

        Returns:
            Database instance

        Raises:
            RuntimeError: If no database is initialized or name not found
        """
        if name is None:
            if self._active_db_name is None:
                raise RuntimeError(
                    "No active database. Call initialize() first during app startup."
                )
            name = self._active_db_name

        if name not in self._databases:
            raise RuntimeError(
                f"Database '{name}' not found. Available:{list(self._databases.keys())}"
            )

        return self._databases[name].db

    def set_active_database(self, name: str) -> None:
        """
        Set active database.

        Args:
            name: Name of database to set as active

        Raises:
            ValueError: If database name not found
        """
        if name not in self._databases:
            raise ValueError(
                f"Database '{name}' not found. Available:{list(self._databases.keys())}"
            )

        self._active_db_name = name
        logger.info("Active database changed", name=name)

    def get_active_database_name(self) -> Optional[str]:
        """Get name of active database."""
        return self._active_db_name

    def list_databases(
        self, user_id: Optional[UUID] = None, is_admin: bool = False
    ) -> List[Dict[str, any]]:
        """
        List databases accessible to a user.

        Args:
            user_id: UUID of the user. If None, returns all databases
            is_admin: If True, user can see all databases

        Returns:
            List of database info dictionaries
        """
        result = []
        for name, metadata in self._databases.items():
            # Admin can see all databases
            # Regular users can only see their own databases
            if (
                is_admin
                or user_id is None
                or metadata.owner_id is None
                or metadata.owner_id == user_id
            ):
                result.append(
                    {
                        "name": name,
                        "path": metadata.db.dbdir,
                        "active": name == self._active_db_name,
                        "person_count": len(metadata.db.data.get("persons", [])),
                        "family_count": len(metadata.db.data.get("families", [])),
                        "read_only": metadata.db.read_only,
                        "pending_patches": len(
                            metadata.db.patch_manager.person_patches
                        ),
                        "owner_id": (
                            str(metadata.owner_id) if metadata.owner_id else None
                        ),
                    }
                )
        return result

    def can_access_database(
        self, db_name: str, user_id: UUID, is_admin: bool = False
    ) -> bool:
        """
        Check if a user can access a database.

        Args:
            db_name: Name of the database
            user_id: UUID of the user
            is_admin: If True, user has admin privileges

        Returns:
            True if user can access the database
        """
        if db_name not in self._databases:
            return False

        metadata = self._databases[db_name]

        # Admin can access all databases
        if is_admin:
            return True

        # Database without owner can be accessed by anyone (legacy databases)
        if metadata.owner_id is None:
            return True

        # User can access their own databases
        return metadata.owner_id == user_id

    def rename_database(
        self, old_name: str, new_name: str, rename_files: bool = False
    ) -> str:
        """
        Rename a database.

        Args:
            old_name: Current name of the database
            new_name: New name for the database
            rename_files: If True, also rename database files on disk

        Returns:
            New database name

        Raises:
            ValueError: If old name not found, new name already exists,
            or other validation errors
        """
        # Validate old database exists
        if old_name not in self._databases:
            raise ValueError(f"Database '{old_name}' not found")

        # Validate new name doesn't already exist
        if new_name in self._databases:
            raise ValueError(f"Database '{new_name}' already exists")

        # Validate new name is not empty
        if not new_name or not new_name.strip():
            raise ValueError("New database name cannot be empty")

        metadata = self._databases[old_name]
        old_path = metadata.db.dbdir

        logger.info(
            "Renaming database",
            old_name=old_name,
            new_name=new_name,
            rename_files=rename_files,
        )

        # Rename files on disk if requested
        if rename_files:
            old_db_path = old_path if old_path.endswith(".gwb") else old_path + ".gwb"

            # Commit pending changes before renaming
            try:
                if metadata.db.patch_manager.person_patches:
                    logger.info(
                        "Committing pending patches before rename", name=old_name
                    )
                    metadata.db.commit_patches()
            except Exception as e:
                logger.warning(
                    "Error committing patches before rename",
                    name=old_name,
                    error=str(e),
                )

            if os.path.exists(old_db_path):
                # Construct new path
                new_path = os.path.join(os.path.dirname(old_path), new_name)
                new_db_path = (
                    new_path if new_path.endswith(".gwb") else new_path + ".gwb"
                )

                # Rename directory
                logger.info(
                    "Renaming database files",
                    old_path=old_db_path,
                    new_path=new_db_path,
                )
                os.rename(old_db_path, new_db_path)

                # Update database object path
                metadata.db.dbdir = new_path
            else:
                logger.warning(
                    "Database files not found on disk, only renaming in memory",
                    path=old_db_path,
                )

        # Update metadata name
        metadata.name = new_name

        # Update in-memory reference
        self._databases[new_name] = self._databases.pop(old_name)

        # Update active database name if this was the active one
        if self._active_db_name == old_name:
            self._active_db_name = new_name
            logger.info("Updated active database name", new_name=new_name)

        logger.info(
            "Database renamed successfully",
            old_name=old_name,
            new_name=new_name,
            files_renamed=rename_files,
        )

        return new_name

    def delete_database(self, name: str, delete_files: bool = False) -> None:
        """
        Delete a database.

        Args:
            name: Name of database to delete
            delete_files: If True, also delete database files from disk

        Raises:
            ValueError: If database name not found or is active
        """
        if name not in self._databases:
            raise ValueError(f"Database '{name}' not found")

        if name == self._active_db_name:
            raise ValueError(
                f"Cannot delete active database '{name}'. "
                f"Switch to another database first."
            )

        metadata = self._databases[name]
        db = metadata.db

        # Commit any pending changes before deletion
        try:
            if db.patch_manager.person_patches:
                logger.info("Committing pending patches before deletion", name=name)
                db.commit_patches()
        except Exception as e:
            logger.warning(
                "Error committing patches before deletion", name=name, error=str(e)
            )

        # Delete files if requested
        if delete_files:
            db_path = db.dbdir if db.dbdir.endswith(".gwb") else db.dbdir + ".gwb"
            if os.path.exists(db_path):
                logger.info("Deleting database files", name=name, path=db_path)
                shutil.rmtree(db_path)

        # Remove from memory
        del self._databases[name]
        logger.info("Database removed", name=name, deleted_files=delete_files)

    def close(self, name: Optional[str] = None) -> None:
        """
        Close database connection and commit pending changes.

        Args:
            name: Name of database to close. If None, closes active database.
        """
        if name is None:
            name = self._active_db_name

        if name is None or name not in self._databases:
            logger.warning("No database to close", name=name)
            return

        metadata = self._databases[name]
        db = metadata.db
        logger.info("Closing database connection", name=name)

        # Commit any pending patches
        try:
            if db.patch_manager.person_patches:
                logger.info(
                    "Committing pending patches",
                    name=name,
                    pending_persons=len(db.patch_manager.person_patches),
                )
                db.commit_patches()
        except Exception as e:
            logger.warning("Error committing patches on close", name=name, error=str(e))

        # Remove from databases dict
        del self._databases[name]

        # Reset active if this was the active database
        if name == self._active_db_name:
            # Set another database as active if available
            if self._databases:
                self._active_db_name = list(self._databases.keys())[0]
                logger.info(
                    "Active database changed after close", name=self._active_db_name
                )
            else:
                self._active_db_name = None

        logger.info("Database connection closed", name=name)

    def close_all(self) -> None:
        """Close all database connections."""
        db_names = list(self._databases.keys())
        for name in db_names:
            self.close(name)
        logger.info("All database connections closed")

    def reload(self, name: Optional[str] = None) -> None:
        """
        Reload database from disk.

        Args:
            name: Name of database to reload. If None, reloads active database.
        """
        if name is None:
            name = self._active_db_name

        if name is None or name not in self._databases:
            raise RuntimeError(f"Database '{name}' not found")

        metadata = self._databases[name]
        db = metadata.db
        logger.info("Reloading database from disk", name=name)
        db.load()
        logger.info("Database reloaded successfully", name=name)

    def get_stats(self, name: Optional[str] = None) -> dict:
        """
        Get database statistics.

        Args:
            name: Name of database. If None, gets stats for active database.

        Returns:
            Dictionary with database stats (person count, family count, etc.)
        """
        if name is None:
            name = self._active_db_name

        if name is None or name not in self._databases:
            raise RuntimeError(f"Database '{name}' not found")

        metadata = self._databases[name]
        db = metadata.db

        return {
            "name": name,
            "db_path": db.dbdir,
            "person_count": len(db.data.get("persons", [])),
            "family_count": len(db.data.get("families", [])),
            "union_count": len(db.data.get("unions", [])),
            "couple_count": len(db.data.get("couples", [])),
            "descend_count": len(db.data.get("descends", [])),
            "pending_patches": len(db.patch_manager.person_patches),
            "read_only": db.read_only,
            "active": name == self._active_db_name,
        }


# Global instance
db_manager = DatabaseManager()


def get_database() -> Database:
    """
    FastAPI dependency to get active database instance.

    Usage in endpoints:
        @router.get("/persons")
        async def list_persons(db: Database = Depends(get_database)):
            persons = db.persons.get_all()
            ...
    """
    return db_manager.get_database()
