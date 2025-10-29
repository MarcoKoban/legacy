"""
Person data model for genealogical records.

This module implements the Person class and related data structures
to represent individuals in genealogical databases, ensuring compatibility
with the OCaml Geneweb implementation.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from geneweb.core.event import Event
from geneweb.core.sosa import Sosa

if TYPE_CHECKING:
    from geneweb.core.family import Family


class Sex(Enum):
    """Person's biological sex."""

    MALE = "male"
    FEMALE = "female"
    NEUTER = "neuter"


class Access(Enum):
    """Access rights for personal data."""

    PUBLIC = "public"
    PRIVATE = "private"
    SEMI_PUBLIC = "semi_public"
    IF_TITLES = "if_titles"


class Death(Enum):
    """Death status of a person."""

    NOT_DEAD = "not_dead"
    DEAD_YOUNG = "dead_young"
    DEAD_DONT_KNOW_WHEN = "dead_dont_know_when"
    DONT_KNOW_IF_DEAD = "dont_know_if_dead"
    OF_COURSE_DEAD = "of_course_dead"


class Burial(Enum):
    """Burial information."""

    UNKNOWN_BURIAL = "unknown_burial"
    BURIED = "buried"
    CREMATED = "cremated"

    FRENCH = "french"
    HEBREW = "hebrew"


@dataclass(eq=True)
class DeathInfo:
    """
    Death-specific information combining status and event details.

    Attributes:
        status: Death status (alive, dead, unknown, etc.)
        event: Event details for the death (date, place, etc.)
    """

    status: Death = Death.NOT_DEAD
    event: Event = field(default_factory=Event)

    def __bool__(self) -> bool:
        """Return True if death information is meaningful."""
        return self.status != Death.NOT_DEAD or bool(self.event)

    def __str__(self) -> str:
        """Return string representation for display."""
        if self.status == Death.NOT_DEAD and not self.event:
            return "Alive"

        parts = [self.status.value.replace("_", " ").title()]
        if self.event:
            parts.append(str(self.event))
        return " - ".join(parts)


@dataclass(eq=True)
class BurialInfo:
    """
    Burial-specific information combining type and event details.

    Attributes:
        burial_type: Type of burial (buried, cremated, unknown)
        event: Event details for the burial (date, place, etc.)
    """

    burial_type: Burial = Burial.UNKNOWN_BURIAL
    event: Event = field(default_factory=Event)

    def __bool__(self) -> bool:
        """Return True if burial information is meaningful."""
        return self.burial_type != Burial.UNKNOWN_BURIAL or bool(self.event)

    def __str__(self) -> str:
        """Return string representation for display."""
        if self.burial_type == Burial.UNKNOWN_BURIAL and not self.event:
            return "Unknown burial"

        parts = [self.burial_type.value.replace("_", " ").title()]
        if self.event:
            parts.append(str(self.event))
        return " - ".join(parts)


