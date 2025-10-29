"""
Utility functions for database management.
"""

import os
from typing import Optional

import structlog

from ...db.database import Database

logger = structlog.get_logger(__name__)


def create_new_database(
    db_path: str,
    initial_persons: Optional[list] = None,
    initial_families: Optional[list] = None,
    overwrite: bool = False,
) -> Database:
    """
    Create a new GeneWeb database.

    Args:
        db_path: Path to database directory (without .gwb extension)
        initial_persons: Optional list of initial persons to add
        initial_families: Optional list of initial families to add
        overwrite: If True, overwrite existing database

    Returns:
        Database instance

    Raises:
        FileExistsError: If database exists and overwrite is False

    Example:
        >>> db = create_new_database("/path/to/my_family")
        >>> # Database created at /path/to/my_family.gwb
    """
    db_full_path = db_path if db_path.endswith(".gwb") else db_path + ".gwb"

    # Check if database already exists
    if os.path.exists(db_full_path) and not overwrite:
        raise FileExistsError(
            f"Database already exists at {db_full_path}. "
            f"Set overwrite=True to replace it."
        )

    logger.info(
        "Creating new database",
        db_path=db_path,
        overwrite=overwrite,
    )

    # Create parent directory if needed
    parent_dir = os.path.dirname(db_path)
    if parent_dir and not os.path.exists(parent_dir):
        os.makedirs(parent_dir, exist_ok=True)

    # Create Database instance (creates directory structure automatically)
    db = Database(db_path)

    # Initialize with empty or provided data
    db.data["persons"] = initial_persons or []
    db.data["families"] = initial_families or []
    db.data["unions"] = []
    db.data["couples"] = []
    db.data["descends"] = []

    # Save to disk
    db.save()

    logger.info(
        "Database created successfully",
        db_path=db_full_path,
        person_count=len(db.data["persons"]),
        family_count=len(db.data["families"]),
    )

    return db


def load_database(db_path: str, read_only: bool = False) -> Database:
    """
    Load an existing GeneWeb database.

    Args:
        db_path: Path to database directory (without .gwb extension)
        read_only: If True, open database in read-only mode

    Returns:
        Database instance

    Raises:
        FileNotFoundError: If database doesn't exist

    Example:
        >>> db = load_database("/path/to/my_family", read_only=True)
    """
    db_full_path = db_path if db_path.endswith(".gwb") else db_path + ".gwb"

    if not os.path.exists(db_full_path):
        raise FileNotFoundError(f"Database not found at {db_full_path}")

    logger.info("Loading database", db_path=db_path, read_only=read_only)

    db = Database(db_path, read_only=read_only)
    db.load()

    logger.info(
        "Database loaded successfully",
        db_path=db_full_path,
        person_count=len(db.data.get("persons", [])),
        family_count=len(db.data.get("families", [])),
    )

    return db


def backup_database(db_path: str, backup_path: Optional[str] = None) -> str:
    """
    Create a backup of a GeneWeb database.

    Args:
        db_path: Path to database directory (without .gwb extension)
        backup_path: Optional backup path. If None, adds .backup suffix

    Returns:
        Path to backup database

    Example:
        >>> backup = backup_database("/path/to/my_family")
        >>> # Backup created at /path/to/my_family.backup.gwb
    """
    import shutil

    db_full_path = db_path if db_path.endswith(".gwb") else db_path + ".gwb"

    if not os.path.exists(db_full_path):
        raise FileNotFoundError(f"Database not found at {db_full_path}")

    if backup_path is None:
        backup_path = db_path + ".backup"

    backup_full_path = (
        backup_path if backup_path.endswith(".gwb") else backup_path + ".gwb"
    )

    logger.info(
        "Creating database backup",
        source=db_full_path,
        destination=backup_full_path,
    )

    # Copy entire directory
    if os.path.exists(backup_full_path):
        shutil.rmtree(backup_full_path)
    shutil.copytree(db_full_path, backup_full_path)

    logger.info("Backup created successfully", backup_path=backup_full_path)

    return backup_full_path


