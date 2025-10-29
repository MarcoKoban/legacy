"""
Person models with GDPR compliance and encryption support.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

# Import from validation and security modules
try:
    from ..security.encryption import decrypt_sensitive_data, encrypt_sensitive_data
    from ..security.validation import sanitize_html, validate_person_name
except ImportError:
    # Fallback functions if security modules not available
    def validate_person_name(name: str) -> str:
        """Temporary name validation."""
        import re

        # Basic name validation
        cleaned = re.sub(r'[<>"\'\-\u001f]', "", name.strip())
        return cleaned

    def sanitize_html(text: str) -> str:
        """Temporary HTML sanitization."""
        import re

        # Basic HTML tag removal
        cleaned = re.sub(r"<[^>]+>", "", text)
        cleaned = re.sub(r"javascript:", "", cleaned, flags=re.IGNORECASE)
        return cleaned

    def encrypt_sensitive_data(data: str, context: str = "") -> str:
        """Fallback encryption function."""
        return data

    def decrypt_sensitive_data(data: str, context: str = "") -> str:
        """Fallback decryption function."""
        return data


class GDPRConsentStatus(str, Enum):
    """GDPR consent status enumeration."""

    PENDING = "pending"
    GRANTED = "granted"
    WITHDRAWN = "withdrawn"
    NOT_REQUIRED = "not_required"


class VisibilityLevel(str, Enum):
    """Data visibility levels for privacy control."""

    PUBLIC = "public"  # Visible to everyone
    FAMILY = "family"  # Visible to family members only
    RESTRICTED = "restricted"  # Visible to admins only
    PRIVATE = "private"  # Visible to owner and admins only


class PersonSex(str, Enum):
    """Person sex enumeration."""

    MALE = "male"
    FEMALE = "female"
    UNKNOWN = "unknown"


class PersonBase(BaseModel):
    """Base person model with common fields."""

    first_name: str = Field(
        ..., min_length=1, max_length=100, description="Person's first name"
    )
    last_name: str = Field(
        ..., min_length=1, max_length=100, description="Person's last name"
    )
    sex: PersonSex = Field(default=PersonSex.UNKNOWN, description="Person's sex")
    birth_date: Optional[str] = Field(
        None, description="Birth date in YYYY-MM-DD format"
    )
    death_date: Optional[str] = Field(
        None, description="Death date in YYYY-MM-DD format"
    )
    birth_place: Optional[str] = Field(None, max_length=255, description="Birth place")
    death_place: Optional[str] = Field(None, max_length=255, description="Death place")
    occupation: Optional[str] = Field(
        None, max_length=255, description="Person's occupation"
    )
    notes: Optional[str] = Field(None, max_length=5000, description="Additional notes")
    visibility_level: VisibilityLevel = Field(
        default=VisibilityLevel.FAMILY, description="Data visibility level"
    )

    # Privacy controls
    anonymized: bool = Field(
        default=False, description="Whether personal data has been anonymized"
    )
    is_deleted: bool = Field(default=False, description="Soft delete flag")

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_names(cls, v):
        """Validate and sanitize person names."""
        if not v or not v.strip():
            raise ValueError("Name cannot be empty")
        return validate_person_name(v)

    @field_validator("notes", "occupation", "birth_place", "death_place")
    @classmethod
    def sanitize_text_fields(cls, v):
        """Sanitize text fields to prevent XSS."""
        if v is None:
            return None
        return sanitize_html(v)

    @field_validator("birth_date", "death_date")
    @classmethod
    def validate_dates(cls, v):
        """Validate date format."""
        if v is None:
            return None
        # Basic date validation
        if not v.strip():
            return None
        return v.strip()


class PersonCreate(PersonBase):
    """Model for creating a new person."""

    # Additional fields for creation
    creator_notes: Optional[str] = Field(
        None, max_length=1000, description="Notes from creator"
    )

    model_config = ConfigDict(
        str_strip_whitespace=True, validate_assignment=True, use_enum_values=True
    )


class PersonUpdate(BaseModel):
    """Model for updating an existing person."""

    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    sex: Optional[PersonSex] = None
    birth_date: Optional[str] = None
    death_date: Optional[str] = None
    birth_place: Optional[str] = Field(None, max_length=255)
    death_place: Optional[str] = Field(None, max_length=255)
    occupation: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = Field(None, max_length=5000)
    visibility_level: Optional[VisibilityLevel] = None

    # GDPR updates
    consent_status: Optional[GDPRConsentStatus] = None
    data_processing_purposes: Optional[List[str]] = None

    model_config = ConfigDict(
        str_strip_whitespace=True, validate_assignment=True, use_enum_values=True
    )

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_names(cls, v):
        """Validate and sanitize person names."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Name cannot be empty")
            return validate_person_name(v)
        return v

    @field_validator("notes", "occupation", "birth_place", "death_place")
    @classmethod
    def sanitize_text_fields(cls, v):
        """Sanitize text fields to prevent XSS."""
        if v is not None:
            return sanitize_html(v)
        return v


