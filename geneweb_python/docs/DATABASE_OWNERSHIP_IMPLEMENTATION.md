# Database Ownership Implementation

## Overview
Implemented per-user database ownership to ensure proper data isolation in the multi-tenant GeneWeb system. Users can now only access databases they own, while admins retain access to all databases.

## Changes Made

### 1. Core Database Management (`src/geneweb/api/dependencies.py`)

#### DatabaseMetadata Class
Added a new wrapper class to track database ownership:
```python
@dataclass
class DatabaseMetadata:
    """Metadata wrapper for a database with ownership information."""
    name: str
    db: Database
    owner_id: Optional[str] = None  # User ID of the owner (None for legacy databases)
```

#### DatabaseManager Updates
- **Modified `_databases` structure**: Changed from `Dict[str, Database]` to `Dict[str, DatabaseMetadata]`
- **Updated `create_database()`**: Now accepts `owner_id` parameter to assign database ownership
- **Added `can_access_database()`**: New method to check if a user can access a specific database
  - Admins can access all databases
  - Regular users can only access databases they own
  - Legacy databases (owner_id=None) are accessible to all users for backwards compatibility
- **Updated `list_databases()`**: Now accepts `user_id` and `is_admin` parameters to filter results
- **Modified `get_database()`**: Returns `metadata.db` to maintain compatibility
- **Updated `rename_database()`**: Works with metadata objects

### 2. Database Router (`src/geneweb/api/routers/database.py`)

#### Updated Endpoints

**List Databases (`GET /databases`)**
- Now filters databases based on user ownership
- Regular users only see their own databases
- Admins see all databases

**Get Active Database (`GET /databases/active`)**
- Added ownership verification
- Returns 403 if user doesn't own the active database (unless admin)

**Create Database (`POST /databases`)**
- Automatically sets the creating user as owner
- Passes `owner_id=security_context.user.user_id` to database creation

**Activate Database (`POST /databases/{name}/activate`)**
- Verifies user owns the database before activating
- Admins can activate any database

**Rename Database (`PUT /databases/{name}/rename`)**
- Verifies user owns the database before renaming
- Admins can rename any database

**Delete Database (`DELETE /databases/{name}`)**
- Verifies user owns the database before deletion
- Admins can delete any database

#### Response Model Updates
Added `owner_id` field to `DatabaseInfo` model:
```python
class DatabaseInfo(BaseModel):
    name: str
    path: str
    active: bool
    person_count: int
    family_count: int
    read_only: bool
    pending_patches: int
    owner_id: Optional[str] = None  # NEW FIELD
```

### 3. Permission Model Updates

All database endpoints now follow this pattern:
- **USER role**: Can only manage databases they own
- **ADMIN role**: Can manage all databases
- Removed the old `SYSTEM_ADMIN` permission checks
- Ownership is checked using `can_access_database()` method

## Security Implications

### Before
- All authenticated users could access all databases
- No isolation between users' data
- Major privacy and security concern

### After
- Each user can only access databases they created
- Admins retain full access for management purposes
- Legacy databases (created before this change) remain accessible to all users
- Proper multi-tenancy with data isolation

## Testing

All existing authentication tests pass (32/32):
```bash
pytest tests/unit/api/security/test_auth.py -v
```

Created comprehensive ownership test (`test_database_ownership.py`) that verifies:
1. ✓ Users can create databases (owned by them)
2. ✓ Users can only see their own databases
3. ✓ Users cannot access other users' databases
4. ✓ Users can access their own databases
5. ✓ Admins can see all databases
6. ✓ Admins can access any database

## Migration Notes

### Existing Databases
Databases created before this implementation have `owner_id=None` and are considered "legacy" databases. These remain accessible to all authenticated users for backwards compatibility.

### New Databases
All databases created after this implementation will have an owner_id set to the creating user's UUID.

### Recommended Migration
For production deployment, consider:
1. Running a migration script to assign ownership to existing databases
2. Or marking all existing databases as "shared" with a special owner_id
3. Documenting the migration strategy for users

## API Behavior Changes

### Before
```bash
# Any user could see all databases
GET /databases
Response: [{"name": "db1"}, {"name": "db2"}, {"name": "db3"}]
```

### After
```bash
# Regular user only sees their own databases
GET /databases
Response: [{"name": "my_db"}]

# Admin sees all databases
GET /databases  # (as admin)
Response: [{"name": "db1", "owner_id": "uuid1"}, 
           {"name": "db2", "owner_id": "uuid2"}, 
           {"name": "my_db", "owner_id": "current_user_uuid"}]
```

## Frontend Integration Required

The frontend needs to be updated to:
1. Handle the new `owner_id` field in database responses
2. Display ownership information to admins
3. Handle 403 errors when accessing databases user doesn't own
4. Update database creation to show that databases are owned by the user
5. Filter available databases based on user ownership

## Deployment Checklist

- [x] Update backend code with ownership logic
- [x] Add DatabaseMetadata class
- [x] Update all database endpoints
- [x] Add ownership checks
- [x] Update response models
- [x] Test ownership isolation
- [ ] Update frontend to handle ownership
- [ ] Deploy to production
- [ ] Migrate existing databases (assign ownership)
- [ ] Update API documentation
- [ ] Notify users of changes

## Related Files

- `src/geneweb/api/dependencies.py` - Core database management
- `src/geneweb/api/routers/database.py` - Database REST endpoints
- `test_database_ownership.py` - Ownership verification tests
- `QUICK_START_AUTH.md` - Authentication documentation (needs update)
- `AUTHENTICATION_SUMMARY.md` - Role summary (needs update)