def validate_database(db_path: str) -> dict:
    """
    Validate database integrity and structure.

    Args:
        db_path: Path to database directory (without .gwb extension)

    Returns:
        Dictionary with validation results

    Example:
        >>> result = validate_database("/path/to/my_family")
        >>> print(result["valid"])  # True if database is valid
    """
    db_full_path = db_path if db_path.endswith(".gwb") else db_path + ".gwb"

    validation = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "db_path": db_full_path,
    }

    # Check if database directory exists
    if not os.path.exists(db_full_path):
        validation["valid"] = False
        validation["errors"].append(f"Database directory not found: {db_full_path}")
        return validation

    # Check for required subdirectories
    required_dirs = ["notes_d", "wiznotes"]
    for dir_name in required_dirs:
        dir_path = os.path.join(db_full_path, dir_name)
        if not os.path.exists(dir_path):
            validation["warnings"].append(f"Missing directory: {dir_name}")

    # Check for base files
    base_file = os.path.join(db_full_path, "base")
    if not os.path.exists(base_file):
        validation["warnings"].append("Missing base file (database may be empty)")

    # Try to load database
    try:
        db = Database(db_path)
        db.load()

        # Validate data structure
        if "persons" not in db.data:
            validation["warnings"].append("No persons data found")
        if "families" not in db.data:
            validation["warnings"].append("No families data found")

        validation["person_count"] = len(db.data.get("persons", []))
        validation["family_count"] = len(db.data.get("families", []))

    except Exception as e:
        validation["valid"] = False
        validation["errors"].append(f"Failed to load database: {str(e)}")

    logger.info(
        "Database validation completed",
        db_path=db_full_path,
        valid=validation["valid"],
        errors=len(validation["errors"]),
        warnings=len(validation["warnings"]),
    )

    return validation


def list_available_databases(databases_dir: str) -> list:
    """
    List all available databases in a directory.

    Args:
        databases_dir: Directory to scan for databases

    Returns:
        List of dictionaries with database information

    Example:
        >>> dbs = list_available_databases("/path/to/databases")
        >>> for db in dbs:
        ...     print(db["name"], db["path"])
    """
    if not os.path.exists(databases_dir):
        logger.warning("Databases directory not found", path=databases_dir)
        return []

    databases = []

    try:
        # List all .gwb directories
        for item in os.listdir(databases_dir):
            item_path = os.path.join(databases_dir, item)

            # Check if it's a directory ending with .gwb
            if os.path.isdir(item_path) and item.endswith(".gwb"):
                db_name = item.replace(".gwb", "")

                # Get basic info
                try:
                    base_file = os.path.join(item_path, "base")
                    exists = os.path.exists(base_file)

                    # Try to get size
                    size = 0
                    if exists:
                        size = os.path.getsize(base_file)

                    databases.append(
                        {
                            "name": db_name,
                            "path": item_path,
                            "exists": exists,
                            "size_bytes": size,
                        }
                    )
                except Exception as e:
                    logger.warning(
                        "Error reading database info", name=db_name, error=str(e)
                    )

        logger.info(
            "Listed available databases", directory=databases_dir, count=len(databases)
        )
    except Exception as e:
        logger.error("Error listing databases", directory=databases_dir, error=str(e))

    return databases


def delete_database_files(db_path: str) -> bool:
    """
    Delete database files from disk.

    Args:
        db_path: Path to database directory (without .gwb extension)

    Returns:
        True if deletion was successful

    Raises:
        FileNotFoundError: If database doesn't exist

    Example:
        >>> delete_database_files("/path/to/my_family")
    """
    import shutil

    db_full_path = db_path if db_path.endswith(".gwb") else db_path + ".gwb"

    if not os.path.exists(db_full_path):
        raise FileNotFoundError(f"Database not found at {db_full_path}")

    logger.info("Deleting database files", db_path=db_full_path)

    try:
        shutil.rmtree(db_full_path)
        logger.info("Database files deleted successfully", db_path=db_full_path)
        return True
    except Exception as e:
        logger.error(
            "Failed to delete database files", db_path=db_full_path, error=str(e)
        )
        raise


def get_database_metadata(db_path: str) -> dict:
    """
    Get metadata about a database without fully loading it.

    Args:
        db_path: Path to database directory (without .gwb extension)

    Returns:
        Dictionary with database metadata

    Example:
        >>> meta = get_database_metadata("/path/to/my_family")
        >>> print(meta["size_mb"], meta["last_modified"])
    """
    import time

    db_full_path = db_path if db_path.endswith(".gwb") else db_path + ".gwb"

    if not os.path.exists(db_full_path):
        raise FileNotFoundError(f"Database not found at {db_full_path}")

    metadata = {
        "path": db_full_path,
        "name": os.path.basename(db_path).replace(".gwb", ""),
        "exists": True,
    }

    try:
        # Get directory size
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(db_full_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)

        metadata["size_bytes"] = total_size
        metadata["size_mb"] = round(total_size / (1024 * 1024), 2)

        # Get last modification time
        base_file = os.path.join(db_full_path, "base")
        if os.path.exists(base_file):
            mtime = os.path.getmtime(base_file)
            metadata["last_modified"] = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(mtime)
            )
            metadata["last_modified_timestamp"] = int(mtime)

        # Count files
        file_count = sum(len(files) for _, _, files in os.walk(db_full_path))
        metadata["file_count"] = file_count

    except Exception as e:
        logger.warning(
            "Error getting database metadata", db_path=db_full_path, error=str(e)
        )
        metadata["error"] = str(e)

    return metadata
