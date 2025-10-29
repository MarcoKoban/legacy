"""
Database management endpoints for GeneWeb API with multi-database support.
"""

import logging
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from ..dependencies import Database, db_manager, get_database
from ..security.auth import Permission, SecurityContext, auth_service

router = APIRouter(tags=["database"])
security = HTTPBearer(
    auto_error=True
)  # Authentication REQUIRED - auto_error=True forces 403 if no token


# Authentication dependency
async def get_security_context(
    request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)
) -> SecurityContext:
    """
    Extract security context from request.
    Authentication is REQUIRED for all database management operations.
    """
    # Verify token (will raise 401 if invalid or missing)
    token_data = auth_service.verify_token(credentials.credentials)

    # Extract client information
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("User-Agent")

    return SecurityContext(
        user=token_data, ip_address=ip_address, user_agent=user_agent
    )


# ===== Pydantic Models =====


class DatabaseStats(BaseModel):
    """Database statistics response model."""

    name: str = Field(..., description="Database name")
    db_path: str = Field(..., description="Path to database directory")
    person_count: int = Field(..., description="Number of persons in database")
    family_count: int = Field(..., description="Number of families in database")
    union_count: int = Field(..., description="Number of unions in database")
    couple_count: int = Field(..., description="Number of couples in database")
    descend_count: int = Field(..., description="Number of descends in database")
    pending_patches: int = Field(..., description="Number of uncommitted patches")
    read_only: bool = Field(..., description="Whether database is read-only")
    active: bool = Field(..., description="Whether this is the active database")


class DatabaseHealth(BaseModel):
    """Database health check response."""

    status: str = Field(..., description="Database status (healthy/degraded/error)")
    message: str = Field(..., description="Status message")
    stats: DatabaseStats = Field(..., description="Database statistics")


class DatabaseInfo(BaseModel):
    """Basic database information."""

    name: str = Field(..., description="Database name")
    path: str = Field(..., description="Database path")
    active: bool = Field(..., description="Whether this is the active database")
    person_count: int = Field(..., description="Number of persons")
    family_count: int = Field(..., description="Number of families")
    read_only: bool = Field(..., description="Read-only status")
    pending_patches: int = Field(..., description="Pending patches")
    owner_id: Optional[str] = Field(
        None, description="Owner user ID (None for legacy databases)"
    )


class DatabaseCreateRequest(BaseModel):
    """Request model for creating a new database."""

    name: str = Field(
        ..., description="Name of the new database", min_length=1, max_length=100
    )
    set_active: bool = Field(
        default=False, description="Set as active database after creation"
    )


class DatabaseCreateResponse(BaseModel):
    """Response model for database creation."""

    success: bool = Field(..., description="Whether creation was successful")
    message: str = Field(..., description="Success or error message")
    database: DatabaseInfo = Field(..., description="Created database info")


class DatabaseListResponse(BaseModel):
    """Response model for listing databases."""

    databases: List[DatabaseInfo] = Field(..., description="List of databases")
    active_database: Optional[str] = Field(None, description="Name of active database")


class DatabaseActivateResponse(BaseModel):
    """Response model for activating a database."""

    success: bool = Field(..., description="Whether activation was successful")
    message: str = Field(..., description="Success or error message")
    active_database: str = Field(..., description="Name of newly active database")


class DatabaseDeleteResponse(BaseModel):
    """Response model for deleting a database."""

    success: bool = Field(..., description="Whether deletion was successful")
    message: str = Field(..., description="Success or error message")
    deleted_files: bool = Field(..., description="Whether files were deleted from disk")


class DatabaseRenameRequest(BaseModel):
    """Request model for renaming a database."""

    new_name: str = Field(
        ..., description="New name for the database", min_length=1, max_length=100
    )
    rename_files: bool = Field(
        default=False, description="Also rename database files on disk"
    )


class DatabaseRenameResponse(BaseModel):
    """Response model for renaming a database."""

    success: bool = Field(..., description="Whether renaming was successful")
    message: str = Field(..., description="Success or error message")
    old_name: str = Field(..., description="Previous database name")
    new_name: str = Field(..., description="New database name")
    files_renamed: bool = Field(..., description="Whether files were renamed on disk")
    database: DatabaseInfo = Field(..., description="Renamed database info")


# ===== Original Endpoints (kept for backward compatibility) =====


@router.get("/stats", response_model=DatabaseStats)
async def get_database_stats(
    db: Database = Depends(get_database),
    security_context: SecurityContext = Depends(get_security_context),
) -> DatabaseStats:
    """
    Get active database statistics.

    Returns current database statistics including record counts and status.
    **Authentication required.**
    """
    try:
        stats = db_manager.get_stats()
        return DatabaseStats(**stats)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get database stats: {str(e)}",
        )


