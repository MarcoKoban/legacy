"""
Unit tests for the Family data model.

This module tests the Family class and related data structures
using comprehensive test cases to ensure proper functionality.
"""

import pytest

from geneweb.core.event import Event
from geneweb.core.family import (
    DivorceInfo,
    DivorceStatus,
    Family,
    FamilyEvent,
    FamilyEventName,
    RelationKind,
    WitnessInfo,
    WitnessKind,
)
from geneweb.core.person import Person, Sex
from geneweb.core.place import Place


@pytest.fixture
def john_doe():
    """Create a sample Person: John Doe."""
    return Person(first_name="John", surname="Doe", sex=Sex.MALE, occ=0)


@pytest.fixture
def jane_smith():
    """Create a sample Person: Jane Smith."""
    return Person(first_name="Jane", surname="Smith", sex=Sex.FEMALE, occ=0)


@pytest.fixture
def bob_johnson():
    """Create a sample Person: Bob Johnson."""
    return Person(first_name="Bob", surname="Johnson", sex=Sex.MALE, occ=0)


@pytest.fixture
def alice_brown():
    """Create a sample Person: Alice Brown."""
    return Person(first_name="Alice", surname="Brown", sex=Sex.FEMALE, occ=0)


class TestFamilyEventName:
    """Test FamilyEventName enum."""

    def test_family_event_name_values(self):
        """Test that all family event names have correct values."""
        assert FamilyEventName.MARRIAGE.value == "marriage"
        assert FamilyEventName.DIVORCE.value == "divorce"
        assert FamilyEventName.PACS.value == "pacs"
        assert FamilyEventName.CUSTOM.value == "custom"


class TestRelationKind:
    """Test RelationKind enum."""

    def test_relation_kind_values(self):
        """Test that all relation kinds have correct values."""
        assert RelationKind.MARRIED.value == "married"
        assert RelationKind.NOT_MARRIED.value == "not_married"
        assert RelationKind.ENGAGED.value == "engaged"
        assert RelationKind.PACS.value == "pacs"


class TestDivorceStatus:
    """Test DivorceStatus enum."""

    def test_divorce_status_values(self):
        """Test that all divorce statuses have correct values."""
        assert DivorceStatus.NOT_DIVORCED.value == "not_divorced"
        assert DivorceStatus.DIVORCED.value == "divorced"
        assert DivorceStatus.SEPARATED.value == "separated"


class TestWitnessKind:
    """Test WitnessKind enum."""

    def test_witness_kind_values(self):
        """Test that all witness kinds have correct values."""
        assert WitnessKind.WITNESS.value == "witness"
        assert WitnessKind.WITNESS_GODPARENT.value == "witness_godparent"
        assert WitnessKind.WITNESS_CIVIL_OFFICER.value == "witness_civil_officer"


class TestDivorceInfo:
    """Test DivorceInfo class."""

    def test_divorce_info_not_divorced(self):
        """Test DivorceInfo with default values."""
        divorce_info = DivorceInfo()
        assert divorce_info.status == DivorceStatus.NOT_DIVORCED
        assert not bool(divorce_info)
        assert str(divorce_info) == "Not divorced"

    def test_divorce_info_divorced(self):
        """Test DivorceInfo with divorce status."""
        event = Event(place=Place("Paris"))
        event.set_date_from_components(1995, 6, 15)
        divorce_info = DivorceInfo(status=DivorceStatus.DIVORCED, event=event)
        assert divorce_info.status == DivorceStatus.DIVORCED
        assert bool(divorce_info)
        assert "Divorced" in str(divorce_info)
        assert "Paris" in str(divorce_info)

    def test_divorce_info_separated(self):
        """Test DivorceInfo with separated status."""
        divorce_info = DivorceInfo(status=DivorceStatus.SEPARATED)
        assert divorce_info.status == DivorceStatus.SEPARATED
        assert bool(divorce_info)
        assert str(divorce_info) == "Separated"


class TestWitnessInfo:
    """Test WitnessInfo class."""

    def test_witness_info_basic(self, john_doe):
        """Test WitnessInfo with basic witness."""
        witness = WitnessInfo(person=john_doe, witness_type=WitnessKind.WITNESS)
        assert witness.person == john_doe
        assert witness.witness_type == WitnessKind.WITNESS
        assert str(witness) == "John Doe (Witness)"

    def test_witness_info_with_occurrence(self):
        """Test WitnessInfo with occurrence number."""
        person = Person(first_name="John", surname="Smith", sex=Sex.MALE, occ=2)
        witness = WitnessInfo(person=person, witness_type=WitnessKind.WITNESS_GODPARENT)
        assert str(witness) == "John Smith (2) (Witness Godparent)"

    def test_witness_info_civil_officer(self):
        """Test WitnessInfo with civil officer role."""
        person = Person(first_name="Marie", surname="Martin", sex=Sex.FEMALE, occ=0)
        witness = WitnessInfo(
            person=person, witness_type=WitnessKind.WITNESS_CIVIL_OFFICER
        )
        assert str(witness) == "Marie Martin (Witness Civil Officer)"


