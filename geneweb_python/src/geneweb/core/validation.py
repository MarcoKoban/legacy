"""
Validation system for genealogical relationship consistency.

This module provides validation tools to ensure data integrity
and prevent logical inconsistencies in family relationships.
"""

import re
from typing import TYPE_CHECKING, Optional, Set

if TYPE_CHECKING:
    from geneweb.core.family import Family
    from geneweb.core.person import Person


class ValidationError(Exception):
    """Raised when relationship validation fails."""

    pass


class RelationshipValidator:
    """Validates genealogical relationships for consistency."""

    @staticmethod
    def validate_no_self_parenting(person: "Person", parent: "Person") -> None:
        """
        Validate that a person cannot be their own parent.

        Args:
            person: The child person
            parent: The proposed parent

        Raises:
            ValidationError: If person and parent are the same
        """
        if person == parent:
            raise ValidationError(
                f"Person {person.first_name} {person.surname} "
                f"cannot be their own parent"
            )

    @staticmethod
    def validate_no_circular_ancestry(
        person: "Person", proposed_ancestor: "Person"
    ) -> None:
        """
        Validate that adding a parent doesn't create circular ancestry.

        Args:
            person: The person getting a new parent
            proposed_ancestor: The proposed parent/ancestor

        Raises:
            ValidationError: If circular ancestry would be created
        """
        # Check if proposed_ancestor is already a descendant of person
        if RelationshipValidator._is_descendant_of(proposed_ancestor, person):
            raise ValidationError(
                f"Cannot make {proposed_ancestor.first_name} "
                f"{proposed_ancestor.surname} a parent of "
                f"{person.first_name} {person.surname}: "
                f"would create circular ancestry"
            )

    @staticmethod
    def validate_birth_death_order(person: "Person") -> None:
        """
        Validate that birth date comes before death date.

        Args:
            person: Person to validate

        Raises:
            ValidationError: If death date is before birth date
        """
        birth_year_str = person.birth_year()
        death_year_str = person.death_year()

        # Convert string years to integers if available
        birth_year = None
        death_year = None

        if birth_year_str:
            try:
                birth_year = int(birth_year_str)
            except (ValueError, TypeError):
                pass

        if death_year_str:
            try:
                death_year = int(death_year_str)
            except (ValueError, TypeError):
                pass

        if birth_year and death_year and death_year < birth_year:
            raise ValidationError(
                f"Person {person.first_name} {person.surname} "
                f"cannot die ({death_year}) before being born ({birth_year})"
            )

    @staticmethod
    def validate_parent_child_age_gap(parent: "Person", child: "Person") -> None:
        """
        Validate reasonable age gap between parent and child.

        Args:
            parent: The parent person
            child: The child person

        Raises:
            ValidationError: If age gap is unreasonable
        """
        parent_birth_str = parent.birth_year()
        child_birth_str = child.birth_year()

        # Convert to integers if available
        parent_birth = None
        child_birth = None

        if parent_birth_str:
            try:
                parent_birth = int(parent_birth_str)
            except (ValueError, TypeError):
                pass

        if child_birth_str:
            try:
                child_birth = int(child_birth_str)
            except (ValueError, TypeError):
                pass

        if parent_birth and child_birth:
            age_gap = child_birth - parent_birth

            # Parent should be at least 10 years older and no more than 80 years older
            if age_gap < 10:
                raise ValidationError(
                    f"Parent {parent.first_name} {parent.surname} "
                    f"(born {parent_birth}) too young to be parent of "
                    f"{child.first_name} {child.surname} (born {child_birth}). "
                    f"Age gap: {age_gap} years"
                )

            if age_gap > 80:
                raise ValidationError(
                    f"Parent {parent.first_name} {parent.surname} "
                    f"(born {parent_birth}) too old to be parent of "
                    f"{child.first_name} {child.surname} (born {child_birth}). "
                    f"Age gap: {age_gap} years"
                )

    @staticmethod
    def validate_family_consistency(family: "Family") -> None:
        """
        Validate overall family consistency.

        Args:
            family: Family to validate

        Raises:
            ValidationError: If family has consistency issues
        """
        # Validate that children are not older than parents
        for child in family.children:
            if family.father:
                for father in family.father:
                    RelationshipValidator.validate_parent_child_age_gap(father, child)
                    RelationshipValidator.validate_no_self_parenting(child, father)
            if family.mother:
                for mother in family.mother:
                    RelationshipValidator.validate_parent_child_age_gap(mother, child)
                    RelationshipValidator.validate_no_self_parenting(child, mother)

            # Validate birth/death order for each person
            RelationshipValidator.validate_birth_death_order(child)

        # Validate parents
        if family.father:
            for father in family.father:
                RelationshipValidator.validate_birth_death_order(father)
        if family.mother:
            for mother in family.mother:
                RelationshipValidator.validate_birth_death_order(mother)

    @staticmethod
    def validate_no_duplicate_children(family: "Family", child: "Person") -> None:
        """
        Validate that a child is not already in the family.

        Args:
            family: The family
            child: The child to add

        Raises:
            ValidationError: If child is already in family
        """
        if child in family.children:
            raise ValidationError(
                f"Child {child.first_name} {child.surname} is already in this family"
            )

    @staticmethod
    def validate_marriage_dates(family: "Family") -> None:
        """
        Validate that marriage dates make sense with birth/death dates.

        Args:
            family: Family to validate

        Raises:
            ValidationError: If marriage dates are inconsistent
        """
        # Get marriage date from family events
        from geneweb.core.family import FamilyEventName

        marriage_events = family.get_events_by_type(FamilyEventName.MARRIAGE)
        if not marriage_events:
            return

        marriage_event = marriage_events[0]
        marriage_date_str = marriage_event.event.date if marriage_event.event else None

        if not marriage_date_str:
            return

        # Extract year from marriage date
        marriage_year = RelationshipValidator._extract_year_from_date(marriage_date_str)
        if not marriage_year:
            return

        # Check that spouses were alive during marriage
        if family.father:
            father_birth_str = family.father[0].birth_year() if family.father else None
            father_death_str = family.father[0].death_year() if family.father else None

            father_birth = None
            father_death = None

            if father_birth_str:
                try:
                    father_birth = int(father_birth_str)
                except (ValueError, TypeError):
                    pass

            if father_death_str:
                try:
                    father_death = int(father_death_str)
                except (ValueError, TypeError):
                    pass

            if father_birth and marriage_year < father_birth:
                raise ValidationError(
                    f"Father {family.father[0].first_name} "
                    f"{family.father[0].surname} cannot marry in {marriage_year} "
                    f"before being born in {father_birth}"
                )

            if father_death and marriage_year > father_death:
                raise ValidationError(
                    f"Father {family.father[0].first_name} {family.father[0].surname} "
                    f"cannot marry in {marriage_year} after dying in {father_death}"
                )

        if family.mother:
            mother_birth_str = family.mother[0].birth_year() if family.mother else None
            mother_death_str = family.mother[0].death_year() if family.mother else None

            mother_birth = None
            mother_death = None

            if mother_birth_str:
                try:
                    mother_birth = int(mother_birth_str)
                except (ValueError, TypeError):
                    pass

            if mother_death_str:
                try:
                    mother_death = int(mother_death_str)
                except (ValueError, TypeError):
                    pass

            if mother_birth and marriage_year < mother_birth:
                raise ValidationError(
                    f"Mother {family.mother[0].first_name} "
                    f"{family.mother[0].surname} cannot marry in {marriage_year} "
                    f"before being born in {mother_birth}"
                )

            if mother_death and marriage_year > mother_death:
                raise ValidationError(
                    f"Mother {family.mother[0].first_name} {family.mother[0].surname} "
                    f"cannot marry in {marriage_year} after dying in {mother_death}"
                )

    @staticmethod
    def _is_descendant_of(
        person: "Person", ancestor: "Person", visited: Optional[Set["Person"]] = None
    ) -> bool:
        """
        Check if person is a descendant of ancestor (recursive with cycle detection).

        Args:
            person: Person to check
            ancestor: Potential ancestor
            visited: Set of already visited persons (cycle detection)

        Returns:
            True if person is descendant of ancestor
        """
        if visited is None:
            visited = set()

        if person in visited:
            return False  # Cycle detected

        if person == ancestor:
            return True

        visited.add(person)

        # Check all parents
        for parent in person.get_parents():
            if RelationshipValidator._is_descendant_of(
                parent, ancestor, visited.copy()
            ):
                return True

        return False

    @staticmethod
    def _extract_year_from_date(date_str: str) -> Optional[int]:
        """
        Extract year from date string.

        Args:
            date_str: Date string in various formats

        Returns:
            Year as integer or None if not found
        """
        # Try to find a 4-digit year
        year_match = re.search(r"\b(1\d{3}|20\d{2})\b", date_str)
        if year_match:
            return int(year_match.group(1))
        return None
