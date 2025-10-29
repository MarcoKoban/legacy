"""Family service for business logic and database operations."""

from typing import Dict, List, Optional
from uuid import uuid4

import structlog

from ...core.event import Event
from ...core.family import DivorceInfo as CoreDivorceInfo
from ...core.family import DivorceStatus as CoreDivorceStatus
from ...core.family import Family as CoreFamily
from ...core.family import FamilyEvent as CoreFamilyEvent
from ...core.family import FamilyEventName as CoreFamilyEventName
from ...core.family import RelationKind as CoreRelationKind
from ...core.family import WitnessInfo as CoreWitnessInfo
from ...core.family import WitnessKind as CoreWitnessKind
from ...core.place import Place
from ...db.database import Database
from ..models.family import (
    DivorceStatus,
    FamilyCreate,
    FamilyEventCreate,
    FamilyEventName,
    FamilyResponse,
    FamilyUpdate,
    RelationKind,
    WitnessKind,
)

logger = structlog.get_logger(__name__)

# Temporary in-memory storage for families until Database class is extended
_FAMILIES_STORAGE: Dict[str, CoreFamily] = {}


class FamilyService:
    """Service for managing families in the database."""

    def __init__(self, db: Database):
        """Initialize family service with database connection."""
        self.db = db

    def _convert_relation_kind(self, relation: RelationKind) -> CoreRelationKind:
        """Convert API RelationKind to core RelationKind."""
        mapping = {
            RelationKind.MARRIED: CoreRelationKind.MARRIED,
            RelationKind.NOT_MARRIED: CoreRelationKind.NOT_MARRIED,
            RelationKind.ENGAGED: CoreRelationKind.ENGAGED,
            RelationKind.NO_MENTION: CoreRelationKind.NO_MENTION,
            RelationKind.MARRIAGE_BANN: CoreRelationKind.MARRIAGE_BANN,
            RelationKind.MARRIAGE_CONTRACT: CoreRelationKind.MARRIAGE_CONTRACT,
            RelationKind.MARRIAGE_LICENSE: CoreRelationKind.MARRIAGE_LICENSE,
            RelationKind.PACS: CoreRelationKind.PACS,
            RelationKind.RESIDENCE: CoreRelationKind.RESIDENCE,
        }
        return mapping[relation]

    def _convert_divorce_status(self, status: DivorceStatus) -> CoreDivorceStatus:
        """Convert API DivorceStatus to core DivorceStatus."""
        mapping = {
            DivorceStatus.NOT_DIVORCED: CoreDivorceStatus.NOT_DIVORCED,
            DivorceStatus.DIVORCED: CoreDivorceStatus.DIVORCED,
            DivorceStatus.SEPARATED: CoreDivorceStatus.SEPARATED,
        }
        return mapping[status]

    def _convert_event_name(self, event_name: FamilyEventName) -> CoreFamilyEventName:
        """Convert API FamilyEventName to core FamilyEventName."""
        mapping = {
            FamilyEventName.MARRIAGE: CoreFamilyEventName.MARRIAGE,
            FamilyEventName.NO_MARRIAGE: CoreFamilyEventName.NO_MARRIAGE,
            FamilyEventName.NO_MENTION: CoreFamilyEventName.NO_MENTION,
            FamilyEventName.ENGAGE: CoreFamilyEventName.ENGAGE,
            FamilyEventName.DIVORCE: CoreFamilyEventName.DIVORCE,
            FamilyEventName.SEPARATED: CoreFamilyEventName.SEPARATED,
            FamilyEventName.ANNULATION: CoreFamilyEventName.ANNULATION,
            FamilyEventName.MARRIAGE_BANN: CoreFamilyEventName.MARRIAGE_BANN,
            FamilyEventName.MARRIAGE_CONTRACT: CoreFamilyEventName.MARRIAGE_CONTRACT,
            FamilyEventName.MARRIAGE_LICENSE: CoreFamilyEventName.MARRIAGE_LICENSE,
            FamilyEventName.PACS: CoreFamilyEventName.PACS,
            FamilyEventName.RESIDENCE: CoreFamilyEventName.RESIDENCE,
            FamilyEventName.CUSTOM: CoreFamilyEventName.CUSTOM,
        }
        return mapping[event_name]

    def _convert_witness_kind(self, witness_kind: WitnessKind) -> CoreWitnessKind:
        """Convert API WitnessKind to core WitnessKind."""
        mapping = {
            WitnessKind.WITNESS: CoreWitnessKind.WITNESS,
            WitnessKind.WITNESS_GODPARENT: CoreWitnessKind.WITNESS_GODPARENT,
            WitnessKind.WITNESS_CIVILOFFICER: (CoreWitnessKind.WITNESS_CIVILOFFICER),
            WitnessKind.WITNESS_RELIGIOUSOFFICER: (
                CoreWitnessKind.WITNESS_RELIGIOUSOFFICER
            ),
            WitnessKind.WITNESS_INFORMANT: CoreWitnessKind.WITNESS_INFORMANT,
            WitnessKind.WITNESS_ATTENDING: CoreWitnessKind.WITNESS_ATTENDING,
            WitnessKind.WITNESS_MENTIONED: CoreWitnessKind.WITNESS_MENTIONED,
            WitnessKind.WITNESS_OTHER: CoreWitnessKind.WITNESS_OTHER,
        }
        return mapping[witness_kind]

    def _create_event_from_data(self, event_data: FamilyEventCreate) -> CoreFamilyEvent:
        """Create a core FamilyEvent from API data."""
        # Create base event
        base_event = Event(
            place=Place(event_data.place or ""),
            note=event_data.note or "",
            src=event_data.source or "",
        )

        # Set date if provided
        if event_data.date:
            try:
                # Parse date (assuming YYYY-MM-DD format)
                parts = event_data.date.split("-")
                if len(parts) == 3:
                    year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
                    base_event.set_date_from_components(year, month, day)
            except (ValueError, IndexError):
                logger.warning(f"Invalid date format: {event_data.date}")

        # Create witnesses
        witnesses = []
        for witness_data in event_data.witnesses:
            # Get person from database by index
            try:
                person_idx = int(witness_data.person_id)
                person = self.db.get_person(person_idx)
                if person:
                    witness_kind = self._convert_witness_kind(witness_data.witness_kind)
                    witnesses.append(CoreWitnessInfo(person, witness_kind))
            except (ValueError, AttributeError):
                logger.warning(f"Could not find person {witness_data.person_id}")

        # Create family event
        event_name = self._convert_event_name(event_data.event_name)
        return CoreFamilyEvent(
            event_name=event_name,
            custom_name=event_data.custom_name or "",
            event=base_event,
            reason=event_data.reason or "",
            witnesses=witnesses,
        )

    def create_family(self, family_data: FamilyCreate) -> FamilyResponse:
        """Create a new family in the database."""
        logger.info("Creating new family", relation=family_data.relation)

        # Get persons from database
        fathers = []
        for pid in family_data.father_ids:
            try:
                person = self.db.get_person(int(pid))
                if person:
                    fathers.append(person)
            except (ValueError, AttributeError):
                logger.warning(f"Father {pid} not found")

        mothers = []
        for pid in family_data.mother_ids:
            try:
                person = self.db.get_person(int(pid))
                if person:
                    mothers.append(person)
            except (ValueError, AttributeError):
                logger.warning(f"Mother {pid} not found")

        children = []
        for pid in family_data.children_ids:
            try:
                person = self.db.get_person(int(pid))
                if person:
                    children.append(person)
            except (ValueError, AttributeError):
                logger.warning(f"Child {pid} not found")

        # Convert relation kind
        relation = self._convert_relation_kind(family_data.relation)

        # Create divorce info if provided
        divorce_info = None
        if family_data.divorce_info:
            divorce_status = self._convert_divorce_status(
                family_data.divorce_info.divorce_status
            )
            divorce_event = Event()
            if family_data.divorce_info.divorce_date:
                try:
                    parts = family_data.divorce_info.divorce_date.split("-")
                    if len(parts) == 3:
                        year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
                        divorce_event.set_date_from_components(year, month, day)
                except (ValueError, IndexError):
                    logger.warning(
                        f"Invalid divorce date: {family_data.divorce_info.divorce_date}"
                    )

            divorce_info = CoreDivorceInfo(
                status=divorce_status,
                event=divorce_event,
            )

        # Create family events
        events = [self._create_event_from_data(e) for e in family_data.events]

        # Create marriage event if marriage date is provided
        if family_data.marriage_date:
            marriage_event = Event(
                place=Place(family_data.marriage_place or ""),
                src=family_data.marriage_source or "",
            )
            try:
                parts = family_data.marriage_date.split("-")
                if len(parts) == 3:
                    year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
                    marriage_event.set_date_from_components(year, month, day)
            except (ValueError, IndexError):
                logger.warning(f"Invalid marriage date: {family_data.marriage_date}")

            events.insert(
                0,
                CoreFamilyEvent(
                    event_name=CoreFamilyEventName.MARRIAGE, event=marriage_event
                ),
            )

        # Create core Family object
        core_family = CoreFamily(
            father=fathers if fathers else None,
            mother=mothers if mothers else None,
            children=children,
            relation=relation,
            divorce=divorce_info if divorce_info else CoreDivorceInfo(),
            events=events,
            comment=family_data.comment or "",
        )

        # Generate ID and store in memory
        family_id = str(uuid4())
        _FAMILIES_STORAGE[family_id] = core_family

        logger.info("Family created successfully", family_id=family_id)

        # Return response
        return self._family_to_response(family_id, core_family)

    def get_family(self, family_id: str) -> Optional[FamilyResponse]:
        """Get a family by ID."""
        family = _FAMILIES_STORAGE.get(family_id)
        if family is None:
            return None

        return self._family_to_response(family_id, family)

    def list_families(
        self, offset: int = 0, limit: int = 100
    ) -> Dict[str, List[FamilyResponse]]:
        """List all families with pagination."""
        # Get all families from storage
        all_families = list(_FAMILIES_STORAGE.items())

        # Apply pagination
        paginated = all_families[offset : offset + limit]  # noqa: E203

        families = [self._family_to_response(fid, fam) for fid, fam in paginated]

        return {"families": families, "total": len(_FAMILIES_STORAGE)}

    def update_family(
        self, family_id: str, update_data: FamilyUpdate
    ) -> Optional[FamilyResponse]:
        """Update a family."""
        family = _FAMILIES_STORAGE.get(family_id)
        if family is None:
            return None

        # Update fields if provided
        if update_data.relation is not None:
            family.relation = self._convert_relation_kind(update_data.relation)

        if update_data.divorce_info is not None:
            divorce_status = self._convert_divorce_status(
                update_data.divorce_info.divorce_status
            )
            divorce_event = Event()
            if update_data.divorce_info.divorce_date:
                try:
                    parts = update_data.divorce_info.divorce_date.split("-")
                    if len(parts) == 3:
                        year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
                        divorce_event.set_date_from_components(year, month, day)
                except (ValueError, IndexError):
                    logger.warning(
                        f"Invalid divorce date: {update_data.divorce_info.divorce_date}"
                    )

            family.divorce = CoreDivorceInfo(
                status=divorce_status,
                event=divorce_event,
            )

        if update_data.comment is not None:
            family.comment = update_data.comment

        if update_data.events is not None:
            family.events = [
                self._create_event_from_data(e) for e in update_data.events
            ]

        # Update parents and children
        if update_data.father_ids is not None:
            fathers = []
            for pid in update_data.father_ids:
                try:
                    person = self.db.get_person(int(pid))
                    if person:
                        fathers.append(person)
                except (ValueError, AttributeError):
                    pass
            family.father = fathers if fathers else None

        if update_data.mother_ids is not None:
            mothers = []
            for pid in update_data.mother_ids:
                try:
                    person = self.db.get_person(int(pid))
                    if person:
                        mothers.append(person)
                except (ValueError, AttributeError):
                    pass
            family.mother = mothers if mothers else None

        if update_data.children_ids is not None:
            children = []
            for pid in update_data.children_ids:
                try:
                    person = self.db.get_person(int(pid))
                    if person:
                        children.append(person)
                except (ValueError, AttributeError):
                    pass
            family.children = children

        return self._family_to_response(family_id, family)

    def delete_family(self, family_id: str) -> bool:
        """Delete a family."""
        if family_id in _FAMILIES_STORAGE:
            del _FAMILIES_STORAGE[family_id]
            return True
        return False

    def _family_to_response(self, family_id: str, family: CoreFamily) -> FamilyResponse:
        """Convert core Family to API FamilyResponse."""
        # Extract person IDs
        father_ids = [str(f.id) for f in (family.father or [])]
        mother_ids = [str(m.id) for m in (family.mother or [])]
        children_ids = [str(c.id) for c in family.children]

        # Convert events
        events = []
        for event in family.events:
            event_dict = {
                "event_name": event.event_name.value,
                "custom_name": event.custom_name if event.custom_name else None,
                "date": event.event.date if event.event else None,
                "place": (
                    event.event.place.name
                    if event.event and event.event.place
                    else None
                ),
                "note": event.event.note if event.event else None,
                "source": event.event.src if event.event else None,
                "reason": event.reason if event.reason else None,
                "witnesses": [
                    {
                        "person_id": str(w.person.index),
                        "witness_kind": w.witness_kind.value,
                    }
                    for w in event.witnesses
                ],
            }
            events.append(event_dict)

        # Get marriage info from events if available
        marriage_date = None
        marriage_place = None
        marriage_source = None
        for event in family.events:
            if event.event_name == CoreFamilyEventName.MARRIAGE and event.event:
                marriage_date = event.event.date
                marriage_place = event.event.place.name if event.event.place else None
                marriage_source = event.event.src
                break

        # Create divorce info
        divorce_info = None
        if family.divorce and family.divorce.status != CoreDivorceStatus.NOT_DIVORCED:
            divorce_info = {
                "divorce_status": family.divorce.status.value,
                "divorce_date": (
                    family.divorce.event.date if family.divorce.event else None
                ),
            }

        return FamilyResponse(
            id=family_id,
            relation=family.relation.value,
            divorce_info=divorce_info,
            marriage_date=marriage_date,
            marriage_place=marriage_place,
            marriage_source=marriage_source,
            comment=family.comment,
            father_ids=father_ids,
            mother_ids=mother_ids,
            children_ids=children_ids,
            events=events,
        )