class TestFamilyEvent:
    """Test FamilyEvent class."""

    def test_family_event_empty(self):
        """Test FamilyEvent with minimal data."""
        event = FamilyEvent(event_name=FamilyEventName.MARRIAGE)
        assert event.event_name == FamilyEventName.MARRIAGE
        assert not bool(event)  # Empty event
        assert str(event) == "Marriage"

    def test_family_event_with_data(self):
        """Test FamilyEvent with full data."""
        base_event = Event(
            place=Place("Church of St. Mary"),
            note="Beautiful ceremony",
        )
        base_event.set_date_from_components(1990, 6, 15)
        alice = Person(first_name="Alice", surname="Johnson", sex=Sex.FEMALE, occ=0)
        bob = Person(first_name="Bob", surname="Wilson", sex=Sex.MALE, occ=0)
        witnesses = [
            WitnessInfo(alice, WitnessKind.WITNESS),
            WitnessInfo(bob, WitnessKind.WITNESS),
        ]
        family_event = FamilyEvent(
            event_name=FamilyEventName.MARRIAGE,
            event=base_event,
            reason="Religious ceremony",
            witnesses=witnesses,
        )

        assert bool(family_event)
        assert "Marriage" in str(family_event)
        assert "Church of St. Mary" in str(family_event)
        assert "Reason: Religious ceremony" in str(family_event)
        assert "Alice Johnson" in str(family_event)

    def test_family_event_custom(self):
        """Test FamilyEvent with custom event name."""
        event = FamilyEvent(
            event_name=FamilyEventName.CUSTOM, custom_name="Engagement Party"
        )
        assert str(event) == "Engagement Party"

    def test_family_event_many_witnesses(self):
        """Test FamilyEvent with many witnesses (truncation)."""
        witnesses = [
            WitnessInfo(
                Person(first_name="Person", surname=f"Number{i}", sex=Sex.MALE, occ=0),
                WitnessKind.WITNESS,
            )
            for i in range(5)
        ]
        event = FamilyEvent(event_name=FamilyEventName.MARRIAGE, witnesses=witnesses)
        str_repr = str(event)
        assert "and 2 more" in str_repr


