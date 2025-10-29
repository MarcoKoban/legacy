"""
Tests for genealogical relationship validation system.

This module tests the validation tools that ensure data integrity
and prevent logical inconsistencies in family relationships.
"""

from datetime import datetime

import pytest

from geneweb.core.event import Event
from geneweb.core.family import Family, FamilyEvent, FamilyEventName
from geneweb.core.person import Death, DeathInfo, Person, Sex
from geneweb.core.validation import RelationshipValidator, ValidationError


class TestRelationshipValidation:
    """Test relationship validation functionality."""

    def test_validate_no_self_parenting_valid(self):
        """Test that different persons can be parent-child."""
        parent = Person("John", "Doe", sex=Sex.MALE)
        child = Person("Jane", "Doe", sex=Sex.FEMALE)

        # Should not raise any exception
        RelationshipValidator.validate_no_self_parenting(child, parent)

    def test_validate_no_self_parenting_invalid(self):
        """Test that a person cannot be their own parent."""
        person = Person("John", "Doe", sex=Sex.MALE)

        with pytest.raises(ValidationError, match="cannot be their own parent"):
            RelationshipValidator.validate_no_self_parenting(person, person)

    def test_validate_no_circular_ancestry_valid(self):
        """Test that normal ancestry relationships are allowed."""
        grandparent = Person("Grand", "Parent", sex=Sex.MALE)
        parent = Person("Parent", "Person", sex=Sex.MALE)
        child = Person("Child", "Person", sex=Sex.FEMALE)

        # Create normal family structure
        family1 = Family()
        family1.add_father(grandparent, validate=False)
        family1.add_child(parent, validate=False)

        family2 = Family()
        family2.add_father(parent, validate=False)
        family2.add_child(child, validate=False)

        # Should not raise any exception for normal relationships
        RelationshipValidator.validate_no_circular_ancestry(child, grandparent)

    def test_validate_no_circular_ancestry_invalid(self):
        """Test that circular ancestry is prevented."""
        grandparent = Person("Grand", "Parent", sex=Sex.MALE)
        parent = Person("Parent", "Person", sex=Sex.MALE)
        child = Person("Child", "Person", sex=Sex.FEMALE)

        # Create family structure
        family1 = Family()
        family1.add_father(grandparent, validate=False)
        family1.add_child(parent, validate=False)

        family2 = Family()
        family2.add_father(parent, validate=False)
        family2.add_child(child, validate=False)

        # Try to make child a parent of grandparent (circular)
        with pytest.raises(ValidationError, match="would create circular ancestry"):
            RelationshipValidator.validate_no_circular_ancestry(grandparent, child)

    def test_validate_birth_death_order_valid(self):
        """Test that normal birth-death order is valid."""
        birth_event = Event.from_datetime(datetime(1990, 1, 1), place="Hospital")
        death_event = Event.from_datetime(datetime(2020, 12, 31), place="Home")

        person = Person(
            "John",
            "Doe",
            sex=Sex.MALE,
            birth=birth_event,
            death=DeathInfo(status=Death.OF_COURSE_DEAD, event=death_event),
        )

        # Should not raise any exception
        RelationshipValidator.validate_birth_death_order(person)

    def test_validate_birth_death_order_invalid(self):
        """Test that death before birth is invalid."""
        birth_event = Event.from_datetime(datetime(1990, 1, 1), place="Hospital")
        death_event = Event.from_datetime(
            datetime(1985, 12, 31), place="Home"
        )  # Before birth

        person = Person(
            "John",
            "Doe",
            sex=Sex.MALE,
            birth=birth_event,
            death=DeathInfo(status=Death.OF_COURSE_DEAD, event=death_event),
        )

        with pytest.raises(ValidationError, match="cannot die.*before being born"):
            RelationshipValidator.validate_birth_death_order(person)

    def test_validate_parent_child_age_gap_valid(self):
        """Test that reasonable age gaps are accepted."""
        parent_birth = Event.from_datetime(datetime(1970, 1, 1))
        child_birth = Event.from_datetime(datetime(1995, 1, 1))  # 25 year gap

        parent = Person("Parent", "Person", sex=Sex.MALE, birth=parent_birth)
        child = Person("Child", "Person", sex=Sex.FEMALE, birth=child_birth)

        # Should not raise any exception
        RelationshipValidator.validate_parent_child_age_gap(parent, child)

    def test_validate_parent_child_age_gap_too_young(self):
        """Test that unreasonably small age gaps are rejected."""
        parent_birth = Event.from_datetime(datetime(1990, 1, 1))
        child_birth = Event.from_datetime(datetime(1995, 1, 1))  # Only 5 year gap

        parent = Person("Parent", "Person", sex=Sex.MALE, birth=parent_birth)
        child = Person("Child", "Person", sex=Sex.FEMALE, birth=child_birth)

        with pytest.raises(ValidationError, match="too young to be parent"):
            RelationshipValidator.validate_parent_child_age_gap(parent, child)

    def test_validate_parent_child_age_gap_too_old(self):
        """Test that unreasonably large age gaps are rejected."""
        parent_birth = Event.from_datetime(datetime(1900, 1, 1))
        child_birth = Event.from_datetime(datetime(1990, 1, 1))  # 90 year gap

        parent = Person("Parent", "Person", sex=Sex.MALE, birth=parent_birth)
        child = Person("Child", "Person", sex=Sex.FEMALE, birth=child_birth)

        with pytest.raises(ValidationError, match="too old to be parent"):
            RelationshipValidator.validate_parent_child_age_gap(parent, child)

    def test_validate_no_duplicate_children(self):
        """Test that duplicate children are prevented."""
        family = Family()
        child = Person("Child", "Person", sex=Sex.FEMALE)

        family.add_child(child, validate=False)  # Add first time

        with pytest.raises(ValidationError, match="already in this family"):
            RelationshipValidator.validate_no_duplicate_children(family, child)

    def test_validate_marriage_dates_valid(self):
        """Test that valid marriage dates are accepted."""
        father_birth = Event.from_datetime(datetime(1970, 1, 1))
        mother_birth = Event.from_datetime(datetime(1975, 1, 1))
        marriage_event = FamilyEvent(
            event_name=FamilyEventName.MARRIAGE,
            event=Event.from_datetime(datetime(1995, 6, 15)),  # Both adults
        )

        father = Person("Father", "Person", sex=Sex.MALE, birth=father_birth)
        mother = Person("Mother", "Person", sex=Sex.FEMALE, birth=mother_birth)

        family = Family(father=[father], mother=[mother], events=[marriage_event])

        # Should not raise any exception
        RelationshipValidator.validate_marriage_dates(family)

    def test_validate_marriage_dates_before_birth(self):
        """Test that marriage before birth is invalid."""
        father_birth = Event.from_datetime(datetime(1970, 1, 1))
        marriage_event = FamilyEvent(
            event_name=FamilyEventName.MARRIAGE,
            event=Event.from_datetime(datetime(1965, 6, 15)),  # Before father's birth
        )

        father = Person("Father", "Person", sex=Sex.MALE, birth=father_birth)

        family = Family(father=[father], events=[marriage_event])

        with pytest.raises(ValidationError, match="cannot marry.*before being born"):
            RelationshipValidator.validate_marriage_dates(family)

    def test_validate_marriage_dates_after_death(self):
        """Test that marriage after death is invalid."""
        father_birth = Event.from_datetime(datetime(1970, 1, 1))
        father_death = Event.from_datetime(datetime(1990, 1, 1))
        marriage_event = FamilyEvent(
            event_name=FamilyEventName.MARRIAGE,
            event=Event.from_datetime(datetime(1995, 6, 15)),  # After father's death
        )

        father = Person(
            "Father",
            "Person",
            sex=Sex.MALE,
            birth=father_birth,
            death=DeathInfo(status=Death.OF_COURSE_DEAD, event=father_death),
        )

        family = Family(father=[father], events=[marriage_event])

        with pytest.raises(ValidationError, match="cannot marry.*after dying"):
            RelationshipValidator.validate_marriage_dates(family)