@router.get("/health", response_model=DatabaseHealth)
async def check_database_health(
    db: Database = Depends(get_database),
    security_context: SecurityContext = Depends(get_security_context),
) -> DatabaseHealth:
    """
    Check database health and connectivity.

    Returns detailed health information including statistics.
    **Authentication required.**
    """
    try:
        stats = db_manager.get_stats()

        # Determine health status
        if stats["pending_patches"] > 100:
            status_value = "degraded"
            message = f"Database has {stats['pending_patches']} uncommitted patches"
        elif stats["read_only"]:
            status_value = "degraded"
            message = "Database is in read-only mode"
        else:
            status_value = "healthy"
            message = "Database is operating normally"

        return DatabaseHealth(
            status=status_value,
            message=message,
            stats=DatabaseStats(**stats),
        )
    except Exception as e:
        return DatabaseHealth(
            status="error",
            message=f"Database health check failed: {str(e)}",
            stats=DatabaseStats(
                db_path="unknown",
                person_count=0,
                family_count=0,
                union_count=0,
                couple_count=0,
                descend_count=0,
                pending_patches=0,
                read_only=False,
            ),
        )


@router.post("/reload", status_code=status.HTTP_200_OK)
async def reload_database(
    db: Database = Depends(get_database),
    security_context: SecurityContext = Depends(get_security_context),
) -> Dict[str, str]:
    """
    Reload database from disk.

    **Admin only**: Reloads the database from disk files, discarding any
    uncommitted in-memory changes.
    **Requires SYSTEM_ADMIN permission.**
    """
    # Check admin permission
    security_context.require_permission(Permission.SYSTEM_ADMIN)

    try:
        db_manager.reload()
        return {
            "status": "success",
            "message": "Database reloaded successfully",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reload database: {str(e)}",
        )


@router.post("/commit", status_code=status.HTTP_200_OK)
async def commit_patches(
    db: Database = Depends(get_database),
    security_context: SecurityContext = Depends(get_security_context),
) -> Dict[str, str]:
    """
    Commit pending patches to database.

    **Admin only**: Commits all pending patches to the database files on disk.
    **Requires SYSTEM_ADMIN permission.**
    """
    # Check admin permission
    security_context.require_permission(Permission.SYSTEM_ADMIN)

    try:
        pending = len(db.patch_manager.person_patches)
        if pending == 0:
            return {
                "status": "success",
                "message": "No pending patches to commit",
                "patches_committed": 0,
            }

        db.commit_patches()
        return {
            "status": "success",
            "message": f"Committed {pending} patches successfully",
            "patches_committed": pending,
        }
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Database is read-only",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to commit patches: {str(e)}",
        )


@router.get("/info", response_model=Dict[str, str])
async def get_database_info(
    db: Database = Depends(get_database),
    security_context: SecurityContext = Depends(get_security_context),
) -> Dict[str, str]:
    """
    Get general database information.

    Returns basic information about the database including path and version.
    **Authentication required.**
    """
    try:
        return {
            "db_path": db.dbdir,
            "read_only": str(db.read_only),
            "format": "GeneWeb binary (.gwb)",
            "api_version": "1.0.0",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get database info: {str(e)}",
        )


# ===== Multi-Database Management Endpoints =====


@router.get("/databases", response_model=DatabaseListResponse)
async def list_databases(
    security_context: SecurityContext = Depends(get_security_context),
) -> DatabaseListResponse:
    """
    List databases accessible to the current user.

    - **USER**: Can only see their own databases
    - **ADMIN**: Can see all databases

    **Authentication required.**
    """
    try:
        # Check if user is admin
        from ..security.auth import UserRole

        is_admin = security_context.user.role == UserRole.ADMIN

        # List databases filtered by ownership
        databases_info = db_manager.list_databases(
            user_id=security_context.user.user_id, is_admin=is_admin
        )
        active_db = db_manager.get_active_database_name()

        databases = [DatabaseInfo(**db_info) for db_info in databases_info]

        return DatabaseListResponse(databases=databases, active_database=active_db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list databases: {str(e)}",
        )


@router.get("/databases/active", response_model=DatabaseInfo)
async def get_active_database(
    security_context: SecurityContext = Depends(get_security_context),
) -> DatabaseInfo:
    """
    Get information about the currently active database.
    **Authentication required.**
    """
    try:
        active_name = db_manager.get_active_database_name()
        if active_name is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No active database"
            )

        # Check if user is admin
        from ..security.auth import UserRole

        is_admin = security_context.user.role == UserRole.ADMIN

        databases = db_manager.list_databases(
            user_id=security_context.user.user_id, is_admin=is_admin
        )
        active_db = next((db for db in databases if db["name"] == active_name), None)

        if active_db is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Active database '{active_name}' not found",
            )

        return DatabaseInfo(**active_db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get active database: {str(e)}",
        )