class TestFamily:
    """Test Family class."""

    def test_family_minimal(self, john_doe):
        """Test Family with minimal data."""
        family = Family(father=[john_doe])
        assert john_doe in family.father
        assert family.mother is None
        assert len(family.children) == 0
        assert family.relation == RelationKind.MARRIED
        assert str(family) == "John Doe (single parent)"

    def test_family_complete(self, john_doe, jane_smith):
        """Test Family with complete data."""
        marriage_event = Event(place=Place("City Hall"), note="Civil ceremony")
        marriage_event.set_date_from_components(1990, 6, 15)
        alice = Person(first_name="Alice", surname="Doe", sex=Sex.FEMALE, occ=0)
        bob = Person(first_name="Bob", surname="Doe", sex=Sex.MALE, occ=0)
        family = Family(
            father=[john_doe],
            mother=[jane_smith],
            children=[alice, bob],
            marriage=marriage_event,
            relation=RelationKind.MARRIED,
            comment="Happy family",
        )

        assert family.has_father()
        assert family.has_mother()
        assert family.has_children()
        assert family.children_count() == 2
        assert not family.is_single_parent()
        assert family.is_married()
        assert not family.is_divorced()
        assert family.has_marriage_info()
        assert str(family) == "John Doe & Jane Smith - 2 children"

    def test_family_single_mother(self, jane_smith):
        """Test Family with single mother."""
        alice = Person(first_name="Alice", surname="Smith", sex=Sex.FEMALE, occ=0)
        family = Family(mother=[jane_smith], children=[alice])
        assert not family.has_father()
        assert family.has_mother()
        assert family.is_single_parent()
        assert str(family) == "Jane Smith (single parent) - 1 children"

    def test_family_creation_empty(self):
        """Test that empty Family can be created and populated later."""
        family = Family()
        assert family.father is None
        assert family.mother is None
        assert len(family.children) == 0
        assert str(family) == "Empty family"

    def test_family_validation_duplicate_children(self, john_doe):
        """Test Family validation with duplicate children."""
        alice = Person(first_name="Alice", surname="Doe", sex=Sex.FEMALE, occ=0)
        with pytest.raises(ValueError, match="Children must be unique"):
            Family(father=[john_doe], children=[alice, alice])

    def test_family_parents_as_lists(self, john_doe, jane_smith):
        """Test Family with parents as lists."""
        family = Family(father=[john_doe], mother=[jane_smith])
        assert john_doe in family.father
        assert jane_smith in family.mother

    def test_family_hash(self, john_doe, jane_smith):
        """Test Family hash method."""
        alice = Person(first_name="Alice", surname="Doe", sex=Sex.FEMALE, occ=0)
        bob = Person(first_name="Bob", surname="Doe", sex=Sex.MALE, occ=0)

        family1 = Family(father=[john_doe], mother=[jane_smith], children=[alice])
        family2 = Family(father=[john_doe], mother=[jane_smith], children=[alice])
        family3 = Family(father=[john_doe], mother=[jane_smith], children=[bob])

        assert hash(family1) == hash(family2)
        assert hash(family1) != hash(family3)

    def test_family_divorced(self):
        """Test Family with divorce information."""
        divorce_event = Event(place=Place("Court"))
        divorce_event.set_date_from_components(2000, 3, 10)
        divorce_info = DivorceInfo(status=DivorceStatus.DIVORCED, event=divorce_event)
        family = Family(
            father=[Person(first_name="John", surname="Doe", sex=Sex.MALE, occ=0)],
            mother=[Person(first_name="Jane", surname="Smith", sex=Sex.FEMALE, occ=0)],
            divorce=divorce_info,
        )

        assert family.is_divorced()
        assert family.has_divorce_info()

    def test_family_not_married(self):
        """Test Family with not married relation."""
        family = Family(
            father=[Person(first_name="John", surname="Doe", sex=Sex.MALE, occ=0)],
            mother=[Person(first_name="Jane", surname="Smith", sex=Sex.FEMALE, occ=0)],
            relation=RelationKind.NOT_MARRIED,
        )
        assert not family.is_married()

    def test_family_events(self):
        """Test Family with events."""
        marriage_event_obj = Event()
        marriage_event_obj.set_date_from_components(1990, 6, 15)
        marriage_event = FamilyEvent(
            event_name=FamilyEventName.MARRIAGE, event=marriage_event_obj
        )
        divorce_event_obj = Event()
        divorce_event_obj.set_date_from_components(2000, 3, 10)
        divorce_event = FamilyEvent(
            event_name=FamilyEventName.DIVORCE, event=divorce_event_obj
        )
        family = Family(
            father=[Person(first_name="John", surname="Doe", sex=Sex.MALE, occ=0)],
            mother=[Person(first_name="Jane", surname="Smith", sex=Sex.FEMALE, occ=0)],
            events=[marriage_event, divorce_event],
        )

        marriage_events = family.get_marriage_events()
        divorce_events = family.get_divorce_events()

        assert len(marriage_events) == 1
        assert len(divorce_events) == 1
        assert marriage_events[0].event_name == FamilyEventName.MARRIAGE
        assert divorce_events[0].event_name == FamilyEventName.DIVORCE

    def test_family_get_events_by_type(self):
        """Test Family get_events_by_type method."""
        events = [
            FamilyEvent(event_name=FamilyEventName.MARRIAGE),
            FamilyEvent(event_name=FamilyEventName.MARRIAGE_BANN),
            FamilyEvent(event_name=FamilyEventName.DIVORCE),
        ]
        family = Family(
            father=[Person(first_name="John", surname="Doe", sex=Sex.MALE, occ=0)],
            events=events,
        )

        marriage_events = family.get_events_by_type(FamilyEventName.MARRIAGE)
        assert len(marriage_events) == 1

        all_marriage_events = family.get_marriage_events()
        assert len(all_marriage_events) == 2  # MARRIAGE + MARRIAGE_BANN

    def test_family_add_child(self):
        """Test Family add_child method (mutable)."""
        alice = Person(first_name="Alice", surname="Doe", sex=Sex.FEMALE, occ=0)
        bob = Person(first_name="Bob", surname="Doe", sex=Sex.MALE, occ=0)
        family = Family(
            father=[Person(first_name="John", surname="Doe", sex=Sex.MALE, occ=0)],
            children=[alice],
        )

        # Before adding Bob
        assert len(family.children) == 1
        assert alice in family.children

        # Add Bob
        family.add_child(bob)

        # After adding Bob - family is mutated
        assert len(family.children) == 2
        assert alice in family.children
        assert bob in family.children

        # Adding same child again with validation disabled does nothing
        initial_length = len(family.children)
        family.add_child(alice, validate=False)
        assert len(family.children) == initial_length

    def test_family_remove_child(self):
        """Test Family remove_child method (mutable)."""
        alice = Person(first_name="Alice", surname="Doe", sex=Sex.FEMALE, occ=0)
        bob = Person(first_name="Bob", surname="Doe", sex=Sex.MALE, occ=0)
        family = Family(
            father=[Person(first_name="John", surname="Doe", sex=Sex.MALE, occ=0)],
            children=[alice, bob],
        )

        # Before removing Alice
        assert len(family.children) == 2
        assert alice in family.children
        assert bob in family.children

        # Remove Alice
        family.remove_child(alice)

        # After removing Alice - family is mutated
        assert len(family.children) == 1
        assert alice not in family.children
        assert bob in family.children

        # Removing non-existent child does nothing
        charlie = Person(first_name="Charlie", surname="Doe", sex=Sex.MALE, occ=0)
        initial_length = len(family.children)
        family.remove_child(charlie)
        assert len(family.children) == initial_length

    def test_family_add_father(self):
        """Test adding fathers to family - supports multiple fathers."""
        father1 = Person(first_name="John", surname="Doe", sex=Sex.MALE, occ=0)
        father2 = Person(first_name="James", surname="Smith", sex=Sex.MALE, occ=0)
        mother = Person(first_name="Jane", surname="Doe", sex=Sex.FEMALE, occ=0)

        # Start with mother only
        family = Family(mother=[mother])

        # Initially no fathers
        assert family.father is None

        # Add first father
        family.add_father(father1)
        assert family.father is not None
        assert len(family.father) == 1
        assert father1 in family.father

        # Add second father (support multiple fathers)
        family.add_father(father2)
        assert len(family.father) == 2
        assert father1 in family.father
        assert father2 in family.father

        # Adding duplicate father does nothing
        initial_length = len(family.father)
        family.add_father(father1)
        assert len(family.father) == initial_length

    def test_family_add_mother(self):
        """Test adding mothers to family - supports multiple mothers."""
        father = Person(first_name="John", surname="Doe", sex=Sex.MALE, occ=0)
        mother1 = Person(first_name="Jane", surname="Doe", sex=Sex.FEMALE, occ=0)
        mother2 = Person(first_name="Mary", surname="Smith", sex=Sex.FEMALE, occ=0)

        # Start with father only
        family = Family(father=[father])

        # Initially no mothers
        assert family.mother is None

        # Add first mother
        family.add_mother(mother1)
        assert family.mother is not None
        assert len(family.mother) == 1
        assert mother1 in family.mother

        # Add second mother (support multiple mothers)
        family.add_mother(mother2)
        assert len(family.mother) == 2
        assert mother1 in family.mother
        assert mother2 in family.mother

        # Adding duplicate mother does nothing
        initial_length = len(family.mother)
        family.add_mother(mother1)
        assert len(family.mother) == initial_length

    def test_family_remove_father(self):
        """Test removing fathers from family."""
        father1 = Person(first_name="John", surname="Doe", sex=Sex.MALE, occ=0)
        father2 = Person(first_name="James", surname="Smith", sex=Sex.MALE, occ=0)
        mother = Person(first_name="Jane", surname="Doe", sex=Sex.FEMALE, occ=0)

        # Start with two fathers and one mother
        family = Family(father=[father1, father2], mother=[mother])

        # Before removing
        assert len(family.father) == 2
        assert father1 in family.father
        assert father2 in family.father

        # Remove first father
        family.remove_father(father1)
        assert len(family.father) == 1
        assert father1 not in family.father
        assert father2 in family.father

        # Remove second father
        family.remove_father(father2)
        assert family.father is None

        # Removing non-existent father does nothing
        non_existing = Person(first_name="Bob", surname="Unknown", sex=Sex.MALE, occ=0)
        family.remove_father(non_existing)  # Should not raise error
        assert family.father is None

    def test_family_remove_mother(self):
        """Test removing mothers from family."""
        father = Person(first_name="John", surname="Doe", sex=Sex.MALE, occ=0)
        mother1 = Person(first_name="Jane", surname="Doe", sex=Sex.FEMALE, occ=0)
        mother2 = Person(first_name="Mary", surname="Smith", sex=Sex.FEMALE, occ=0)

        # Start with one father and two mothers
        family = Family(father=[father], mother=[mother1, mother2])

        # Before removing
        assert len(family.mother) == 2
        assert mother1 in family.mother
        assert mother2 in family.mother

        # Remove first mother
        family.remove_mother(mother1)
        assert len(family.mother) == 1
        assert mother1 not in family.mother
        assert mother2 in family.mother

        # Remove second mother
        family.remove_mother(mother2)
        assert family.mother is None

        # Removing non-existent mother does nothing
        non_existing = Person(
            first_name="Alice", surname="Unknown", sex=Sex.FEMALE, occ=0
        )
        family.remove_mother(non_existing)  # Should not raise error
        assert family.mother is None

    def test_propagate_sosa_to_child_valueerror_branch(self):
        from geneweb.core.family import Family
        from geneweb.core.person import Person, Sex
        from geneweb.core.sosa import Sosa

        class DummyParent(Person):
            def get_all_sosa_numbers(self):
                # Sosa < 2 pour forcer ValueError
                return [Sosa(1)]

        class DummyChild(Person):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.sosa_added = []

            def add_sosa(self, sosa):
                self.sosa_added.append(sosa)

        # Patch Sosa.child_sosa pour lever ValueError
        orig_child_sosa = Sosa.child_sosa

        def child_sosa(self):
            if self.value < 2:
                raise ValueError("Sosa < 2 cannot have child")
            return Sosa(self.value // 2)

        Sosa.child_sosa = child_sosa
        # Test
        child = DummyChild(first_name="Test", surname="Child", sex=Sex.MALE, occ=0)
        family = Family()
        parent = DummyParent(first_name="Parent", surname="Test", sex=Sex.MALE, occ=0)
        family.father = [parent]
        family.mother = None
        family._propagate_sosa_to_child(child)
        Sosa.child_sosa = orig_child_sosa
        # On vérifie que rien n'a été ajouté (branche except/continue)
        assert not child.sosa_added


class TestFamilyIntegration:
    """Test Family integration with other components."""

    def test_family_with_witnesses(self):
        """Test Family with witness information."""
        witnesses = [
            WitnessInfo(
                Person(first_name="Alice", surname="Johnson", sex=Sex.FEMALE, occ=0),
                WitnessKind.WITNESS,
            ),
            WitnessInfo(
                Person(first_name="Bob", surname="Wilson", sex=Sex.MALE, occ=0),
                WitnessKind.WITNESS_CIVIL_OFFICER,
            ),
        ]
        family = Family(
            father=[Person(first_name="John", surname="Doe", sex=Sex.MALE, occ=0)],
            mother=[Person(first_name="Jane", surname="Smith", sex=Sex.FEMALE, occ=0)],
            witnesses=witnesses,
        )

        assert len(family.witnesses) == 2
        assert family.witnesses[0].witness_type == WitnessKind.WITNESS
        assert family.witnesses[1].witness_type == WitnessKind.WITNESS_CIVIL_OFFICER

    def test_family_complete_scenario(self):
        """Test complete family scenario with all features."""
        # Marriage event
        marriage_event = Event(
            place="Church of St. Mary",
            note="Beautiful ceremony",
        )
        marriage_event.set_date_from_components(1990, 6, 15)

        # Witnesses
        witnesses = [
            WitnessInfo(
                Person(first_name="Alice", surname="Johnson", sex=Sex.FEMALE, occ=0),
                WitnessKind.WITNESS,
            ),
            WitnessInfo(
                Person(first_name="Father", surname="Smith", sex=Sex.MALE, occ=0),
                WitnessKind.WITNESS_RELIGIOUS_OFFICER,
            ),
        ]

        # Family events
        events = [
            FamilyEvent(
                event_name=FamilyEventName.MARRIAGE,
                event=marriage_event,
                witnesses=witnesses[:1],
            )
        ]

        # Complete family
        family = Family(
            father=[Person(first_name="John", surname="Doe", sex=Sex.MALE, occ=0)],
            mother=[Person(first_name="Jane", surname="Smith", sex=Sex.FEMALE, occ=0)],
            children=[
                Person(first_name="Alice", surname="Doe", sex=Sex.FEMALE, occ=0),
                Person(first_name="Bob", surname="Doe", sex=Sex.MALE, occ=0),
            ],
            marriage=marriage_event,
            relation=RelationKind.MARRIED,
            events=events,
            witnesses=witnesses,
            comment="Happy family founded in 1990",
            sources="Parish records, civil registry",
            origin_file="family_records.ged",
        )

        # Verify all aspects
        assert family.has_father() and family.has_mother()
        assert family.children_count() == 2
        assert family.is_married() and not family.is_divorced()
        assert family.has_marriage_info()
        assert len(family.events) == 1
        assert len(family.witnesses) == 2
        assert "Happy family" in family.comment
        assert family.origin_file == "family_records.ged"
