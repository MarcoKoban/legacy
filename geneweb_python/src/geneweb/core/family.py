"""
Family data model for genealogical records.

This module implements the Family class and related data structures
to represent family relationships in genealogical databases, ensuring compatibility
with the OCaml Geneweb implementation while providing improved design patterns.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from geneweb.core.event import Event

if TYPE_CHECKING:
    from geneweb.core.person import Person


class RelationKind(Enum):
    """Type of family relationship."""

    MARRIED = "married"
    NOT_MARRIED = "not_married"
    ENGAGED = "engaged"
    NO_SEXES_CHECK_NOT_MARRIED = "no_sexes_check_not_married"
    NO_MENTION = "no_mention"
    NO_SEXES_CHECK_MARRIED = "no_sexes_check_married"
    MARRIAGE_BANN = "marriage_bann"
    MARRIAGE_CONTRACT = "marriage_contract"
    MARRIAGE_LICENSE = "marriage_license"
    PACS = "pacs"
    RESIDENCE = "residence"


class DivorceStatus(Enum):
    """Divorce status of a family."""

    NOT_DIVORCED = "not_divorced"
    DIVORCED = "divorced"
    SEPARATED_OLD = "separated_old"
    NOT_SEPARATED = "not_separated"
    SEPARATED = "separated"


class WitnessKind(Enum):
    """Type of witness in family events."""

    WITNESS = "witness"
    WITNESS_GODPARENT = "witness_godparent"
    WITNESS_CIVIL_OFFICER = "witness_civil_officer"
    WITNESS_RELIGIOUS_OFFICER = "witness_religious_officer"
    WITNESS_INFORMANT = "witness_informant"
    WITNESS_ATTENDING = "witness_attending"
    WITNESS_MENTIONED = "witness_mentioned"
    WITNESS_OTHER = "witness_other"


class FamilyEventName(Enum):
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


@dataclass(frozen=True, eq=True)
class DivorceInfo:
    """
    Divorce information with optional date and details.

    Attributes:
        status: Divorce status
        event: Event details for the divorce (date, place, etc.)
    """

    status: DivorceStatus = DivorceStatus.NOT_DIVORCED
    event: Event = field(default_factory=Event)

    def __bool__(self) -> bool:
        """Return True if divorce information is meaningful."""
        return self.status != DivorceStatus.NOT_DIVORCED or bool(self.event)

    def __str__(self) -> str:
        """Return string representation for display."""
        if self.status == DivorceStatus.NOT_DIVORCED and not self.event:
            return "Not divorced"

        parts = [self.status.value.replace("_", " ").title()]
        if self.event:
            parts.append(str(self.event))
        return " - ".join(parts)


@dataclass(frozen=True, eq=True)
class WitnessInfo:
    """
    Witness information for family events.

    Attributes:
        person: The witness person object
        witness_type: Type of witness role
    """

    person: "Person"
    witness_type: WitnessKind = WitnessKind.WITNESS

    def __str__(self) -> str:
        """Return string representation for display."""
        name = f"{self.person.first_name} {self.person.surname}"
        if self.person.occ > 0:
            name += f" ({self.person.occ})"
        return f"{name} ({self.witness_type.value.replace('_', ' ').title()})"


@dataclass(frozen=True, eq=True)
class FamilyEvent:
    """
    Family-specific event information.

    This class represents family events like marriage, divorce, engagement, etc.
    with associated metadata and witnesses.

    Attributes:
        event_name: Type of family event
        event: Basic event information (date, place, note, src)
        reason: Reason for the event (e.g., divorce reason)
        witnesses: List of witnesses for this event
        custom_name: Custom event name if event_name is CUSTOM
    """

    event_name: FamilyEventName
    event: Event = field(default_factory=Event)
    reason: str = ""
    witnesses: List[WitnessInfo] = field(default_factory=list)
    custom_name: str = ""

    def __bool__(self) -> bool:
        """Return True if family event has meaningful data."""
        return bool(self.event) or bool(self.reason) or bool(self.witnesses)

    def __str__(self) -> str:
        """Return string representation for display."""
        name = (
            self.custom_name
            if self.event_name == FamilyEventName.CUSTOM
            else self.event_name.value.replace("_", " ").title()
        )

        parts = [name]
        if self.event:
            parts.append(str(self.event))
        if self.reason:
            parts.append(f"Reason: {self.reason}")
        if self.witnesses:
            witness_list = ", ".join(str(w) for w in self.witnesses[:3])
            if len(self.witnesses) > 3:
                witness_list += f" and {len(self.witnesses) - 3} more"
            parts.append(f"Witnesses: {witness_list}")

        return " - ".join(parts)


@dataclass(eq=True)
class Family:
    """
    Family data model for genealogical records.

    This class represents a family unit (typically a couple and their children)
    with improved design patterns compared to the OCaml implementation.

    Attributes:
        father: The father Person object (optional)
        mother: The mother Person object (optional)
        children: List of children Person objects
        marriage: Marriage event information
        relation: Type of relationship between partners
        divorce: Divorce information
        events: List of family events (marriage, divorce, etc.)
        witnesses: List of witnesses for the family formation
        comment: General comments about the family
        sources: Sources documenting this family
        origin_file: Original file where family was defined
        family_id: Unique identifier for this family (optional)
    """

    # Core family structure
    father: Optional[List["Person"]] = None
    mother: Optional[List["Person"]] = None
    children: List["Person"] = field(default_factory=list)

    # Relationship information
    marriage: Event = field(default_factory=Event)
    relation: RelationKind = RelationKind.MARRIED
    divorce: DivorceInfo = field(default_factory=DivorceInfo)

    # Extended event information
    events: List[FamilyEvent] = field(default_factory=list)
    witnesses: List[WitnessInfo] = field(default_factory=list)

    # Metadata
    comment: str = ""
    sources: str = ""
    origin_file: str = ""

    # Technical identifier
    family_id: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate family data after initialization."""
        # Note: We allow empty families to be created and populated later

        # Validate that children are unique
        if len(self.children) != len(set(self.children)):
            raise ValueError("Children must be unique")

    def __str__(self) -> str:
        """Return string representation for display."""
        parts = []

        if self.father and self.mother:
            father_name = f"{self.father[0].first_name} {self.father[0].surname}"
            mother_name = f"{self.mother[0].first_name} {self.mother[0].surname}"
            parts.append(f"{father_name} & {mother_name}")
        elif self.father:
            father_name = f"{self.father[0].first_name} {self.father[0].surname}"
            parts.append(f"{father_name} (single parent)")
        elif self.mother:
            mother_name = f"{self.mother[0].first_name} {self.mother[0].surname}"
            parts.append(f"{mother_name} (single parent)")

        if self.children:
            parts.append(f"{len(self.children)} children")

        return " - ".join(parts) if parts else "Empty family"

    def __hash__(self) -> int:
        """Return hash value for use in sets and dictionaries."""
        father_tuple = tuple(self.father) if self.father else None
        mother_tuple = tuple(self.mother) if self.mother else None
        return hash((father_tuple, mother_tuple, tuple(self.children)))

    def has_father(self) -> bool:
        """Return True if family has a father."""
        return self.father is not None and len(self.father) > 0

    def has_mother(self) -> bool:
        """Return True if family has a mother."""
        return self.mother is not None and len(self.mother) > 0

    def has_children(self) -> bool:
        """Return True if family has children."""
        return len(self.children) > 0

    def children_count(self) -> int:
        """Return the number of children in this family."""
        return len(self.children)

    def is_single_parent(self) -> bool:
        """Return True if this is a single-parent family."""
        has_father = self.has_father()
        has_mother = self.has_mother()
        return has_father != has_mother

    def is_married(self) -> bool:
        """Return True if the couple is married."""
        return self.relation in [
            RelationKind.MARRIED,
            RelationKind.NO_SEXES_CHECK_MARRIED,
        ]

    def is_divorced(self) -> bool:
        """Return True if the couple is divorced."""
        return self.divorce.status in [
            DivorceStatus.DIVORCED,
            DivorceStatus.SEPARATED,
            DivorceStatus.SEPARATED_OLD,
        ]

    def has_marriage_info(self) -> bool:
        """Return True if marriage information is available."""
        return bool(self.marriage)

    def has_divorce_info(self) -> bool:
        """Return True if divorce information is available."""
        return bool(self.divorce)

    def get_events_by_type(self, event_type: FamilyEventName) -> List[FamilyEvent]:
        """Return all events of a specific type."""
        return [event for event in self.events if event.event_name == event_type]

    def get_marriage_events(self) -> List[FamilyEvent]:
        """Return all marriage-related events."""
        marriage_types = [
            FamilyEventName.MARRIAGE,
            FamilyEventName.MARRIAGE_BANN,
            FamilyEventName.MARRIAGE_CONTRACT,
            FamilyEventName.MARRIAGE_LICENSE,
            FamilyEventName.PACS,
        ]
        return [event for event in self.events if event.event_name in marriage_types]

    def get_divorce_events(self) -> List[FamilyEvent]:
        """Return all divorce-related events."""
        divorce_types = [
            FamilyEventName.DIVORCE,
            FamilyEventName.SEPARATED,
            FamilyEventName.ANNULATION,
        ]
        return [event for event in self.events if event.event_name in divorce_types]

    def add_child(self, child: "Person", validate: bool = True) -> None:
        """Add a child to this family and maintain bidirectional relationship."""
        # Perform validations if requested
        if validate:
            from geneweb.core.validation import RelationshipValidator

            RelationshipValidator.validate_no_duplicate_children(self, child)

        # If validation is disabled, allow silent skip for duplicates
        if not validate and child in self.children:
            return

            # Validate parent-child relationships
            if self.father:
                for father in self.father:
                    RelationshipValidator.validate_no_self_parenting(child, father)
                    RelationshipValidator.validate_no_circular_ancestry(child, father)
                    RelationshipValidator.validate_parent_child_age_gap(father, child)

            if self.mother:
                for mother in self.mother:
                    RelationshipValidator.validate_no_self_parenting(child, mother)
                    RelationshipValidator.validate_no_circular_ancestry(child, mother)
                    RelationshipValidator.validate_parent_child_age_gap(mother, child)

            # Validate birth/death order
            RelationshipValidator.validate_birth_death_order(child)

        self.children.append(child)
        # Maintain bidirectional relationship
        child.add_family_as_child(self)
        # Propagate Sosa numbers from parents to child
        self._propagate_sosa_to_child(child)

    def remove_child(self, child: "Person") -> None:
        """Remove a child from this family and maintain bidirectional relationship."""
        if child not in self.children:
            return
        self.children.remove(child)
        # Maintain bidirectional relationship
        child.remove_family_as_child(self)

    def add_father(self, father: "Person", validate: bool = True) -> None:
        """Add a father to this family and maintain bidirectional relationship."""
        if self.father is None:
            self.father = []
        if father in self.father:
            return

        # Perform validations if requested
        if validate:
            from geneweb.core.validation import RelationshipValidator

            # Validate father relationships with children
            for child in self.children:
                RelationshipValidator.validate_no_self_parenting(child, father)
                RelationshipValidator.validate_no_circular_ancestry(child, father)
                RelationshipValidator.validate_parent_child_age_gap(father, child)

            # Validate birth/death order
            RelationshipValidator.validate_birth_death_order(father)

        self.father.append(father)
        # Maintain bidirectional relationship
        father.add_family_as_parent(self)
        # Propagate Sosa numbers from children to father
        self._propagate_sosa_from_children_to_parent(father, is_father=True)

    def add_mother(self, mother: "Person", validate: bool = True) -> None:
        """Add a mother to this family and maintain bidirectional relationship."""
        if self.mother is None:
            self.mother = []
        if mother in self.mother:
            return

        # Perform validations if requested
        if validate:
            from geneweb.core.validation import RelationshipValidator

            # Validate mother relationships with children
            for child in self.children:
                RelationshipValidator.validate_no_self_parenting(child, mother)
                RelationshipValidator.validate_no_circular_ancestry(child, mother)
                RelationshipValidator.validate_parent_child_age_gap(mother, child)

            # Validate birth/death order
            RelationshipValidator.validate_birth_death_order(mother)

        self.mother.append(mother)
        # Maintain bidirectional relationship
        mother.add_family_as_parent(self)
        # Propagate Sosa numbers from children to mother
        self._propagate_sosa_from_children_to_parent(mother, is_father=False)

    def remove_father(self, father: "Person") -> None:
        """Remove a father from this family and maintain bidirectional relationship."""
        if self.father is None or father not in self.father:
            return
        self.father.remove(father)
        # Maintain bidirectional relationship
        father.remove_family_as_parent(self)
        # Clean up empty list
        if not self.father:
            self.father = None

    def remove_mother(self, mother: "Person") -> None:
        """Remove a mother from this family and maintain bidirectional relationship."""
        if self.mother is None or mother not in self.mother:
            return
        self.mother.remove(mother)
        # Maintain bidirectional relationship
        mother.remove_family_as_parent(self)
        # Clean up empty list
        if not self.mother:
            self.mother = None

    def validate_family(self) -> None:
        """Validate the entire family for consistency."""
        from geneweb.core.validation import RelationshipValidator

        RelationshipValidator.validate_family_consistency(self)
        RelationshipValidator.validate_marriage_dates(self)

    def get_all_parents(self) -> List["Person"]:
        """Return all parents (fathers and mothers) in this family."""
        parents = []
        if self.father:
            parents.extend(self.father)
        if self.mother:
            parents.extend(self.mother)
        return parents

    def get_all_members(self) -> List["Person"]:
        """Return all family members (parents and children)."""
        members = self.get_all_parents()
        members.extend(self.children)
        return members

    def is_member(self, person: "Person") -> bool:
        """Check if a person is a member of this family."""
        return person in self.get_all_members()

    def is_parent(self, person: "Person") -> bool:
        """Check if a person is a parent in this family."""
        return person in self.get_all_parents()

    def is_child(self, person: "Person") -> bool:
        """Check if a person is a child in this family."""
        return person in self.children

    # Private methods for Sosa propagation

    def _propagate_sosa_to_child(self, child: "Person") -> None:
        """Propagate Sosa numbers from parents to a specific child."""
        # Get all parent Sosa numbers
        parent_sosa_numbers = []

        if self.father:
            for father in self.father:
                parent_sosa_numbers.extend(father.get_all_sosa_numbers())

        if self.mother:
            for mother in self.mother:
                parent_sosa_numbers.extend(mother.get_all_sosa_numbers())

        # Calculate child Sosa numbers from parent Sosa numbers
        for parent_sosa in parent_sosa_numbers:
            if parent_sosa.value >= 2:  # Only parent Sosa numbers can have children
                try:
                    child_sosa = parent_sosa.child_sosa()
                    child.add_sosa(child_sosa)
                except ValueError:
                    continue

    def _propagate_sosa_from_children_to_parent(
        self, parent: "Person", is_father: bool
    ) -> None:
        """Propagate Sosa numbers from children to a parent."""
        for child in self.children:
            child_sosa_numbers = child.get_all_sosa_numbers()
            for child_sosa in child_sosa_numbers:
                if child_sosa.value > 0:  # Skip Sosa 0
                    if is_father:
                        parent_sosa = child_sosa.father_sosa()
                    else:
                        parent_sosa = child_sosa.mother_sosa()
                    parent.add_sosa(parent_sosa)
