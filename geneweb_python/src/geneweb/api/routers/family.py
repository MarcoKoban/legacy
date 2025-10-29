"""Family management API endpoints."""

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status

from ...db.database import Database
from ..dependencies import get_database
from ..models.family import (
    FamilyCreate,
    FamilyCreateResponse,
    FamilyDeleteResponse,
    FamilyListResponse,
    FamilyResponse,
    FamilyUpdate,
)
from ..services.family_service import FamilyService

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/v1/families", tags=["families"])


@router.post(
    "/",
    response_model=FamilyCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new family",
)
async def create_family(
    family_data: FamilyCreate,
    db: Database = Depends(get_database),
) -> FamilyCreateResponse:
    """
    Create a new family with parents, children, events, and sources.

    **Request Body:**
    - **father_ids**: List of father person IDs
    - **mother_ids**: List of mother person IDs
    - **children_ids**: List of children person IDs
    - **relation**: Type of relationship (married, not_married, etc.)
    - **marriage_date**: Marriage date in YYYY-MM-DD format (optional)
    - **marriage_place**: Marriage location (optional)
    - **marriage_source**: Marriage source (optional)
    - **divorce_info**: Divorce information (optional)
    - **comment**: General family comment (optional)
    - **events**: List of family events with witnesses and sources (optional)

    **Returns:**
    - Created family with all details including ID

    **Example:**
    ```json
    {
      "father_ids": ["p001"],
      "mother_ids": ["p002"],
      "children_ids": ["p003", "p004"],
      "relation": "married",
      "marriage_date": "1995-06-15",
      "marriage_place": "Paris, France",
      "marriage_source": "Mairie de Paris",
      "comment": "Beautiful ceremony",
      "events": [
        {
          "event_name": "marriage",
          "date": "1995-06-15",
          "place": "Paris, France",
          "source": "Marriage certificate",
          "witnesses": [
            {
              "person_id": "p005",
              "witness_kind": "witness"
            }
          ]
        }
      ]
    }
    ```
    """
    try:
        logger.info("Creating new family")

        # Validate that at least one parent exists
        if not family_data.father_ids and not family_data.mother_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one parent (father or mother) is required",
            )

        family_service = FamilyService(db)
        family = family_service.create_family(family_data)

        return FamilyCreateResponse(
            success=True,
            message=f"Family created successfully with ID: {family.id}",
            family=family,
        )

    except HTTPException:
        # Re-raise HTTP exceptions without modification
        raise
    except ValueError as e:
        logger.error("Validation error creating family", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error("Error creating family", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create family: {str(e)}",
        )


@router.get(
    "/{family_id}",
    response_model=FamilyResponse,
    summary="Get a family by ID",
)
async def get_family(
    family_id: str,
    db: Database = Depends(get_database),
) -> FamilyResponse:
    """
    Get a family by its ID.

    **Path Parameters:**
    - **family_id**: The unique identifier of the family

    **Returns:**
    - Family details including parents, children, and events

    **Raises:**
    - **404 Not Found**: If family doesn't exist
    """
    try:
        family_service = FamilyService(db)
        family = family_service.get_family(family_id)

        if family is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Family with ID {family_id} not found",
            )

        return family

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting family", family_id=family_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get family: {str(e)}",
        )


@router.get(
    "/",
    response_model=FamilyListResponse,
    summary="List all families",
)
async def list_families(
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(100, ge=1, le=1000, description="Limit for pagination"),
    db: Database = Depends(get_database),
) -> FamilyListResponse:
    """
    List all families with pagination.

    **Query Parameters:**
    - **offset**: Starting position (default: 0)
    - **limit**: Maximum number of results (default: 100, max: 1000)

    **Returns:**
    - List of families with pagination info
    """
    try:
        family_service = FamilyService(db)
        result = family_service.list_families(offset=offset, limit=limit)

        return FamilyListResponse(
            families=result["families"],
            total=result["total"],
            offset=offset,
            limit=limit,
        )

    except Exception as e:
        logger.error("Error listing families", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list families: {str(e)}",
        )


@router.patch(
    "/{family_id}",
    response_model=FamilyResponse,
    summary="Update a family",
)
async def update_family(
    family_id: str,
    update_data: FamilyUpdate,
    db: Database = Depends(get_database),
) -> FamilyResponse:
    """
    Update a family's information.

    **Path Parameters:**
    - **family_id**: The unique identifier of the family

    **Request Body:**
    - All fields are optional
    - Only provided fields will be updated

    **Returns:**
    - Updated family details

    **Raises:**
    - **404 Not Found**: If family doesn't exist
    """
    try:
        family_service = FamilyService(db)
        family = family_service.update_family(family_id, update_data)

        if family is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Family with ID {family_id} not found",
            )

        return family

    except HTTPException:
        raise
    except ValueError as e:
        logger.error("Validation error updating family", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error("Error updating family", family_id=family_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update family: {str(e)}",
        )


@router.delete(
    "/{family_id}",
    response_model=FamilyDeleteResponse,
    summary="Delete a family",
)
async def delete_family(
    family_id: str,
    db: Database = Depends(get_database),
) -> FamilyDeleteResponse:
    """
    Delete a family by ID.

    **Path Parameters:**
    - **family_id**: The unique identifier of the family

    **Returns:**
    - Success message with deleted family ID

    **Raises:**
    - **404 Not Found**: If family doesn't exist

    **Note:**
    - This does NOT delete the persons in the family
    - Only removes the family relationship
    """
    try:
        family_service = FamilyService(db)
        success = family_service.delete_family(family_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Family with ID {family_id} not found",
            )

        return FamilyDeleteResponse(
            success=True,
            message=f"Family {family_id} deleted successfully",
            family_id=family_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error deleting family", family_id=family_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete family: {str(e)}",
        )