class PersonResponse(PersonBase):
    """Model for person API responses."""

    id: UUID = Field(..., description="Unique person identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    version: int = Field(default=1, description="Data version for optimistic locking")

    # Computed fields
    is_living: bool = Field(default=True, description="Whether person is still living")
    age: Optional[int] = Field(None, description="Current age or age at death")

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class PersonSummary(BaseModel):
    """Summary model for person listings."""

    id: UUID = Field(..., description="Unique person identifier")
    first_name: str = Field(..., description="Person's first name")
    last_name: str = Field(..., description="Person's last name")
    sex: PersonSex = Field(default=PersonSex.UNKNOWN, description="Person's sex")
    birth_date: Optional[str] = Field(None, description="Birth date")
    death_date: Optional[str] = Field(None, description="Death date")
    is_living: bool = Field(default=True, description="Whether person is still living")
    age: Optional[int] = Field(None, description="Current age or age at death")

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class PersonSearchFilters(BaseModel):
    """Model for person search filters."""

    first_name: Optional[str] = Field(None, description="Filter by first name")
    last_name: Optional[str] = Field(None, description="Filter by last name")
    sex: Optional[PersonSex] = Field(None, description="Filter by sex")
    birth_year_min: Optional[int] = Field(None, description="Minimum birth year")
    birth_year_max: Optional[int] = Field(None, description="Maximum birth year")
    is_living: Optional[bool] = Field(None, description="Filter by living status")

    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")
    sort_by: str = Field(default="last_name", description="Sort field")
    sort_order: str = Field(default="asc", description="Sort order (asc/desc)")

    model_config = ConfigDict(use_enum_values=True)


class PersonListResponse(BaseModel):
    """Response model for person list."""

    items: List[PersonSummary] = Field(..., description="List of persons")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether next page exists")
    has_previous: bool = Field(..., description="Whether previous page exists")

    model_config = ConfigDict(from_attributes=True)


class PersonSearchResponse(BaseModel):
    """Response model for person search results."""

    persons: List[PersonResponse] = Field(..., description="List of matching persons")
    total_count: int = Field(..., description="Total number of matching results")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Results per page")
    has_more: bool = Field(..., description="Whether more results are available")


class GDPRExportData(BaseModel):
    """Model for GDPR data export."""

    person_id: UUID = Field(..., description="Person identifier")
    export_date: datetime = Field(..., description="Export generation date")
    personal_data: Dict[str, Any] = Field(..., description="All personal data")
    consent_history: List[Dict[str, Any]] = Field(
        ..., description="Consent change history"
    )
    data_usage_log: List[Dict[str, Any]] = Field(
        ..., description="Data access and usage log"
    )

    model_config = ConfigDict(from_attributes=True)


class GDPRConsent(BaseModel):
    """Model for a GDPR consent record."""

    purpose: str = Field(..., description="Purpose of data processing")
    status: GDPRConsentStatus = Field(..., description="Consent status")
    granted_at: Optional[datetime] = Field(None, description="When consent was granted")
    withdrawn_at: Optional[datetime] = Field(
        None, description="When consent was withdrawn"
    )
    ip_address: Optional[str] = Field(None, description="IP address of consent action")
    user_agent: Optional[str] = Field(None, description="User agent of consent action")

    model_config = ConfigDict(use_enum_values=True)


class GDPRConsentRequest(BaseModel):
    """Model for GDPR consent management."""

    person_id: UUID = Field(..., description="Person identifier")
    consent_status: GDPRConsentStatus = Field(..., description="New consent status")
    processing_purposes: List[str] = Field(..., description="Data processing purposes")
    consent_date: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Consent timestamp",
    )
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")

    model_config = ConfigDict(use_enum_values=True)


