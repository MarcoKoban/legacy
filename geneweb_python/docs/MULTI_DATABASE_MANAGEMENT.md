# Multi-Database Management

## Overview

The GeneWeb API now supports managing multiple databases simultaneously. You can create, list, switch between, and delete databases dynamically through the API without restarting the server.

## Table of Contents

1. [Key Features](#key-features)
2. [API Endpoints](#api-endpoints)
3. [DatabaseManager Enhancements](#databasemanager-enhancements)
4. [Usage Examples](#usage-examples)
5. [Migration Guide](#migration-guide)

---

## Key Features

### ✨ Multiple Database Support

- **Load Multiple Databases**: Manage several databases in memory simultaneously
- **Active Database Concept**: One database is "active" at a time for operations
- **Dynamic Switching**: Change the active database without restart
- **Independent Management**: Each database maintains its own state and patches

### 🔧 Database Operations

- **Create**: Create new empty databases via API
- **List**: View all loaded databases with statistics
- **Activate**: Switch between databases
- **Delete**: Remove databases from memory and optionally from disk
- **Query**: Get detailed information about any database

---

## API Endpoints

### 1. List All Databases

```http
GET /api/v1/database/databases
```

Returns a list of all loaded databases with their statistics.

**Response:**
```json
{
  "databases": [
    {
      "name": "family_tree",
      "path": "/data/family_tree.gwb",
      "active": true,
      "person_count": 150,
      "family_count": 80,
      "read_only": false,
      "pending_patches": 2
    },
    {
      "name": "research_db",
      "path": "/data/research_db.gwb",
      "active": false,
      "person_count": 45,
      "family_count": 20,
      "read_only": false,
      "pending_patches": 0
    }
  ],
  "active_database": "family_tree"
}
```

---

### 2. Get Active Database

```http
GET /api/v1/database/databases/active
```

Returns information about the currently active database.

**Response:**
```json
{
  "name": "family_tree",
  "path": "/data/family_tree.gwb",
  "active": true,
  "person_count": 150,
  "family_count": 80,
  "read_only": false,
  "pending_patches": 2
}
```

---

### 3. Create New Database

```http
POST /api/v1/database/databases
```

Creates a new empty database.

**Request Body:**
```json
{
  "name": "new_family",
  "set_active": false
}
```

**Parameters:**
- `name` (required): Name of the new database (without .gwb extension)
- `set_active` (optional, default: false): Whether to set this as the active database

**Response:**
```json
{
  "success": true,
  "message": "Database 'new_family' created successfully",
  "database": {
    "name": "new_family",
    "path": "/data/new_family.gwb",
    "active": false,
    "person_count": 0,
    "family_count": 0,
    "read_only": false,
    "pending_patches": 0
  }
}
```

---

### 4. Activate Database

```http
POST /api/v1/database/databases/{name}/activate
```

Sets a database as the active database for all subsequent operations.

**Path Parameters:**
- `name`: Name of the database to activate

**Response:**
```json
{
  "success": true,
  "message": "Database 'research_db' is now active",
  "active_database": "research_db"
}
```

---

### 5. Delete Database

```http
DELETE /api/v1/database/databases/{name}?delete_files=false
```

Deletes a database from memory and optionally from disk.

**Path Parameters:**
- `name`: Name of the database to delete

**Query Parameters:**
- `delete_files` (optional, default: false): Whether to delete files from disk

**Response:**
```json
{
  "success": true,
  "message": "Database 'old_db' deleted successfully",
  "deleted_files": false
}
```

**Important Notes:**
- Cannot delete the currently active database
- Switch to another database first before deletion
- `delete_files=true` permanently removes data from disk (use with caution!)

---

## DatabaseManager Enhancements

### New Multi-Database Methods

#### `create_database(name, db_path=None, create_if_missing=True, set_active=False)`

Creates or loads a database.

```python
from geneweb.api.dependencies import db_manager

# Create new database
db_manager.create_database("family_tree", set_active=True)

# Load existing database from specific path
db_manager.create_database("archive", db_path="/archives/old_data", set_active=False)
```

---

#### `get_database(name=None)`

Gets a database instance. If `name` is None, returns the active database.

```python
# Get active database
db = db_manager.get_database()

# Get specific database
research_db = db_manager.get_database("research_db")
```

---

#### `set_active_database(name)`

Changes the active database.

```python
db_manager.set_active_database("research_db")
```

---

#### `get_active_database_name()`

Returns the name of the active database.

```python
active = db_manager.get_active_database_name()
print(f"Currently using: {active}")
```

---

#### `list_databases()`

Lists all loaded databases with their information.

```python
databases = db_manager.list_databases()
for db_info in databases:
    print(f"{db_info['name']}: {db_info['person_count']} persons")
```

---

#### `delete_database(name, delete_files=False)`

Removes a database from memory and optionally from disk.

```python
# Remove from memory only
db_manager.delete_database("old_db", delete_files=False)

# Remove from memory AND delete files
db_manager.delete_database("temp_db", delete_files=True)
```

---

#### `close(name=None)` and `close_all()`

Close specific or all databases.

```python
# Close specific database
db_manager.close("research_db")

# Close all databases
db_manager.close_all()
```

---

## Usage Examples

### Example 1: Working with Multiple Databases

```python
from geneweb.api.dependencies import db_manager

# Create multiple databases
db_manager.create_database("main_family", set_active=True)
db_manager.create_database("research")
db_manager.create_database("archive")

# List all databases
databases = db_manager.list_databases()
print(f"Loaded {len(databases)} databases")

# Work with main database
main_db = db_manager.get_database("main_family")
print(f"Main DB has {len(main_db.data['persons'])} persons")

# Switch to research database
db_manager.set_active_database("research")

# Get active database (now research)
current_db = db_manager.get_database()
```

---

### Example 2: API Usage with cURL

```bash
# List all databases
curl http://localhost:8000/api/v1/database/databases

# Create new database
curl -X POST http://localhost:8000/api/v1/database/databases \
  -H "Content-Type: application/json" \
  -d '{"name": "my_new_db", "set_active": false}'

# Get active database
curl http://localhost:8000/api/v1/database/databases/active

# Activate a database
curl -X POST http://localhost:8000/api/v1/database/databases/my_new_db/activate

# Delete database (memory only)
curl -X DELETE http://localhost:8000/api/v1/database/databases/old_db

# Delete database with files
curl -X DELETE "http://localhost:8000/api/v1/database/databases/old_db?delete_files=true"
```

---

### Example 3: Python API Client

```python
import requests

BASE_URL = "http://localhost:8000/api/v1/database"

# List databases
response = requests.get(f"{BASE_URL}/databases")
databases = response.json()
print(f"Active: {databases['active_database']}")

# Create new database
response = requests.post(
    f"{BASE_URL}/databases",
    json={"name": "test_db", "set_active": True}
)
result = response.json()
print(f"Created: {result['database']['name']}")

# Activate database
response = requests.post(f"{BASE_URL}/databases/test_db/activate")
print(response.json()["message"])

# Delete database
response = requests.delete(f"{BASE_URL}/databases/test_db?delete_files=false")
print(response.json()["message"])
```

---

### Example 4: Application Startup with Multiple Databases

```python
from fastapi import FastAPI
from geneweb.api.dependencies import db_manager
from geneweb.api.routers import database

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    # Initialize default database
    db_manager.initialize()  # Loads default database
    
    # Load additional databases
    db_manager.create_database("archive", create_if_missing=False)
    db_manager.create_database("research", create_if_missing=False)
    
    print(f"Loaded {len(db_manager.list_databases())} databases")

@app.on_event("shutdown")
async def shutdown_event():
    # Close all databases
    db_manager.close_all()

# Include database router
app.include_router(database.router)
```

---

## Migration Guide

### Backward Compatibility

✅ **All existing code continues to work without changes!**

The `initialize()` method and `get_database()` function work exactly as before:

```python
# Old code (still works)
db_manager.initialize("/data/my_db")
db = db_manager.get_database()

# New multi-database features (optional)
db_manager.create_database("another_db")
db_manager.set_active_database("another_db")
```

### What Changed

| Old Behavior | New Behavior |
|--------------|--------------|
| Single database instance `_database` | Dictionary of databases `_databases` |
| No concept of "active" database | Active database pointer `_active_db_name` |
| `initialize()` sets single DB | `initialize()` creates/loads default DB and sets it active |
| `get_database()` returns single DB | `get_database()` returns active DB (or specified by name) |
| `close()` closes single DB | `close()` closes specific DB or active DB |

### Key Points

1. **Default behavior unchanged**: `initialize()` still works the same way
2. **Active database concept**: The "active" database is used for all operations when no name is specified
3. **Explicit database selection**: You can now specify which database to use in `get_database(name)`
4. **New endpoints**: All multi-database endpoints are additive (don't break existing endpoints)

---

## Utility Functions

### List Available Databases on Disk

```python
from geneweb.api.utils.database import list_available_databases

# Scan directory for .gwb databases
available = list_available_databases("/data")
for db in available:
    print(f"{db['name']}: {db['size_bytes']} bytes")
```

### Get Database Metadata

```python
from geneweb.api.utils.database import get_database_metadata

metadata = get_database_metadata("/data/my_family")
print(f"Size: {metadata['size_mb']} MB")
print(f"Last modified: {metadata['last_modified']}")
```

### Delete Database Files

```python
from geneweb.api.utils.database import delete_database_files

# Permanently delete database files from disk
delete_database_files("/data/old_db")
```

---

## Best Practices

### 1. Always Check Active Database

```python
active = db_manager.get_active_database_name()
print(f"Working with: {active}")
```

### 2. Handle Database Not Found

```python
try:
    db_manager.set_active_database("nonexistent")
except ValueError as e:
    print(f"Database not found: {e}")
```

### 3. Don't Delete Active Database

```python
# ❌ BAD - Will raise ValueError
db_manager.delete_database(db_manager.get_active_database_name())

# ✅ GOOD - Switch first
db_manager.set_active_database("another_db")
db_manager.delete_database("old_db")
```

### 4. Close Databases on Shutdown

```python
@app.on_event("shutdown")
async def shutdown():
    db_manager.close_all()  # Commits all pending patches
```

### 5. Use with Caution: delete_files=True

```python
# ⚠️ WARNING: This permanently deletes data!
db_manager.delete_database("temp", delete_files=True)
```

---

## Error Handling

Common errors and how to handle them:

```python
# Database not found
try:
    db = db_manager.get_database("missing")
except RuntimeError as e:
    print(f"Error: {e}")

# Cannot delete active database
try:
    db_manager.delete_database(db_manager.get_active_database_name())
except ValueError as e:
    print(f"Error: {e}")
    # Solution: switch to another DB first

# Database already exists
try:
    db_manager.create_database("existing_name")
except Exception as e:
    print(f"Database already loaded: {e}")
```

---

## Performance Considerations

- **Memory Usage**: Each loaded database consumes memory. Close databases you're not using.
- **Disk I/O**: Creating/deleting databases involves disk operations
- **Patches**: Each database maintains its own patch queue
- **Concurrent Access**: The API is designed for single-threaded access to each database

---

## Security Notes

⚠️ **Important Security Considerations:**

1. **Access Control**: Implement authentication for database creation/deletion endpoints
2. **Path Validation**: Database names are validated to prevent path traversal attacks
3. **Disk Space**: Monitor available disk space when creating databases
4. **Backup**: Always backup before using `delete_files=true`

---

## Testing

See the test file `tests/integration/test_multi_database_management.py` for comprehensive examples.

---

## Changelog

### Version 2.0.0 - Multi-Database Support

**Added:**
- Multi-database support in `DatabaseManager`
- New API endpoints for database management
- Utility functions for database operations
- Active database concept
- Comprehensive documentation

**Changed:**
- `DatabaseManager` now manages multiple databases
- `get_database()` supports optional name parameter
- Internal storage changed from `_database` to `_databases` dict

**Backward Compatible:**
- All existing code works without modifications
- `initialize()` behavior unchanged
- Default database concept maintained

---

## Support

For questions or issues:
1. Check this documentation
2. Review test cases in `tests/integration/`
3. See `DATABASE_MANAGEMENT_FEATURES.md` for original single-DB features