@router.post(
    "/databases",
    response_model=DatabaseCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_database(
    request: DatabaseCreateRequest,
    security_context: SecurityContext = Depends(get_security_context),
) -> DatabaseCreateResponse:
    """
    Create a new database owned by the current user.

    - **USER**: Can create databases (will be owned by them)
    - **ADMIN**: Can create databases (will be owned by them)

    Creates a new empty database with the specified name.
    Optionally sets it as the active database.
    **Authentication required.**
    """
    try:
        logging.getLogger("geneweb.api").info(
            "received request to create database: %s by user %s",
            request.name,
            security_context.user.username,
        )

        # Create the database with current user as owner
        db_name = db_manager.create_database(
            name=request.name,
            create_if_missing=True,
            set_active=request.set_active,
            owner_id=security_context.user.user_id,  # Set the owner!
        )

        # Check if user is admin
        from ..security.auth import UserRole

        is_admin = security_context.user.role == UserRole.ADMIN

        # Get database info
        databases = db_manager.list_databases(
            user_id=security_context.user.user_id, is_admin=is_admin
        )
        db_info = next((db for db in databases if db["name"] == db_name), None)

        if db_info is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database created but could not retrieve info",
            )

        return DatabaseCreateResponse(
            success=True,
            message=f"Database '{db_name}' created successfully",
            database=DatabaseInfo(**db_info),
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create database: {str(e)}",
        )


@router.post("/databases/{name}/activate", response_model=DatabaseActivateResponse)
async def activate_database(
    name: str,
    security_context: SecurityContext = Depends(get_security_context),
) -> DatabaseActivateResponse:
    """
    Set a database as the active database.

    All subsequent operations will use this database unless specified otherwise.

    - **USER**: Can only activate databases they own
    - **ADMIN**: Can activate any database

    **Authentication required.**
    """
    # Check if user is admin
    from ..security.auth import UserRole

    is_admin = security_context.user.role == UserRole.ADMIN

    # First check if database exists (to return 404 instead of 403)
    if name not in db_manager._databases:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Database'{name}' not found.{list(db_manager._databases.keys())}",
        )

    # Then verify user can access this database
    if not db_manager.can_access_database(
        name, security_context.user.user_id, is_admin
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You can only activate databases you own.",
        )

    try:
        db_manager.set_active_database(name)

        return DatabaseActivateResponse(
            success=True,
            message=f"Database '{name}' is now active",
            active_database=name,
        )
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to activate database: {str(e)}",
        )


@router.put("/databases/{name}/rename", response_model=DatabaseRenameResponse)
async def rename_database(
    name: str,
    request: DatabaseRenameRequest,
    security_context: SecurityContext = Depends(get_security_context),
) -> DatabaseRenameResponse:
    """
    Rename a database.

    Args:
        name: Current name of the database to rename
        request: Rename request containing new name and options
        security_context: Authentication context

    Returns:
        DatabaseRenameResponse with success status and database info

    - **USER**: Can only rename databases they own
    - **ADMIN**: Can rename any database

    Note: If rename_files is True, the database files on disk will also be renamed.
          This requires that no other process is accessing the database files.
    **Authentication required.**
    """
    # Check if user is admin
    from ..security.auth import UserRole

    is_admin = security_context.user.role == UserRole.ADMIN

    # First check if database exists (to return 404 instead of 403)
    if name not in db_manager._databases:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Database '{name}' not found",
        )

    # Then verify user can access this database
    if not db_manager.can_access_database(
        name, security_context.user.user_id, is_admin
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You can only rename databases you own.",
        )

    try:
        logging.getLogger("geneweb.api").info(
            "Received request to rename database: %s -> %s by user %s",
            name,
            request.new_name,
            security_context.user.username,
        )

        # Rename the database
        new_name = db_manager.rename_database(
            old_name=name, new_name=request.new_name, rename_files=request.rename_files
        )

        # Get updated database info
        databases = db_manager.list_databases(
            user_id=security_context.user.user_id, is_admin=is_admin
        )
        db_info = next((db for db in databases if db["name"] == new_name), None)

        if db_info is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database renamed but could not retrieve updated info",
            )

        return DatabaseRenameResponse(
            success=True,
            message=f"Database renamed from '{name}' to '{new_name}' successfully",
            old_name=name,
            new_name=new_name,
            files_renamed=request.rename_files,
            database=DatabaseInfo(**db_info),
        )
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except OSError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to rename database files: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to rename database: {str(e)}",
        )


@router.delete("/databases/{name}", response_model=DatabaseDeleteResponse)
async def delete_database(
    name: str,
    delete_files: bool = False,
    security_context: SecurityContext = Depends(get_security_context),
) -> DatabaseDeleteResponse:
    """
    Delete a database from memory and optionally from disk.

    Args:
        name: Name of the database to delete
        delete_files: If True, also delete database files from disk (default: False)
        security_context: Authentication context

    - **USER**: Can only delete databases they own
    - **ADMIN**: Can delete any database

    Note: Cannot delete the currently active database. Switch to another database first.
    **Authentication required.**
    """
    # Check if user is admin
    from ..security.auth import UserRole

    is_admin = security_context.user.role == UserRole.ADMIN

    # Verify user can access this database
    if not db_manager.can_access_database(
        name, security_context.user.user_id, is_admin
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You can only delete databases you own.",
        )

    try:
        db_manager.delete_database(name, delete_files=delete_files)

        return DatabaseDeleteResponse(
            success=True,
            message=f"Database '{name}' deleted successfully",
            deleted_files=delete_files,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete database: {str(e)}",
        )