class AuditLogEntry(BaseModel):
    """Model for audit log entries."""

    id: UUID = Field(default_factory=uuid4, description="Audit entry identifier")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Event timestamp",
    )
    user_id: str = Field(..., description="User who performed the action")
    action: str = Field(..., description="Action performed")
    resource_type: str = Field(..., description="Type of resource affected")
    resource_id: Optional[str] = Field(
        None, description="Identifier of affected resource"
    )
    details: Dict[str, Any] = Field(
        default_factory=dict, description="Additional event details"
    )
    ip_address: Optional[str] = Field(None, description="Client IP address")
    user_agent: Optional[str] = Field(None, description="Client user agent")
    session_id: Optional[str] = Field(None, description="Session identifier")

    # Security fields
    checksum: Optional[str] = Field(
        None, description="Cryptographic checksum for integrity"
    )
    encrypted_sensitive_data: Optional[str] = Field(
        None, description="Encrypted sensitive data"
    )

    model_config = ConfigDict(from_attributes=True)


class PersonAccessLog(BaseModel):
    """Model for tracking person data access."""

    person_id: UUID = Field(..., description="Person whose data was accessed")
    accessed_by: str = Field(..., description="User who accessed the data")
    access_time: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Access timestamp",
    )
    access_type: str = Field(
        ..., description="Type of access (read, update, export, etc.)"
    )
    fields_accessed: List[str] = Field(
        default_factory=list, description="Specific fields accessed"
    )
    purpose: Optional[str] = Field(None, description="Purpose of data access")
    ip_address: Optional[str] = Field(None, description="Client IP address")

    model_config = ConfigDict(from_attributes=True)


# GDPR-specific models for GDPR router
class PersonGDPRExport(BaseModel):
    """Complete person data export for GDPR Article 15 (Right of Access)."""

    person_data: Dict[str, Any] = Field(..., description="Complete person data")
    audit_logs: List[Dict[str, Any]] = Field(
        default_factory=list, description="Audit trail of data access"
    )
    gdpr_consents: List[Dict[str, Any]] = Field(
        default_factory=list, description="GDPR consent history"
    )
    export_requested_by: str = Field(..., description="User who requested export")
    export_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Export timestamp",
    )
    lawful_basis: str = Field(..., description="Legal basis for data processing")
    data_retention_period: str = Field(..., description="How long data is retained")
    third_party_processors: List[str] = Field(
        default_factory=list, description="Third parties with data access"
    )

    model_config = ConfigDict(from_attributes=True)


class PersonAnonymizationRequest(BaseModel):
    """Request to anonymize person data for GDPR Article 17 (Right to be Forgotten)."""

    person_id: UUID = Field(..., description="Person to anonymize")
    reason: str = Field(..., description="Reason for anonymization request")
    confirm_irreversible: bool = Field(
        ..., description="Confirmation that operation is irreversible"
    )
    legal_basis: Optional[str] = Field(
        None, description="Legal basis for anonymization"
    )
    retain_statistical: bool = Field(
        default=True, description="Retain anonymized statistical data"
    )

    model_config = ConfigDict(from_attributes=True)


class PersonConsentUpdate(BaseModel):
    """Update GDPR consent for person data processing."""

    consents: List[GDPRConsentRequest] = Field(
        ..., description="List of consent updates"
    )
    notes: Optional[str] = Field(
        None, description="Optional notes about consent update"
    )

    model_config = ConfigDict(from_attributes=True)
