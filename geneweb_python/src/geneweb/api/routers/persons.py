"""
Secure Person CRUD endpoints with GDPR compliance and audit trail.
"""

from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..dependencies import get_database
from ..models.person import (
    PersonCreate,
    PersonListResponse,
    PersonResponse,
    PersonSearchFilters,
    PersonUpdate,
)
from ..security.audit import audit_logger
from ..security.auth import (
    Permission,
    SecurityContext,
    auth_service,
)
from ..security.validation import validate_request_data
from ..services.person_service import (
    PersonAccessDeniedError,
    PersonNotFoundError,
    PersonService,
)

logger = structlog.get_logger(__name__)
security = HTTPBearer(
    auto_error=True
)  # Authentication REQUIRED - auto_error=True forces 403 if no token

router = APIRouter(prefix="/api/v1/persons", tags=["persons"])


async def get_security_context(
    request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)
) -> SecurityContext:
    """
    Extract security context from request.
    Authentication is REQUIRED - no anonymous access.
    """
    # Verify token (will raise 401 if invalid or missing)
    token_data = auth_service.verify_token(credentials.credentials)

    # Extract client information
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("User-Agent")

    return SecurityContext(
        user=token_data, ip_address=ip_address, user_agent=user_agent
    )


def get_person_service(db=Depends(get_database)) -> PersonService:
    """Get PersonService instance with database dependency."""
    return PersonService(database=db)


@router.post("/", response_model=PersonResponse, status_code=status.HTTP_201_CREATED)
async def create_person(
    person_data: PersonCreate,
    security_context: SecurityContext = Depends(get_security_context),
    person_service: PersonService = Depends(get_person_service),
) -> PersonResponse:
    """
    Create a new person.

    - **Requires**: CREATE_PERSON permission (optional for local use)
    - **Security**: Input validation, XSS protection, audit logging
    """
    # Check permissions
    security_context.require_permission(Permission.CREATE_PERSON)

    # Validate and sanitize input
    validated_data = validate_request_data(person_data.dict())

    try:
        # Create person through service
        person = await person_service.create_person(
            person_data=validated_data,
            created_by=security_context.user.user_id,
            security_context=security_context,
        )

        # Log audit event
        await audit_logger.log_person_created(
            security_context=security_context,
            person_id=person.id,
            person_data=validated_data,
        )

        logger.info(
            "Person created successfully",
            person_id=str(person.id),
            user_id=str(security_context.user.user_id),
            ip_address=security_context.ip_address,
        )

        return person

    except Exception as e:
        logger.error(
            "Person creation failed",
            error=str(e),
            user_id=str(security_context.user.user_id),
            ip_address=security_context.ip_address,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create person",
        )


@router.get("/{person_id}", response_model=PersonResponse)
async def get_person(
    person_id: UUID,
    security_context: SecurityContext = Depends(get_security_context),
    person_service: PersonService = Depends(),
) -> PersonResponse:
    """
    Get person by ID with role-based access control.

    - **Security**: Access control based on user role and family relationships
    - **Privacy**: Sensitive data filtered based on access level
    - **Audit**: All access attempts logged
    """
    try:
        security_context.require_permission(Permission.VIEW_ALL_PERSONS)

        # Get person data
        person = await person_service.get_person(
            person_id=person_id, security_context=security_context
        )

        if not person:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Person not found"
            )

        # Log access
        await audit_logger.log_person_accessed(
            security_context=security_context, person_id=person_id, access_type="view"
        )

        return person

    except PersonNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Person not found"
        )
    except PersonAccessDeniedError:
        await audit_logger.log_access_denied(
            security_context=security_context,
            resource_type="person",
            resource_id=person_id,
            reason="Insufficient permissions",
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )


