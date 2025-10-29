"""
Adapter to convert between DB Person models and API Person models.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

import structlog

from ...core.person import Access
from ...core.person import Person as DBPerson
from ...core.person import Sex as DBSex
from ..models.person import (
    GDPRConsentStatus,
    PersonResponse,
    PersonSex,
    VisibilityLevel,
)

logger = structlog.get_logger(__name__)


class PersonAdapter:
    """Adapter to convert between database and API person models."""

    @staticmethod
    def db_sex_to_api_sex(db_sex: DBSex) -> PersonSex:
        """Convert database Sex enum to API PersonSex enum."""
        mapping = {
            DBSex.MALE: PersonSex.MALE,
            DBSex.FEMALE: PersonSex.FEMALE,
            DBSex.NEUTER: PersonSex.UNKNOWN,
        }
        return mapping.get(db_sex, PersonSex.UNKNOWN)

    @staticmethod
    def api_sex_to_db_sex(api_sex: PersonSex) -> DBSex:
        """Convert API PersonSex enum to database Sex enum."""
        mapping = {
            PersonSex.MALE: DBSex.MALE,
            PersonSex.FEMALE: DBSex.FEMALE,
            PersonSex.UNKNOWN: DBSex.NEUTER,
        }
        return mapping.get(api_sex, DBSex.NEUTER)

    @staticmethod
    def db_access_to_visibility(access: Access) -> VisibilityLevel:
        """Convert database Access to API VisibilityLevel."""
        mapping = {
            Access.PUBLIC: VisibilityLevel.PUBLIC,
            Access.SEMI_PUBLIC: VisibilityLevel.FAMILY,
            Access.PRIVATE: VisibilityLevel.PRIVATE,
            Access.IF_TITLES: VisibilityLevel.RESTRICTED,
        }
        return mapping.get(access, VisibilityLevel.FAMILY)

    @staticmethod
    def visibility_to_db_access(visibility: VisibilityLevel) -> Access:
        """Convert API VisibilityLevel to database Access."""
        mapping = {
            VisibilityLevel.PUBLIC: Access.PUBLIC,
            VisibilityLevel.FAMILY: Access.SEMI_PUBLIC,
            VisibilityLevel.PRIVATE: Access.PRIVATE,
            VisibilityLevel.RESTRICTED: Access.IF_TITLES,
        }
        return mapping.get(visibility, Access.SEMI_PUBLIC)

    @staticmethod
    def db_person_to_api_response(
        db_person: DBPerson, person_id: Optional[UUID] = None
    ) -> PersonResponse:
        """
        Convert database Person to API PersonResponse.

        Args:
            db_person: Person object from the database
            person_id: Optional UUID for the person (generated if not provided)

        Returns:
            PersonResponse object ready for API
        """
        if person_id is None:
            person_id = uuid4()

        now = datetime.now(timezone.utc)

        # Extract birth date
        birth_date_str = None
        if db_person.birth:
            if (
                hasattr(db_person.birth, "calendar_date")
                and db_person.birth.calendar_date
            ):
                # Event with calendar_date
                cd = db_person.birth.calendar_date
                birth_date_str = f"{cd.year:04d}-{cd.month:02d}-{cd.day:02d}"
            elif hasattr(db_person.birth, "date") and db_person.birth.date:
                # Event with date property
                birth_date_str = str(db_person.birth.date)

        # Extract death date
        death_date_str = None
        is_living = True
        if db_person.death:
            if hasattr(db_person.death, "event") and db_person.death.event:
                # DeathInfo with event
                if (
                    hasattr(db_person.death.event, "calendar_date")
                    and db_person.death.event.calendar_date
                ):
                    cd = db_person.death.event.calendar_date
                    death_date_str = f"{cd.year:04d}-{cd.month:02d}-{cd.day:02d}"
                    is_living = False
            elif (
                hasattr(db_person.death, "calendar_date")
                and db_person.death.calendar_date
            ):
                # Direct Event
                cd = db_person.death.calendar_date
                death_date_str = f"{cd.year:04d}-{cd.month:02d}-{cd.day:02d}"
                is_living = False

        # Extract places
        birth_place = None
        if db_person.birth:
            if hasattr(db_person.birth, "place") and db_person.birth.place:
                birth_place = str(db_person.birth.place)

        death_place = None
        if db_person.death:
            if hasattr(db_person.death, "event") and db_person.death.event:
                if (
                    hasattr(db_person.death.event, "place")
                    and db_person.death.event.place
                ):
                    death_place = str(db_person.death.event.place)
            elif hasattr(db_person.death, "place") and db_person.death.place:
                death_place = str(db_person.death.place)

        # Extract occupation
        occupation = db_person.occupation if hasattr(db_person, "occupation") else None

        # Create response
        return PersonResponse(
            id=person_id,
            first_name=db_person.first_name or "",
            last_name=db_person.surname or "",
            sex=PersonAdapter.db_sex_to_api_sex(db_person.sex),
            birth_date=birth_date_str,
            death_date=death_date_str,
            birth_place=birth_place,
            death_place=death_place,
            occupation=occupation,
            notes=db_person.notes or "",
            visibility_level=PersonAdapter.db_access_to_visibility(db_person.access),
            has_valid_consent=False,  # Default, should be managed separately
            consent_status=GDPRConsentStatus.NOT_REQUIRED,
            is_living=is_living,
            age=db_person.age if hasattr(db_person, "age") else None,
            created_at=now,
            updated_at=now,
            version=1,
            is_deleted=False,
            anonymized=False,
            gdpr_consents=[],
        )

    @staticmethod
    def api_create_to_db_person(person_data: Dict[str, Any]) -> DBPerson:
        """
        Convert API PersonCreate data to database Person.

        Args:
            person_data: Dictionary with person creation data

        Returns:
            DBPerson object ready for database storage
        """
        from ...core.calendar import CalendarDate, CalendarType
        from ...core.event import Event
        from ...core.place import Place

        # Create birth event
        birth_event = None
        if person_data.get("birth_date") or person_data.get("birth_place"):
            birth_event = Event(place=Place(person_data.get("birth_place", "")))
            if person_data.get("birth_date"):
                try:
                    # Parse date string (YYYY-MM-DD)
                    date_str = person_data["birth_date"]
                    parts = date_str.split("-")
                    if len(parts) >= 1:
                        year = int(parts[0]) if parts[0] else 0
                        month = int(parts[1]) if len(parts) > 1 and parts[1] else 0
                        day = int(parts[2]) if len(parts) > 2 and parts[2] else 0
                        birth_event.calendar_date = CalendarDate(
                            year=year,
                            month=month,
                            day=day,
                            calendar_type=CalendarType.GREGORIAN,
                        )
                except (ValueError, AttributeError):
                    pass

        # Create death event
        death_event = None
        if person_data.get("death_date") or person_data.get("death_place"):
            death_event = Event(place=Place(person_data.get("death_place", "")))
            if person_data.get("death_date"):
                try:
                    date_str = person_data["death_date"]
                    parts = date_str.split("-")
                    if len(parts) >= 1:
                        year = int(parts[0]) if parts[0] else 0
                        month = int(parts[1]) if len(parts) > 1 and parts[1] else 0
                        day = int(parts[2]) if len(parts) > 2 and parts[2] else 0
                        death_event.calendar_date = CalendarDate(
                            year=year,
                            month=month,
                            day=day,
                            calendar_type=CalendarType.GREGORIAN,
                        )
                except (ValueError, AttributeError):
                    pass

        # Convert sex
        api_sex = person_data.get("sex", "unknown")
        if isinstance(api_sex, str):
            api_sex = PersonSex(api_sex)
        db_sex = PersonAdapter.api_sex_to_db_sex(api_sex)

        # Convert visibility to access
        visibility = person_data.get("visibility_level", VisibilityLevel.FAMILY)
        if isinstance(visibility, str):
            visibility = VisibilityLevel(visibility)
        access = PersonAdapter.visibility_to_db_access(visibility)

        # Create Person object
        person = DBPerson(
            first_name=person_data.get("first_name", ""),
            surname=person_data.get("last_name", ""),
            sex=db_sex,
            birth=birth_event,
            death=death_event,
            occupation=person_data.get("occupation", ""),
            notes=person_data.get("notes", ""),
            access=access,
        )

        return person
