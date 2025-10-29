"""
Person service with secure database operations and GDPR compliance.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, List, Optional
from uuid import UUID, uuid4

import structlog

from ..models.person import (
    GDPRConsent,
    PersonListResponse,
    PersonResponse,
    PersonSearchFilters,
    PersonSummary,
)
from ..security.auth import SecurityContext
from ..security.encryption import (
    decrypt_sensitive_data,
    encrypt_sensitive_data,
)

if TYPE_CHECKING:
    from geneweb.db.database import Database

logger = structlog.get_logger(__name__)


class PersonNotFoundError(Exception):
    """Person not found exception."""

    pass


class PersonAccessDeniedError(Exception):
    """Person access denied exception."""

    pass


class PersonVersionConflictError(Exception):
    """Version conflict during update."""

    pass


class PersonService:
    """Service for person data management with security and GDPR compliance."""

    def __init__(self, database: Optional["Database"] = None):
        # Initialize in-memory storage (in production, use proper database)
        self._persons: Dict[UUID, Dict[str, Any]] = {}
        self._consent_history: Dict[UUID, List[GDPRConsent]] = {}
        self.database = database

        # Initialize in-memory collection for core.person.Person objects
        self._persons_collection: List[Any] = []  # List[core.person.Person]
        self._uuid_to_index: Dict[UUID, int] = {}
        self._index_to_uuid: Dict[int, UUID] = {}

        self._load_from_geneweb_db()

    def _load_from_geneweb_db(self):
        """Load existing data from Geneweb database format."""
        try:
            # This would integrate with the existing outbase.py system
            # For now, we'll create a simple in-memory structure
            logger.info("Loading persons from Geneweb database")
            # TODO: Implement actual database loading
        except Exception as e:
            logger.warning("Failed to load existing database", error=str(e))

    def _encrypt_person_data(self, person_data: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt sensitive person data fields."""
        encrypted_data = person_data.copy()

        # Fields that need encryption
        sensitive_fields = [
            "birth_date",
            "birth_place",
            "death_date",
            "death_place",
            "email",
            "phone",
            "address",
        ]

        for field in sensitive_fields:
            if field in encrypted_data and encrypted_data[field] is not None:
                encrypted_data[f"{field}_encrypted"] = encrypt_sensitive_data(
                    str(encrypted_data[field])
                )
                # Remove plaintext
                del encrypted_data[field]

        return encrypted_data

    def _decrypt_person_data(self, encrypted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt sensitive person data fields."""
        decrypted_data = encrypted_data.copy()

        # Fields that were encrypted
        sensitive_fields = [
            "birth_date",
            "birth_place",
            "death_date",
            "death_place",
            "email",
            "phone",
            "address",
        ]

        for field in sensitive_fields:
            encrypted_field = f"{field}_encrypted"
            if encrypted_field in decrypted_data:
                try:
                    decrypted_value = decrypt_sensitive_data(
                        decrypted_data[encrypted_field]
                    )
                    if decrypted_value is not None:
                        # Convert back to proper type
                        if field in ["birth_date", "death_date"] and decrypted_value:
                            try:
                                decrypted_data[field] = datetime.fromisoformat(
                                    decrypted_value.replace("Z", "+00:00")
                                ).date()
                            except ValueError:
                                decrypted_data[field] = decrypted_value
                        else:
                            decrypted_data[field] = decrypted_value

                    # Remove encrypted field from response
                    del decrypted_data[encrypted_field]

                except Exception as e:
                    logger.warning(f"Failed to decrypt field {field}", error=str(e))
                    # Keep encrypted field but don't expose plaintext
                    del decrypted_data[encrypted_field]

        return decrypted_data

    def _filter_person_data_by_access_level(
        self, person_data: Dict[str, Any], security_context: SecurityContext
    ) -> Dict[str, Any]:
        """Filter person data based on user access level."""

        # Admin and editor see everything
        if security_context.user.role.value in ["admin", "editor"]:
            return person_data

        # Family members see family data
        if security_context.user.role.value == "family":
            person_id = person_data.get("id")
            if (
                person_id == security_context.user.family_person_id
                or person_id in security_context.user.related_person_ids
            ):
                return person_data

            # For non-family members, filter sensitive data
            filtered = person_data.copy()
            sensitive_fields = [
                "email",
                "phone",
                "address",
                "birth_place",
                "death_place",
            ]
            for field in sensitive_fields:
                if field in filtered:
                    filtered[field] = None
            return filtered

        public_fields = [
            "id",
            "first_name",
            "last_name",
            "sex",
            "birth_date",
            "death_date",
            "is_living",
            "age",
            "created_at",
            "updated_at",
        ]

        return {k: v for k, v in person_data.items() if k in public_fields}

    async def create_person(
        self,
        person_data: Dict[str, Any],
        created_by: UUID,
        security_context: SecurityContext,
    ) -> PersonResponse:
        """Create a new person with encryption and audit trail."""

        person_id = uuid4()
        now = datetime.now(timezone.utc)

        # Prepare person data
        person_record = {
            "id": person_id,
            "created_at": now,
            "updated_at": now,
            "version": 1,
            "is_deleted": False,
            "anonymized": False,
            "visibility_level": "family",
            "has_valid_consent": True,
            "consent_status": "granted",
            "created_by": created_by,
            **person_data,
        }

        # Calculate computed fields
        if person_record.get("birth_date") and not person_record.get("death_date"):
            # Convert birth_date string to date object for calculation
            birth_date_str = person_record["birth_date"]
            if isinstance(birth_date_str, str):
                from datetime import date

                birth_date = date.fromisoformat(birth_date_str)
            else:
                birth_date = birth_date_str
            age = (datetime.now().date() - birth_date).days // 365
            person_record["age"] = age
            person_record["is_living"] = True
        else:
            person_record["is_living"] = False

        # Encrypt sensitive data
        encrypted_record = self._encrypt_person_data(person_record)

        # Store in memory (in production, use proper database)
        self._persons[person_id] = encrypted_record

        # Also add to _persons_collection for database integration
        index = len(self._persons_collection)
        self._persons_collection.append(
            encrypted_record
        )  # TODO: convert to core.person.Person
        self._uuid_to_index[person_id] = index
        self._index_to_uuid[index] = person_id

        # Store consent
        if "gdpr_consents" in person_data:
            self._consent_history[person_id] = person_data["gdpr_consents"]

        # Save to Geneweb format
        await self._save_to_geneweb_db()

        # Return decrypted response
        decrypted_data = self._decrypt_person_data(encrypted_record)

        # Convert date objects to strings for Pydantic
        if "birth_date" in decrypted_data and not isinstance(
            decrypted_data["birth_date"], str
        ):
            from datetime import date

            if isinstance(decrypted_data["birth_date"], date):
                decrypted_data["birth_date"] = decrypted_data["birth_date"].isoformat()
        if "death_date" in decrypted_data and not isinstance(
            decrypted_data["death_date"], str
        ):
            from datetime import date

            if isinstance(decrypted_data["death_date"], date):
                decrypted_data["death_date"] = decrypted_data["death_date"].isoformat()

        return PersonResponse(**decrypted_data)

    async def get_person(
        self, person_id: UUID, security_context: SecurityContext
    ) -> Optional[PersonResponse]:
        """Get person by ID with access control."""

        if person_id not in self._persons:
            return None

        encrypted_data = self._persons[person_id]

        # Check if person is deleted
        if encrypted_data.get("is_deleted", False):
            # Only admins can see deleted persons
            if security_context.user.role.value != "admin":
                return None

        # Decrypt data
        decrypted_data = self._decrypt_person_data(encrypted_data)

        # Filter based on access level
        filtered_data = self._filter_person_data_by_access_level(
            decrypted_data, security_context
        )

        # Convert date objects to strings for Pydantic
        if "birth_date" in filtered_data and not isinstance(
            filtered_data["birth_date"], str
        ):
            from datetime import date

            if isinstance(filtered_data["birth_date"], date):
                filtered_data["birth_date"] = filtered_data["birth_date"].isoformat()
        if "death_date" in filtered_data and not isinstance(
            filtered_data["death_date"], str
        ):
            from datetime import date

            if isinstance(filtered_data["death_date"], date):
                filtered_data["death_date"] = filtered_data["death_date"].isoformat()

        return PersonResponse(**filtered_data)

    async def get_person_complete(
        self,
        person_id: UUID,
        security_context: SecurityContext,
        decrypt_sensitive: bool = False,
    ) -> Optional[PersonResponse]:
        """Get complete person data including encrypted fields for admin operations."""

        if person_id not in self._persons:
            return None

        encrypted_data = self._persons[person_id]

        if decrypt_sensitive:
            data = self._decrypt_person_data(encrypted_data)
        else:
            data = encrypted_data

        return PersonResponse(**data)

    async def update_person(
        self,
        person_id: UUID,
        update_data: Dict[str, Any],
        updated_by: UUID,
        security_context: SecurityContext,
    ) -> PersonResponse:
        """Update person with version control and audit trail."""

        if person_id not in self._persons:
            raise PersonNotFoundError(f"Person {person_id} not found")

        current_data = self._persons[person_id].copy()

        # Version control check
        current_version = current_data.get("version", 1)
        if "version" in update_data and update_data["version"] != current_version:
            raise PersonVersionConflictError("Version conflict during update")

        # Update fields
        current_data.update(update_data)
        current_data["updated_at"] = datetime.now(timezone.utc)
        current_data["version"] = current_version + 1
        current_data["updated_by"] = updated_by

        # Re-encrypt sensitive data
        encrypted_data = self._encrypt_person_data(current_data)

        # Store updated data
        self._persons[person_id] = encrypted_data

        # Also update _persons_collection if person exists there
        if person_id in self._uuid_to_index:
            index = self._uuid_to_index[person_id]
            self._persons_collection[index] = encrypted_data

        # Save to Geneweb format
        await self._save_to_geneweb_db()

        # Return decrypted response
        decrypted_data = self._decrypt_person_data(encrypted_data)
        filtered_data = self._filter_person_data_by_access_level(
            decrypted_data, security_context
        )

        return PersonResponse(**filtered_data)

    async def soft_delete_person(
        self, person_id: UUID, security_context: SecurityContext
    ):
        """Soft delete person (mark as deleted)."""

        if person_id not in self._persons:
            raise PersonNotFoundError(f"Person {person_id} not found")

        self._persons[person_id]["is_deleted"] = True
        self._persons[person_id]["deleted_at"] = datetime.now(timezone.utc)

        await self._save_to_geneweb_db()

    async def hard_delete_person(
        self, person_id: UUID, security_context: SecurityContext
    ):
        """Hard delete person (permanent removal)."""

        if person_id not in self._persons:
            raise PersonNotFoundError(f"Person {person_id} not found")

        del self._persons[person_id]
        if person_id in self._consent_history:
            del self._consent_history[person_id]

        await self._save_to_geneweb_db()

    async def anonymize_person(
        self,
        person_id: UUID,
        anonymized_data: Dict[str, Any],
        security_context: SecurityContext,
    ):
        """Anonymize person data according to GDPR."""

        if person_id not in self._persons:
            raise PersonNotFoundError(f"Person {person_id} not found")

        # Store anonymized data
        encrypted_data = self._encrypt_person_data(anonymized_data)
        self._persons[person_id] = encrypted_data

        await self._save_to_geneweb_db()

    async def list_persons(
        self, filters: PersonSearchFilters, security_context: SecurityContext
    ) -> PersonListResponse:
        """List persons with filtering and pagination."""

        # Filter persons based on criteria and access level
        filtered_persons = []

        for person_id, encrypted_data in self._persons.items():
            # Skip deleted persons unless admin
            if (
                encrypted_data.get("is_deleted", False)
                and security_context.user.role.value != "admin"
            ):
                continue

            # Decrypt for filtering
            person_data = self._decrypt_person_data(encrypted_data)

            # Apply search filters
            if self._matches_filters(person_data, filters):
                # Filter data by access level
                filtered_data = self._filter_person_data_by_access_level(
                    person_data, security_context
                )
                filtered_persons.append(PersonSummary(**filtered_data))

        # Sort results
        if filters.sort_by == "last_name":
            filtered_persons.sort(
                key=lambda p: p.last_name, reverse=(filters.sort_order == "desc")
            )
        elif filters.sort_by == "birth_date":
            filtered_persons.sort(
                key=lambda p: p.birth_date or datetime.min.date(),
                reverse=(filters.sort_order == "desc"),
            )

        # Pagination
        total = len(filtered_persons)
        start = (filters.page - 1) * filters.page_size
        end = start + filters.page_size
        page_items = filtered_persons[start:end]

        total_pages = (total + filters.page_size - 1) // filters.page_size

        return PersonListResponse(
            items=page_items,
            total=total,
            page=filters.page,
            page_size=filters.page_size,
            total_pages=total_pages,
            has_next=filters.page < total_pages,
            has_previous=filters.page > 1,
        )

    def _matches_filters(
        self, person_data: Dict[str, Any], filters: PersonSearchFilters
    ) -> bool:
        """Check if person matches search filters."""

        if filters.first_name:
            if (
                not person_data.get("first_name", "")
                .lower()
                .startswith(filters.first_name.lower())
            ):
                return False

        if filters.last_name:
            if (
                not person_data.get("last_name", "")
                .lower()
                .startswith(filters.last_name.lower())
            ):
                return False

        if filters.sex:
            if person_data.get("sex") != filters.sex:
                return False

        if filters.birth_year_min or filters.birth_year_max:
            birth_date = person_data.get("birth_date")
            if birth_date:
                birth_year = birth_date.year
                if filters.birth_year_min and birth_year < filters.birth_year_min:
                    return False
                if filters.birth_year_max and birth_year > filters.birth_year_max:
                    return False

        if filters.is_living is not None:
            if person_data.get("is_living") != filters.is_living:
                return False

        return True

    async def get_consent_history(self, person_id: UUID) -> List[GDPRConsent]:
        """Get GDPR consent history for person."""
        return self._consent_history.get(person_id, [])

    async def update_consent(
        self,
        person_id: UUID,
        consents: List[GDPRConsent],
        updated_by: UUID,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> List[GDPRConsent]:
        """Update GDPR consent for person."""

        # Update consent with timestamp and user info
        for consent in consents:
            if consent.status.value == "granted":
                consent.granted_at = datetime.now(timezone.utc)
            elif consent.status.value == "withdrawn":
                consent.withdrawn_at = datetime.now(timezone.utc)

            consent.ip_address = ip_address
            consent.user_agent = user_agent

        # Store consent history
        if person_id not in self._consent_history:
            self._consent_history[person_id] = []

        self._consent_history[person_id].extend(consents)

        # Update person's consent status
        if person_id in self._persons:
            has_valid_consent = any(
                consent.status.value == "granted" for consent in consents
            )
            self._persons[person_id]["has_valid_consent"] = has_valid_consent

            # Update consent status
            if has_valid_consent:
                self._persons[person_id]["consent_status"] = "granted"
            else:
                self._persons[person_id]["consent_status"] = "withdrawn"

        await self._save_to_geneweb_db()

        return consents

    async def _save_to_geneweb_db(self):
        """Save current state to Geneweb database format."""
        try:
            # This would integrate with the existing outbase.py system
            # For now, we'll implement a basic version

            # Convert our data structure to Geneweb format
            # This is a simplified implementation
            logger.info("Saving persons to Geneweb database format")

            # In a real implementation, this would:
            # 1. Convert our person data to Geneweb's internal format
            # 2. Use the existing outbase.py functions to save
            # 3. Maintain compatibility with existing Geneweb tools

        except Exception as e:
            logger.error("Failed to save to Geneweb database", error=str(e))