@dataclass(eq=True)
class Person:
    """
    Person data model for genealogical records.

    This class represents an individual in a genealogical database,
    with attributes matching the OCaml Geneweb implementation.

    Attributes:
        first_name: Person's first name (required)
        surname: Person's surname/family name (required)
        occ: Occurrence number for distinguishing homonyms
        sex: Biological sex (required)
        access: Access rights for this person's data
        public_name: Public display name (if different from first_name)
        image: Path/URL to person's image
        occupation: Person's profession or occupation
        birth: Birth information
        baptism: Baptism information
        death: Death status
        burial: Burial type
        notes: General notes about the person
        sources: General sources for person information
        sosa: Sosa genealogical number (optional)
    """

    # Required fields
    first_name: str
    surname: str
    sex: Sex

    # Optional fields with defaults
    occ: int = 0
    access: Access = Access.PUBLIC
    public_name: str = ""
    image: str = ""
    occupation: str = ""

    # Birth information
    birth: Event = field(default_factory=Event)

    # Baptism information
    baptism: Event = field(default_factory=Event)

    # Death information
    death: DeathInfo = field(default_factory=DeathInfo)

    # Burial information
    burial: BurialInfo = field(default_factory=BurialInfo)

    # General information
    notes: str = ""
    sources: str = ""

    # Genealogical information
    sosa: Optional[Sosa] = None
    sosa_list: List[Sosa] = field(
        default_factory=list
    )  # Support for multiple Sosa numbers (implexes)

    # Bidirectional relationships with families
    families_as_parent: List["Family"] = field(default_factory=list)
    families_as_child: List["Family"] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate person data after initialization."""
        if not self.first_name.strip():
            raise ValueError("First name cannot be empty")

        if not self.surname.strip():
            raise ValueError("Surname cannot be empty")

        if self.occ < 0:
            raise ValueError(f"Occurrence must be non-negative, got {self.occ}")

    def __str__(self) -> str:
        """Return string representation for display."""
        if self.occ > 0:
            return f"{self.first_name} {self.surname} ({self.occ})"
        return f"{self.first_name} {self.surname}"

    def __repr__(self) -> str:
        """Return string representation for debugging."""
        return (
            f"Person(first_name='{self.first_name}', "
            f"surname='{self.surname}', occ={self.occ}, sex={self.sex.name})"
        )

    def __hash__(self) -> int:
        """Return hash value for use in sets and dictionaries."""
        return hash((self.first_name, self.surname, self.occ))

    def __eq__(self, other: object) -> bool:
        """Test equality with another Person."""
        if not isinstance(other, Person):
            return False
        return (
            self.first_name == other.first_name
            and self.surname == other.surname
            and self.occ == other.occ
        )

    def full_name(self) -> str:
        """Return the full name for display."""
        if self.public_name:
            return self.public_name
        return self.__str__()

    def is_alive(self) -> bool:
        """Return True if the person is considered alive."""
        return self.death.status == Death.NOT_DEAD

    def is_dead(self) -> bool:
        """Return True if the person is confirmed dead."""
        return self.death.status in [
            Death.DEAD_YOUNG,
            Death.DEAD_DONT_KNOW_WHEN,
            Death.OF_COURSE_DEAD,
        ]

    def death_status_unknown(self) -> bool:
        """Return True if death status is unknown."""
        return self.death.status == Death.DONT_KNOW_IF_DEAD

    def has_birth_info(self) -> bool:
        """Return True if birth information is available."""
        return bool(self.birth)

    def has_death_info(self) -> bool:
        """Return True if death information is available."""
        return bool(self.death)

    def has_burial_info(self) -> bool:
        """Return True if burial information is available."""
        return bool(self.burial)

    def birth_year(self) -> Optional[str]:
        """Extract birth year from birth date if available."""
        if self.birth and self.birth.calendar_date and self.birth.calendar_date.year:
            # Return year from CalendarDate
            return str(self.birth.calendar_date.year)
        return None

    def death_year(self) -> Optional[str]:
        """Extract death year from death date if available."""
        if (
            self.death
            and self.death.event
            and self.death.event.calendar_date
            and self.death.event.calendar_date.year
        ):
            # Return year from CalendarDate
            return str(self.death.event.calendar_date.year)
        return None

    def lifespan(self) -> str:
        """Return a formatted lifespan string (birth year - death year)."""
        birth_yr = self.birth_year()
        death_yr = self.death_year()

        if birth_yr and death_yr:
            return f"{birth_yr} - {death_yr}"
        elif birth_yr and self.is_dead():
            return f"{birth_yr} - ?"
        elif birth_yr:
            return f"{birth_yr} - "
        elif death_yr:
            return f"? - {death_yr}"
        else:
            return ""

    # Family relationship management methods

    def add_family_as_parent(self, family: "Family") -> None:
        """Add a family where this person is a parent."""
        if family not in self.families_as_parent:
            self.families_as_parent.append(family)

    def remove_family_as_parent(self, family: "Family") -> None:
        """Remove a family where this person is a parent."""
        if family in self.families_as_parent:
            self.families_as_parent.remove(family)

    def add_family_as_child(self, family: "Family") -> None:
        """Add a family where this person is a child."""
        if family not in self.families_as_child:
            self.families_as_child.append(family)

    def remove_family_as_child(self, family: "Family") -> None:
        """Remove a family where this person is a child."""
        if family in self.families_as_child:
            self.families_as_child.remove(family)

    def get_all_families(self) -> List["Family"]:
        """Return all families this person belongs to (as parent or child)."""
        return self.families_as_parent + self.families_as_child

    def get_spouses(self) -> List["Person"]:
        """Return all spouses (persons with whom this person has families)."""
        spouses = []
        for family in self.families_as_parent:
            if family.has_father() and family.has_mother():
                # Check if this person is father or mother
                if family.father and self in family.father:
                    if family.mother:
                        spouses.extend(
                            [spouse for spouse in family.mother if spouse != self]
                        )
                elif family.mother and self in family.mother:
                    if family.father:
                        spouses.extend(
                            [spouse for spouse in family.father if spouse != self]
                        )
        return list(set(spouses))  # Remove duplicates

    def get_children(self) -> List["Person"]:
        """Return all children from all families where this person is a parent."""
        children = []
        for family in self.families_as_parent:
            children.extend(family.children)
        return list(set(children))  # Remove duplicates

    def get_parents(self) -> List["Person"]:
        """Return all parents from families where this person is a child."""
        parents = []
        for family in self.families_as_child:
            if family.father:
                parents.extend(family.father)
            if family.mother:
                parents.extend(family.mother)
        return list(set(parents))  # Remove duplicates

    def has_multiple_marriages(self) -> bool:
        """Return True if this person has multiple marriage families."""
        return len(self.families_as_parent) > 1

    # Sosa number management methods

    def add_sosa(self, sosa: Sosa) -> None:
        """Add a Sosa number to this person."""
        if sosa not in self.sosa_list:
            self.sosa_list.append(sosa)
        # Keep the primary sosa as the smallest non-zero value
        if self.sosa is None or (sosa.value > 0 and sosa.value < self.sosa.value):
            self.sosa = sosa

    def add_sosa_and_propagate(self, sosa: Sosa) -> None:
        """Add a Sosa number and propagate to parents."""
        self.add_sosa(sosa)
        self.propagate_sosa_to_parents()

    def has_sosa(self, sosa: Sosa) -> bool:
        """Check if this person has a specific Sosa number."""
        return sosa in self.sosa_list or self.sosa == sosa

    def has_any_sosa(self) -> bool:
        """Check if this person has any Sosa number."""
        return len(self.sosa_list) > 0 or (
            self.sosa is not None and self.sosa.value > 0
        )

    def get_all_sosa_numbers(self) -> List[Sosa]:
        """Get all Sosa numbers for this person."""
        all_sosa = list(self.sosa_list)
        if self.sosa is not None and self.sosa not in all_sosa:
            all_sosa.append(self.sosa)
        return sorted(all_sosa, key=lambda s: s.value)

    def get_primary_sosa(self) -> Optional[Sosa]:
        """Get the primary (smallest non-zero) Sosa number."""
        return self.sosa

    def calculate_parent_sosa_numbers(self) -> tuple[List[Sosa], List[Sosa]]:
        """
        Calculate what Sosa numbers this person's parents should have.

        Returns:
            Tuple of (father_sosa_list, mother_sosa_list)
        """
        father_sosa_numbers = []
        mother_sosa_numbers = []

        for sosa in self.get_all_sosa_numbers():
            if sosa.value > 0:  # Skip Sosa 0
                father_sosa_numbers.append(sosa.father_sosa())
                mother_sosa_numbers.append(sosa.mother_sosa())

        return father_sosa_numbers, mother_sosa_numbers

    def calculate_child_sosa_numbers(self) -> List[Sosa]:
        """
        Calculate what Sosa numbers this person's children should have
        based on this person's Sosa.

        Returns:
            List of possible child Sosa numbers
        """
        child_sosa_numbers = []

        for sosa in self.get_all_sosa_numbers():
            if sosa.value >= 2:  # Only parents (Sosa >= 2) can have children
                try:
                    child_sosa = sosa.child_sosa()
                    if child_sosa not in child_sosa_numbers:
                        child_sosa_numbers.append(child_sosa)
                except ValueError:
                    # Skip invalid parent Sosa numbers
                    continue

        return child_sosa_numbers

    def propagate_sosa_to_parents(self) -> None:
        """
        Propagate Sosa numbers to parents based on this person's Sosa numbers.
        """
        father_sosa_list, mother_sosa_list = self.calculate_parent_sosa_numbers()

        for family in self.families_as_child:
            # Propagate to fathers
            if family.father:
                for father in family.father:
                    for sosa in father_sosa_list:
                        if not father.has_sosa(sosa):  # Only add if not already present
                            father.add_sosa(sosa)
                            # Recursively propagate to grandparents
                            father.propagate_sosa_to_parents()

            # Propagate to mothers
            if family.mother:
                for mother in family.mother:
                    for sosa in mother_sosa_list:
                        if not mother.has_sosa(sosa):  # Only add if not already present
                            mother.add_sosa(sosa)
                            # Recursively propagate to grandparents
                            mother.propagate_sosa_to_parents()

    def propagate_sosa_to_children(self) -> None:
        """
        Propagate Sosa numbers to children based on this person's Sosa numbers.
        """
        child_sosa_list = self.calculate_child_sosa_numbers()

        for family in self.families_as_parent:
            for child in family.children:
                for sosa in child_sosa_list:
                    child.add_sosa(sosa)
