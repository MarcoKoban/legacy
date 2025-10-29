"""Family models for API with events, witnesses, and sources."""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RelationKind(str, Enum):
    """Type of relationship between parents."""

    MARRIED = "married"
    NOT_MARRIED = "not_married"
    ENGAGED = "engaged"
    NO_MENTION = "no_mention"
    MARRIAGE_BANN = "marriage_bann"
    MARRIAGE_CONTRACT = "marriage_contract"
    MARRIAGE_LICENSE = "marriage_license"
    PACS = "pacs"
    RESIDENCE = "residence"


class DivorceStatus(str, Enum):
    """Divorce status for a family."""

    NOT_DIVORCED = "not_divorced"
    DIVORCED = "divorced"
    SEPARATED = "separated"


class WitnessKind(str, Enum):
    """Type of witness."""

    WITNESS = "witness"
    WITNESS_GODPARENT = "witness_godparent"
    WITNESS_CIVILOFFICER = "witness_civilofficer"
    WITNESS_RELIGIOUSOFFICER = "witness_religiousofficer"
    WITNESS_INFORMANT = "witness_informant"
    WITNESS_ATTENDING = "witness_attending"
    WITNESS_MENTIONED = "witness_mentioned"
    WITNESS_OTHER = "witness_other"


class FamilyEventName(str, Enum):
    """Types of family events."""

    MARRIAGE = "marriage"
    NO_MARRIAGE = "no_marriage"
    NO_MENTION = "no_mention"
    ENGAGE = "engage"
    DIVORCE = "divorce"
    SEPARATED = "separated"
    ANNULATION = "annulation"
    MARRIAGE_BANN = "marriage_bann"
    MARRIAGE_CONTRACT = "marriage_contract"
    MARRIAGE_LICENSE = "marriage_license"
    PACS = "pacs"
    RESIDENCE = "residence"
    CUSTOM = "custom"


class WitnessInfo(BaseModel):
    """Information about a witness at an event."""

    person_id: str = Field(..., description="ID of the witness person")
    witness_kind: WitnessKind = Field(
        default=WitnessKind.WITNESS, description="Type of witness"
    )


class FamilyEventBase(BaseModel):
    """Base model for a family event."""

    event_name: FamilyEventName = Field(..., description="Type of family event")
    custom_name: Optional[str] = Field(
        None, description="Custom event name if event_name is CUSTOM"
    )
    date: Optional[str] = Field(None, description="Event date (YYYY-MM-DD format)")
    place: Optional[str] = Field(None, max_length=255, description="Event location")
    note: Optional[str] = Field(None, max_length=2000, description="Event notes")
    source: Optional[str] = Field(
        None, max_length=500, description="Source of information"
    )
    reason: Optional[str] = Field(None, max_length=500, description="Event reason")
    witnesses: List[WitnessInfo] = Field(
        default_factory=list, description="List of witnesses"
    )


class FamilyEventCreate(FamilyEventBase):
    """Model for creating a family event."""

    pass


class FamilyEventResponse(FamilyEventBase):
    """Model for family event in responses."""

    id: Optional[str] = Field(None, description="Event ID")


class DivorceInfo(BaseModel):
    """Information about divorce."""

    divorce_status: DivorceStatus = Field(
        default=DivorceStatus.NOT_DIVORCED, description="Divorce status"
    )
    divorce_date: Optional[str] = Field(
        None, description="Divorce date (YYYY-MM-DD format)"
    )


class FamilyBase(BaseModel):
    """Base family model with common fields."""

    relation: RelationKind = Field(
        default=RelationKind.MARRIED, description="Type of relationship"
    )
    divorce_info: Optional[DivorceInfo] = Field(
        None, description="Divorce information if applicable"
    )
    marriage_date: Optional[str] = Field(
        None, description="Marriage date (YYYY-MM-DD format)"
    )
    marriage_place: Optional[str] = Field(
        None, max_length=255, description="Marriage location"
    )
    marriage_source: Optional[str] = Field(
        None, max_length=500, description="Marriage source"
    )
    comment: Optional[str] = Field(
        None, max_length=2000, description="General family comment"
    )
    events: List[FamilyEventCreate] = Field(
        default_factory=list, description="List of family events"
    )

    @field_validator("marriage_date")
    @classmethod
    def validate_marriage_date(cls, v):
        """Validate marriage date format."""
        if v is None:
            return None
        # Basic validation - could be enhanced
        if not v.strip():
            return None
        return v.strip()


class FamilyCreate(FamilyBase):
    """Model for creating a new family."""

    father_ids: List[str] = Field(
        default_factory=list, description="List of father person IDs"
    )
    mother_ids: List[str] = Field(
        default_factory=list, description="List of mother person IDs"
    )
    children_ids: List[str] = Field(
        default_factory=list, description="List of children person IDs"
    )

    @field_validator("father_ids", "mother_ids", "children_ids")
    @classmethod
    def validate_person_ids(cls, v):
        """Ensure person IDs are unique."""
        if v is None:
            return []
        # Remove duplicates while preserving order
        seen = set()
        unique = []
        for item in v:
            if item not in seen:
                seen.add(item)
                unique.append(item)
        return unique


class FamilyUpdate(BaseModel):
    """Model for updating a family."""

    relation: Optional[RelationKind] = None
    divorce_info: Optional[DivorceInfo] = None
    marriage_date: Optional[str] = None
    marriage_place: Optional[str] = None
    marriage_source: Optional[str] = None
    comment: Optional[str] = None
    father_ids: Optional[List[str]] = None
    mother_ids: Optional[List[str]] = None
    children_ids: Optional[List[str]] = None
    events: Optional[List[FamilyEventCreate]] = None


class FamilyResponse(FamilyBase):
    """Model for family in API responses."""

    id: str = Field(..., description="Family ID")
    father_ids: List[str] = Field(
        default_factory=list, description="List of father person IDs"
    )
    mother_ids: List[str] = Field(
        default_factory=list, description="List of mother person IDs"
    )
    children_ids: List[str] = Field(
        default_factory=list, description="List of children person IDs"
    )
    events: List[FamilyEventResponse] = Field(
        default_factory=list, description="List of family events"
    )
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)


class FamilyListResponse(BaseModel):
    """Response model for listing families."""

    families: List[FamilyResponse] = Field(..., description="List of families")
    total: int = Field(..., description="Total number of families")
    offset: int = Field(default=0, description="Offset for pagination")
    limit: int = Field(default=100, description="Limit for pagination")


class FamilyCreateResponse(BaseModel):
    """Response model for family creation."""

    success: bool = Field(..., description="Whether creation was successful")
    message: str = Field(..., description="Success or error message")
    family: FamilyResponse = Field(..., description="Created family data")


class FamilyDeleteResponse(BaseModel):
    """Response model for family deletion."""

    success: bool = Field(..., description="Whether deletion was successful")
    message: str = Field(..., description="Success or error message")
    family_id: str = Field(..., description="ID of deleted family")