class TestFamilyValidationIntegration:
    """Test validation integration in Family methods."""

    def test_add_child_with_validation_success(self):
        """Test successful child addition with validation."""
        parent_birth = Event.from_date_string("1970-01-01")
        child_birth = Event.from_date_string("1995-01-01")

        parent = Person("Parent", "Person", sex=Sex.MALE, birth=parent_birth)
        child = Person("Child", "Person", sex=Sex.FEMALE, birth=child_birth)

        family = Family()
        family.add_father(parent, validate=False)
        family.add_child(child, validate=True)  # Should succeed

        assert child in family.children
        assert family in child.families_as_child

    def test_add_child_with_validation_failure(self):
        """Test child addition failure due to validation."""
        child = Person("Child", "Person", sex=Sex.FEMALE)

        family = Family()
        family.add_child(child, validate=False)  # Add first time

        # Try to add same child again with validation
        with pytest.raises(ValidationError):
            family.add_child(child, validate=True)

    def test_add_father_with_validation_success(self):
        """Test successful father addition with validation."""
        parent_birth = Event.from_date_string("1970-01-01")
        child_birth = Event.from_date_string("1995-01-01")

        parent = Person("Parent", "Person", sex=Sex.MALE, birth=parent_birth)
        child = Person("Child", "Person", sex=Sex.FEMALE, birth=child_birth)

        family = Family()
        family.add_child(child, validate=False)
        family.add_father(parent, validate=True)  # Should succeed

        assert parent in family.father
        assert family in parent.families_as_parent

    def test_add_father_with_validation_failure(self):
        """Test father addition failure due to validation."""
        parent_birth = Event.from_datetime(datetime(1995, 1, 1))  # Same year as child
        child_birth = Event.from_datetime(datetime(1995, 1, 1))

        parent = Person("Parent", "Person", sex=Sex.MALE, birth=parent_birth)
        child = Person("Child", "Person", sex=Sex.FEMALE, birth=child_birth)

        family = Family()
        family.add_child(child, validate=False)

        # Try to add parent with invalid age gap
        with pytest.raises(ValidationError):
            family.add_father(parent, validate=True)

    def test_add_mother_with_validation_success(self):
        """Test successful mother addition with validation."""
        parent_birth = Event.from_datetime(datetime(1970, 1, 1))
        child_birth = Event.from_datetime(datetime(1995, 1, 1))

        parent = Person("Parent", "Person", sex=Sex.FEMALE, birth=parent_birth)
        child = Person("Child", "Person", sex=Sex.FEMALE, birth=child_birth)

        family = Family()
        family.add_child(child, validate=False)
        family.add_mother(parent, validate=True)  # Should succeed

        assert parent in family.mother
        assert family in parent.families_as_parent

    def test_add_mother_with_validation_failure(self):
        """Test mother addition failure due to validation."""
        person = Person("Person", "Person", sex=Sex.FEMALE)

        family = Family()
        family.add_child(person, validate=False)

        # Try to make person their own parent
        with pytest.raises(ValidationError):
            family.add_mother(person, validate=True)

    def test_validation_can_be_disabled(self):
        """Test that validation can be bypassed when needed."""
        person = Person("Person", "Person", sex=Sex.FEMALE)

        family = Family()
        family.add_child(person, validate=False)

        # This should work even though it's invalid, because validation is disabled
        family.add_mother(person, validate=False)

        assert person in family.mother
        assert person in family.children

    def test_family_validate_method(self):
        """Test the family validation method."""
        parent_birth = Event.from_date_string("1970-01-01")
        child_birth = Event.from_date_string("1995-01-01")

        parent = Person("Parent", "Person", sex=Sex.MALE, birth=parent_birth)
        child = Person("Child", "Person", sex=Sex.FEMALE, birth=child_birth)

        family = Family()
        family.add_father(parent, validate=False)
        family.add_child(child, validate=False)

        # Should validate successfully
        family.validate_family()

    def test_family_validate_method_failure(self):
        """Test family validation method with invalid data."""
        parent_birth = Event.from_datetime(datetime(1995, 1, 1))  # Too young
        child_birth = Event.from_datetime(datetime(1996, 1, 1))

        parent = Person("Parent", "Person", sex=Sex.MALE, birth=parent_birth)
        child = Person("Child", "Person", sex=Sex.FEMALE, birth=child_birth)

        family = Family()
        family.add_father(parent, validate=False)
        family.add_child(child, validate=False)

        # Should fail validation
        with pytest.raises(ValidationError):
            family.validate_family()