@router.get("/", response_model=PersonListResponse)
async def list_persons(
    filters: PersonSearchFilters = Depends(),
    security_context: SecurityContext = Depends(get_security_context),
    person_service: PersonService = Depends(),
) -> PersonListResponse:
    """
    List persons with advanced filtering and pagination.

    - **Security**: Results filtered by user access level
    - **Privacy**: Sensitive data protection based on consent
    - **Performance**: Optimized pagination and caching
    """
    security_context.require_permission(Permission.VIEW_ALL_PERSONS)

    try:
        result = await person_service.list_persons(
            filters=filters, security_context=security_context
        )

        logger.info(
            "Person list accessed",
            user_id=str(security_context.user.user_id),
            total_results=result.total,
            page=filters.page,
            ip_address=security_context.ip_address,
        )

        return result

    except Exception as e:
        logger.error(
            "Person list query failed",
            error=str(e),
            user_id=str(security_context.user.user_id),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve persons",
        )


@router.put("/{person_id}", response_model=PersonResponse)
async def update_person(
    person_id: UUID,
    person_update: PersonUpdate,
    security_context: SecurityContext = Depends(get_security_context),
    person_service: PersonService = Depends(),
) -> PersonResponse:
    """
    Update person with version control and comprehensive audit trail.

    - **Security**: Role-based access control with family relationship validation
    - **Versioning**: Optimistic locking to prevent conflicts
    - **Audit**: Complete change tracking with before/after values
    """
    try:
        security_context.require_permission(Permission.UPDATE_ANY_PERSON)

        # Validate and sanitize input
        validated_data = validate_request_data(person_update.dict(exclude_unset=True))

        # Get current person data for audit trail
        current_person = await person_service.get_person(person_id, security_context)
        if not current_person:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Person not found"
            )

        # Update person
        updated_person = await person_service.update_person(
            person_id=person_id,
            update_data=validated_data,
            updated_by=security_context.user.user_id,
            security_context=security_context,
        )

        # Log audit event with before/after values
        await audit_logger.log_person_updated(
            security_context=security_context,
            person_id=person_id,
            old_data=current_person.dict(),
            new_data=updated_person.dict(),
        )

        logger.info(
            "Person updated successfully",
            person_id=str(person_id),
            user_id=str(security_context.user.user_id),
            changes=list(validated_data.keys()),
        )

        return updated_person

    except PersonNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Person not found"
        )
    except PersonAccessDeniedError:
        await audit_logger.log_access_denied(
            security_context=security_context,
            resource_type="person",
            resource_id=person_id,
            reason="Update access denied",
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied for update"
        )


@router.delete("/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_person(
    person_id: UUID,
    security_context: SecurityContext = Depends(get_security_context),
    person_service: PersonService = Depends(),
    hard_delete: bool = Query(False, description="Permanent deletion (admin only)"),
) -> None:
    """
    Soft delete person with GDPR compliance.

    - **Security**: Admin-only for hard delete, family/editor for soft delete
    - **GDPR**: Soft delete preserves audit trail, anonymization available
    - **Safety**: Confirmation required, audit trail maintained
    """
    try:
        # Check permissions
        if hard_delete:
            security_context.require_permission(Permission.SYSTEM_ADMIN)
        else:
            security_context.require_permission(Permission.DELETE_PERSON)

        # Get person data for audit
        person = await person_service.get_person(person_id, security_context)
        if not person:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Person not found"
            )

        # Perform deletion
        if hard_delete:
            await person_service.hard_delete_person(person_id, security_context)
        else:
            await person_service.soft_delete_person(person_id, security_context)

        # Log audit event
        await audit_logger.log_person_deleted(
            security_context=security_context,
            person_id=person_id,
            person_data=person.dict(),
        )

        logger.warning(
            "Person deleted",
            person_id=str(person_id),
            user_id=str(security_context.user.user_id),
            hard_delete=hard_delete,
            ip_address=security_context.ip_address,
        )

    except PersonNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Person not found"
        )
    except PersonAccessDeniedError:
        await audit_logger.log_access_denied(
            security_context=security_context,
            resource_type="person",
            resource_id=person_id,
            reason="Delete access denied",
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied for deletion"
        )
