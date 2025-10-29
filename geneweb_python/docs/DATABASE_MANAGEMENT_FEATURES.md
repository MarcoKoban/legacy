# Database Management Features

## Overview

This document describes the enhanced database management capabilities added to the GeneWeb API. These features provide better control over database initialization, utilities for common operations, and dedicated API endpoints for database management.

## Table of Contents

1. [Enhanced DatabaseManager](#enhanced-databasemanager)
2. [Database Utilities](#database-utilities)
3. [Database Management Router](#database-management-router)
4. [Testing](#testing)
5. [Usage Examples](#usage-examples)

---

## Enhanced DatabaseManager

The `DatabaseManager` class (in `src/geneweb/api/dependencies.py`) has been enhanced with new features for better database control.

### New Features

#### 1. Controlled Database Creation

```python
def initialize(
    self, 
    db_path: str, 
    read_only: bool = False, 
    create_if_missing: bool = True
)
```

**Parameters:**
- `db_path`: Path to the database file (`.gwb`)
- `read_only`: Whether to open in read-only mode (default: `False`)
- `create_if_missing`: Whether to create database if it doesn't exist (default: `True`)

**Behavior:**
- When `create_if_missing=True`: 
  - Creates parent directories if needed
  - Initializes empty database if file doesn't exist
  - No error if database already exists
  
- When `create_if_missing=False`:
  - Raises `FileNotFoundError` if database doesn't exist
  - Only opens existing databases

**Example:**
```python
from src.geneweb.api.dependencies import DatabaseManager

# Create database if missing (default)
manager = DatabaseManager()
manager.initialize("path/to/database.gwb")

# Only open existing databases
manager.initialize("path/to/database.gwb", create_if_missing=False)
```

#### 2. Database Statistics

```python
def get_stats(self) -> Dict[str, Any]
```

Returns comprehensive database statistics:

```python
{
    "person_count": 150,      # Number of persons
    "family_count": 80,       # Number of families
    "pending_patches": 0,     # Uncommitted changes
    "read_only": False        # Database mode
}
```

#### 3. Database Reload

```python
def reload(self)
```

Reloads the database from disk, refreshing all data without closing the connection.

**Use cases:**
- After external modifications to database files
- Recovering from errors
- Refreshing cached data

#### 4. Improved Close

```python
def close(self)
```

Enhanced to commit pending patches before closing with better logging and error handling.

---

## Database Utilities

New utility functions in `src/geneweb/api/utils/database.py` provide common database operations.

### 1. Create New Database

```python
def create_new_database(
    db_path: str,
    initial_persons: Optional[List[Person]] = None,
    initial_families: Optional[List[Family]] = None,
    overwrite: bool = False
) -> Database
```

Creates a new GeneWeb database with optional initial data.

**Parameters:**
- `db_path`: Path for new database
- `initial_persons`: Optional list of persons to add
- `initial_families`: Optional list of families to add
- `overwrite`: Whether to overwrite existing database

**Returns:** Initialized `Database` object

**Example:**
```python
from src.geneweb.api.utils.database import create_new_database
from src.geneweb.core.person import Person, Sex

# Create empty database
db = create_new_database("family_tree.gwb")

# Create with initial data
initial_person = Person(
    first_name="John",
    surname="Doe",
    sex=Sex.MALE
)
db = create_new_database(
    "family_tree.gwb",
    initial_persons=[initial_person],
    overwrite=True
)
```

### 2. Load Database

```python
def load_database(
    db_path: str,
    read_only: bool = False
) -> Database
```

Loads an existing database.

**Parameters:**
- `db_path`: Path to database file
- `read_only`: Open in read-only mode

**Returns:** Loaded `Database` object

**Raises:** `FileNotFoundError` if database doesn't exist

**Example:**
```python
from src.geneweb.api.utils.database import load_database

# Load database
db = load_database("family_tree.gwb")

# Load read-only
db = load_database("family_tree.gwb", read_only=True)
```

### 3. Backup Database

```python
def backup_database(
    db_path: str,
    backup_path: Optional[str] = None
) -> str
```

Creates a backup copy of a database.

**Parameters:**
- `db_path`: Path to database to backup
- `backup_path`: Optional custom backup path (default: `{db_path}.backup.gwb`)

**Returns:** Path to backup file

**Example:**
```python
from src.geneweb.api.utils.database import backup_database

# Backup with default name
backup_path = backup_database("family_tree.gwb")
# Creates: family_tree.backup.gwb

# Backup with custom name
backup_path = backup_database(
    "family_tree.gwb",
    "backups/family_tree_2024_01_15.gwb"
)
```

### 4. Validate Database

```python
def validate_database(db_path: str) -> Dict[str, Any]
```

Validates database structure and integrity.

**Parameters:**
- `db_path`: Path to database to validate

**Returns:** Validation result dictionary:
```python
{
    "valid": True,           # Overall validity
    "errors": [],            # List of errors (strings)
    "warnings": []           # List of warnings (strings)
}
```

**Example:**
```python
from src.geneweb.api.utils.database import validate_database

result = validate_database("family_tree.gwb")

if result["valid"]:
    print("✓ Database is valid")
    if result["warnings"]:
        print(f"Warnings: {result['warnings']}")
else:
    print(f"✗ Database has errors: {result['errors']}")
```

---

## Database Management Router

New API endpoints in `src/geneweb/api/routers/database.py` provide HTTP access to database management operations.

### Endpoints

#### 1. Get Database Statistics

```http
GET /api/v1/database/stats
```

Returns database statistics.

**Response:**
```json
{
    "person_count": 150,
    "family_count": 80,
    "pending_patches": 0,
    "read_only": false
}
```

#### 2. Database Health Check

```http
GET /api/v1/database/health
```

Checks database health and returns detailed status.

**Response:**
```json
{
    "status": "healthy",
    "message": "Database is operational",
    "stats": {
        "person_count": 150,
        "family_count": 80,
        "pending_patches": 0,
        "read_only": false
    }
}
```

**Status values:**
- `healthy`: Database is operational
- `unhealthy`: Database has issues
- `read_only`: Database is in read-only mode

#### 3. Reload Database

```http
POST /api/v1/database/reload
```

Reloads database from disk.

**Response:**
```json
{
    "success": true,
    "message": "Database reloaded successfully",
    "stats": {
        "person_count": 150,
        "family_count": 80,
        "pending_patches": 0,
        "read_only": false
    }
}
```

**Note:** Requires admin authentication (when enabled)

#### 4. Commit Pending Changes

```http
POST /api/v1/database/commit
```

Commits pending patches to disk.

**Response:**
```json
{
    "success": true,
    "message": "Changes committed successfully",
    "patches_committed": 5
}
```

**Note:** Requires admin authentication (when enabled)

#### 5. Get Database Info

```http
GET /api/v1/database/info
```

Returns basic database information.

**Response:**
```json
{
    "path": "/path/to/database.gwb",
    "read_only": false,
    "initialized": true
}
```

### Authentication

Currently, admin endpoints (reload, commit) are accessible without authentication. To enable authentication, uncomment the dependency in `database.py`:

```python
# Before:
async def reload_database():
    ...

# After:
async def reload_database(current_user: Dict = Depends(require_admin)):
    ...
```

---

## Testing

Comprehensive tests are included in `tests/integration/test_database_management.py`.

### Test Coverage

#### DatabaseManager Tests (7 tests)
- ✅ `test_initialize_with_create_if_missing_true`: Database creation
- ✅ `test_initialize_with_create_if_missing_false`: Error handling
- ✅ `test_initialize_creates_parent_directories`: Directory creation
- ✅ `test_get_stats_returns_correct_data`: Statistics retrieval
- ✅ `test_reload_refreshes_database`: Database reload
- ✅ `test_close_commits_pending_patches`: Close behavior
- ✅ `test_singleton_pattern`: Singleton implementation

#### Database Utilities Tests (13 tests)
- ✅ `test_create_new_database_empty`: Empty database creation
- ✅ `test_create_new_database_with_initial_data`: Database with data
- ✅ `test_create_new_database_overwrite_false`: Overwrite protection
- ✅ `test_create_new_database_overwrite_true`: Overwrite enabled
- ✅ `test_load_database_existing`: Load existing database
- ✅ `test_load_database_nonexistent`: Load error handling
- ✅ `test_load_database_read_only`: Read-only mode
- ✅ `test_backup_database_default_path`: Default backup
- ✅ `test_backup_database_custom_path`: Custom backup
- ✅ `test_backup_database_nonexistent`: Backup error handling
- ✅ `test_validate_database_valid`: Validation success
- ✅ `test_validate_database_empty_warnings`: Empty database warnings
- ✅ `test_validate_database_nonexistent`: Validation error handling

### Running Tests

```bash
# Run all database management tests
pytest tests/integration/test_database_management.py -v

# Run all integration tests
pytest tests/integration/ -v

# Run with coverage
pytest tests/integration/test_database_management.py --cov=src/geneweb
```

---

## Usage Examples

### Example 1: Initialize Database with Control

```python
from src.geneweb.api.dependencies import DatabaseManager

manager = DatabaseManager()

# Try to open existing database, fail if not exists
try:
    manager.initialize("production.gwb", create_if_missing=False)
    print("✓ Existing database opened")
except FileNotFoundError:
    print("✗ Database not found, creating new one")
    manager.initialize("production.gwb", create_if_missing=True)
```

### Example 2: Create and Backup Database

```python
from src.geneweb.api.utils.database import (
    create_new_database,
    backup_database,
    validate_database
)
from src.geneweb.core.person import Person, Sex

# Create database with initial data
person = Person(
    first_name="Alice",
    surname="Smith",
    sex=Sex.FEMALE
)
db = create_new_database(
    "family.gwb",
    initial_persons=[person]
)

# Validate it
result = validate_database("family.gwb")
print(f"Valid: {result['valid']}")

# Create backup
backup_path = backup_database("family.gwb")
print(f"Backup created: {backup_path}")
```

### Example 3: Monitor Database Health

```python
from src.geneweb.api.dependencies import DatabaseManager

manager = DatabaseManager()
manager.initialize("family.gwb")

# Get statistics
stats = manager.get_stats()
print(f"Persons: {stats['person_count']}")
print(f"Families: {stats['family_count']}")
print(f"Pending: {stats['pending_patches']}")

# Reload if needed
if stats['pending_patches'] > 10:
    manager.reload()
    print("Database reloaded")

# Close properly
manager.close()
```

### Example 4: Use API Endpoints

```bash
# Get statistics
curl http://localhost:8000/api/v1/database/stats

# Check health
curl http://localhost:8000/api/v1/database/health

# Reload database
curl -X POST http://localhost:8000/api/v1/database/reload

# Commit changes
curl -X POST http://localhost:8000/api/v1/database/commit

# Get database info
curl http://localhost:8000/api/v1/database/info
```

---

## Best Practices

### 1. Database Initialization

- Use `create_if_missing=False` in production to prevent accidental database creation
- Use `create_if_missing=True` in development for convenience
- Always check the result of `get_stats()` after initialization

### 2. Backup Strategy

- Create backups before major operations
- Use timestamped backup names for history
- Validate database after restoration

### 3. Monitoring

- Check `pending_patches` regularly
- Use health endpoint for monitoring systems
- Reload database after external modifications

### 4. Error Handling

```python
from src.geneweb.api.dependencies import DatabaseManager
import logging

logger = logging.getLogger(__name__)

manager = DatabaseManager()
try:
    manager.initialize("database.gwb", create_if_missing=False)
    stats = manager.get_stats()
    logger.info(f"Database loaded: {stats}")
except FileNotFoundError:
    logger.error("Database not found")
    # Handle missing database
except Exception as e:
    logger.exception("Database initialization failed")
    # Handle other errors
finally:
    manager.close()
```

---

## Migration Guide

If you have existing code using DatabaseManager:

### Before:
```python
manager = DatabaseManager()
manager.initialize("database.gwb")
db = manager.get_database()
```

### After (no changes required):
```python
# Same code works, but now with more features
manager = DatabaseManager()
manager.initialize("database.gwb")  # create_if_missing=True by default
db = manager.get_database()

# New features available:
stats = manager.get_stats()
manager.reload()
```

---

## API Integration

The database router is automatically included in the FastAPI application. Register it in `main.py`:

```python
from src.geneweb.api.routers import database

app.include_router(
    database.router,
    prefix="/api/v1",
    tags=["database"]
)
```

---

## Troubleshooting

### Problem: Database not created
**Solution:** Check that `create_if_missing=True` and parent directory is writable

### Problem: FileNotFoundError during load
**Solution:** Verify path is correct or use `create_if_missing=True`

### Problem: Pending patches not committed
**Solution:** Call `manager.close()` or use commit endpoint

### Problem: Database corruption detected
**Solution:** Use `validate_database()` to identify issues, restore from backup

---

## Future Enhancements

Potential features for future development:

1. **Automatic Backups**: Scheduled backup creation
2. **Migration Tools**: Database version migration utilities  
3. **Export/Import**: JSON export/import for portability
4. **Compression**: Database compression utilities
5. **Multi-Database**: Support for multiple database management
6. **Audit Log**: Track all database operations
7. **Performance Metrics**: Database performance monitoring
8. **Replication**: Database replication support

---

## Related Documentation

- [Database Integration Guide](DATABASE_INTEGRATION_GUIDE.md)
- [Developer Guide](DEVELOPER_GUIDE.md)
- [API Documentation](API/)

---

**Last Updated:** 2024-01-15  
**Version:** 1.0.0  
**Authors:** GeneWeb Development Team