class TestValidationEdgeCases:
    """Test edge cases and complex validation scenarios."""

    def test_complex_circular_ancestry(self):
        """Test detection of complex circular ancestry patterns."""
        # Create: A -> B -> C, then try C -> A (3-generation cycle)
        person_a = Person("A", "Person", sex=Sex.MALE)
        person_b = Person("B", "Person", sex=Sex.MALE)
        person_c = Person("C", "Person", sex=Sex.FEMALE)

        # A is parent of B
        family1 = Family()
        family1.add_father(person_a, validate=False)
        family1.add_child(person_b, validate=False)

        # B is parent of C
        family2 = Family()
        family2.add_father(person_b, validate=False)
        family2.add_child(person_c, validate=False)

        # Try to make C parent of A (would create cycle)
        with pytest.raises(ValidationError, match="would create circular ancestry"):
            RelationshipValidator.validate_no_circular_ancestry(person_a, person_c)

    def test_validation_with_missing_dates(self):
        """Test that validation handles missing birth/death dates gracefully."""
        parent = Person("Parent", "Person", sex=Sex.MALE)  # No birth date
        child = Person("Child", "Person", sex=Sex.FEMALE)  # No birth date

        family = Family()

        # Should not raise exceptions when dates are missing
        family.add_father(parent, validate=True)
        family.add_child(child, validate=True)

        assert parent in family.father
        assert child in family.children

    def test_extract_year_from_various_date_formats(self):
        """Test year extraction from various date formats."""
        validator = RelationshipValidator()

        # Test various date formats
        assert validator._extract_year_from_date("1990-01-01") == 1990
        assert validator._extract_year_from_date("01/01/1990") == 1990
        assert validator._extract_year_from_date("January 1, 1990") == 1990
        assert validator._extract_year_from_date("1990") == 1990
        assert validator._extract_year_from_date("circa 1990") == 1990
        assert validator._extract_year_from_date("no date") is None
        assert validator._extract_year_from_date("") is None

    def test_birth_death_validation_with_invalid_date_formats(self):
        """Test birth/death validation with invalid date formats."""
        # Test with invalid birth year format
        person = Person("John", "Doe", sex=Sex.MALE)
        birth_event = Event(place="Hospital")
        birth_event.set_date_from_string("invalid_date")
        person._birth = birth_event

        death_event = Event(place="Home")
        death_event.set_date_from_string("2020")
        person._death = DeathInfo(status=Death.OF_COURSE_DEAD, event=death_event)

        # Should not raise exception with invalid birth date format
        RelationshipValidator.validate_birth_death_order(person)

        # Test with invalid death year format
        birth_event2 = Event(place="Hospital")
        birth_event2.set_date_from_string("1990")
        person._birth = birth_event2

        death_event2 = Event(place="Home")
        death_event2.set_date_from_string("invalid_date")
        person._death = DeathInfo(status=Death.OF_COURSE_DEAD, event=death_event2)

        # Should not raise exception with invalid death date format
        RelationshipValidator.validate_birth_death_order(person)

    def test_parent_child_age_gap_with_invalid_dates(self):
        """Test parent-child age gap validation with invalid date formats."""
        # Test with invalid parent birth date
        parent = Person("Parent", "Person", sex=Sex.MALE)
        parent_birth = Event(place="Hospital")
        parent_birth.set_date_from_string("invalid_date")
        parent._birth = parent_birth

        child = Person("Child", "Person", sex=Sex.FEMALE)
        child_birth = Event(place="Hospital")
        child_birth.set_date_from_string("1995")
        child._birth = child_birth

        # Should not raise exception with invalid parent date
        RelationshipValidator.validate_parent_child_age_gap(parent, child)

        # Test with invalid child birth date
        parent_birth2 = Event(place="Hospital")
        parent_birth2.set_date_from_string("1970")
        parent._birth = parent_birth2

        child_birth2 = Event(place="Hospital")
        child_birth2.set_date_from_string("invalid_date")
        child._birth = child_birth2

        # Should not raise exception with invalid child date
        RelationshipValidator.validate_parent_child_age_gap(parent, child)

    def test_marriage_validation_with_mother_before_birth(self):
        """Test marriage validation when mother marries before birth."""
        mother_birth = Event.from_datetime(datetime(1975, 1, 1))
        marriage_event = FamilyEvent(
            event_name=FamilyEventName.MARRIAGE,
            event=Event.from_datetime(datetime(1970, 6, 15)),  # Before mother's birth
        )

        mother = Person("Mother", "Person", sex=Sex.FEMALE, birth=mother_birth)
        family = Family(mother=[mother], events=[marriage_event])

        with pytest.raises(ValidationError, match="cannot marry.*before being born"):
            RelationshipValidator.validate_marriage_dates(family)

    def test_marriage_validation_with_mother_after_death(self):
        """Test marriage validation when mother marries after death."""
        mother_birth = Event.from_datetime(datetime(1970, 1, 1))
        mother_death = Event.from_datetime(datetime(1990, 1, 1))
        marriage_event = FamilyEvent(
            event_name=FamilyEventName.MARRIAGE,
            event=Event.from_datetime(datetime(1995, 6, 15)),  # After mother's death
        )

        mother = Person(
            "Mother",
            "Person",
            sex=Sex.FEMALE,
            birth=mother_birth,
            death=DeathInfo(status=Death.OF_COURSE_DEAD, event=mother_death),
        )

        family = Family(mother=[mother], events=[marriage_event])

        with pytest.raises(ValidationError, match="cannot marry.*after dying"):
            RelationshipValidator.validate_marriage_dates(family)

    def test_marriage_validation_with_invalid_date_formats(self):
        """Test marriage validation with invalid date formats in parent dates."""
        # Test with invalid mother birth date format
        mother = Person("Mother", "Person", sex=Sex.FEMALE)
        mother_birth = Event(place="Hospital")
        mother_birth.set_date_from_string("invalid_date")
        mother._birth = mother_birth

        marriage_event = FamilyEvent(
            event_name=FamilyEventName.MARRIAGE,
            event=Event.from_datetime(datetime(1995, 6, 15)),
        )

        family = Family(mother=[mother], events=[marriage_event])

        # Should not raise exception with invalid date format
        RelationshipValidator.validate_marriage_dates(family)

    def test_descendant_check_with_cycle_detection(self):
        """Test descendant checking with cycle detection."""
        person_a = Person("A", "Person", sex=Sex.MALE)
        person_b = Person("B", "Person", sex=Sex.MALE)
        person_c = Person("C", "Person", sex=Sex.FEMALE)

        # Create families to establish parent-child relationships
        family1 = Family()
        family1.add_father(person_a, validate=False)
        family1.add_child(person_b, validate=False)

        family2 = Family()
        family2.add_father(person_b, validate=False)
        family2.add_child(person_c, validate=False)

        # Test normal descendant relationship
        assert RelationshipValidator._is_descendant_of(person_b, person_a) is True
        assert RelationshipValidator._is_descendant_of(person_c, person_a) is True
        assert RelationshipValidator._is_descendant_of(person_a, person_c) is False

    def test_marriage_validation_no_events(self):
        """Test marriage validation when family has no marriage events."""
        father = Person("Father", "Person", sex=Sex.MALE)
        mother = Person("Mother", "Person", sex=Sex.FEMALE)

        family = Family(father=[father], mother=[mother])  # No events

        # Should not raise exception when no marriage events exist
        RelationshipValidator.validate_marriage_dates(family)

    def test_marriage_validation_no_date_in_event(self):
        """Test marriage validation when marriage event has no date."""
        father = Person("Father", "Person", sex=Sex.MALE)
        marriage_event = FamilyEvent(
            event_name=FamilyEventName.MARRIAGE, event=None  # No event data
        )

        family = Family(father=[father], events=[marriage_event])

        # Should not raise exception when event has no date
        RelationshipValidator.validate_marriage_dates(family)

    def test_year_extraction_edge_cases(self):
        """Test year extraction with various edge cases."""
        validator = RelationshipValidator()

        # Test with 2-digit years (should not match)
        assert validator._extract_year_from_date("90-01-01") is None

        # Test with years outside valid range
        assert validator._extract_year_from_date("0990") is None  # Too old
        assert validator._extract_year_from_date("3000") is None  # Too future

        # Test with multiple years (should get first valid one)
        assert validator._extract_year_from_date("Born 1990, moved 1995") == 1990

        # Test 21st century years
        assert validator._extract_year_from_date("2010-01-01") == 2010
        assert validator._extract_year_from_date("2099") == 2099
