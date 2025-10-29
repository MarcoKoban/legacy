from datetime import datetime

import pytest

from geneweb.core.event import Event
from geneweb.core.person import (
    Access,
    Burial,
    BurialInfo,
    Death,
    DeathInfo,
    Person,
    Sex,
)
from geneweb.core.place import Place
from geneweb.core.sosa import Sosa


class TestDeathInfo:
    """Test the DeathInfo class."""

    def test_death_info_alive(self):
        """Test death info for living person."""
        death_info = DeathInfo()
        assert death_info.status == Death.NOT_DEAD
        assert not death_info.event
        assert not death_info  # Should be false for alive person
        assert str(death_info) == "Alive"

    def test_death_info_dead(self):
        """Test death info for deceased person."""
        death_event = Event.from_datetime(datetime(2020, 3, 15), place=Place("London"))
        death_info = DeathInfo(status=Death.OF_COURSE_DEAD, event=death_event)

        assert death_info.status == Death.OF_COURSE_DEAD
        assert death_info.event.date == "2020-03-15"
        assert bool(death_info)  # Should be truth
        assert "Of Course Dead" in str(death_info)


class TestBurialInfo:
    """Test the BurialInfo class."""

    def test_burial_info_unknown(self):
        """Test burial info for unknown burial."""
        burial_info = BurialInfo()
        assert burial_info.burial_type == Burial.UNKNOWN_BURIAL
        assert not burial_info.event
        assert not burial_info
        assert str(burial_info) == "Unknown burial"

    def test_burial_info_buried(self):
        """Test burial info for buried person."""
        burial_event = Event.from_datetime(
            datetime(2020, 3, 20), place=Place("Cemetery")
        )
        burial_info = BurialInfo(burial_type=Burial.BURIED, event=burial_event)

        assert burial_info.burial_type == Burial.BURIED
        assert burial_info.event.place.name == "Cemetery"
        assert bool(burial_info)
        assert "Buried" in str(burial_info)


class TestPersonImproved:
    """Test the improved Person class with structured events."""

    def test_person_creation_minimal(self):
        """Test creating person with minimal required information."""
        person = Person(first_name="John", surname="Doe", sex=Sex.MALE)

        assert person.first_name == "John"
        assert person.surname == "Doe"
        assert person.sex == Sex.MALE
        assert person.occ == 0
        assert person.access == Access.PUBLIC

        # Check default events
        assert not person.birth  # Empty event should be false
        assert not person.baptism
        assert not person.death  # Alive by default
        assert not person.burial

    def test_person_with_birth_event(self):
        """Test person with birth event information."""
        birth_event = Event.from_datetime(
            datetime(1990, 1, 15), place="Paris, France", note="Hospital birth"
        )

        person = Person(
            first_name="Marie", surname="Dupont", sex=Sex.FEMALE, birth=birth_event
        )

        assert person.has_birth_info()
        assert person.birth.date == "1990-01-15"
        assert person.birth.place == "Paris, France"
        assert person.birth_year() == "1990"

    def test_person_with_death_info(self):
        """Test person with death information."""
        death_event = Event.from_datetime(datetime(2020, 3, 15), place="London")
        death_info = DeathInfo(status=Death.OF_COURSE_DEAD, event=death_event)

        person = Person(
            first_name="Robert", surname="Smith", sex=Sex.MALE, death=death_info
        )

        assert person.has_death_info()
        assert person.is_dead()
        assert not person.is_alive()
        assert person.death_year() == "2020"
        assert person.lifespan() == "? - 2020"

    def test_person_lifespan_calculations(self):
        """Test lifespan calculation methods."""
        birth_event = Event.from_datetime(datetime(1950, 6, 20))
        death_event = Event.from_datetime(datetime(2020, 12, 10))
        death_info = DeathInfo(status=Death.OF_COURSE_DEAD, event=death_event)

        person = Person(
            first_name="Elizabeth",
            surname="Johnson",
            sex=Sex.FEMALE,
            birth=birth_event,
            death=death_info,
        )

        assert person.birth_year() == "1950"
        assert person.death_year() == "2020"
        assert person.lifespan() == "1950 - 2020"

    def test_person_status_methods(self):
        """Test person status inquiry methods."""
        # Living person
        alive_person = Person("John", "Doe", Sex.MALE)
        assert alive_person.is_alive()
        assert not alive_person.is_dead()
        assert not alive_person.death_status_unknown()

        # Dead person
        dead_person = Person(
            "Jane", "Doe", Sex.FEMALE, death=DeathInfo(status=Death.OF_COURSE_DEAD)
        )
        assert not dead_person.is_alive()
        assert dead_person.is_dead()

        # Unknown status
        unknown_person = Person(
            "Mystery",
            "Person",
            Sex.NEUTER,
            death=DeathInfo(status=Death.DONT_KNOW_IF_DEAD),
        )
        assert unknown_person.death_status_unknown()
        assert not unknown_person.is_alive()
        assert not unknown_person.is_dead()

    def test_person_immutability(self):
        """Test that Person objects are mutable (architectural change)."""
        person = Person("John", "Doe", Sex.MALE)

        # Person objects are now mutable to match Family architecture
        person.first_name = "Jane"
        assert person.first_name == "Jane"

    def test_event_immutability(self):
        """Test that Event objects are immutable."""
        event = Event.from_datetime(datetime(2020, 1, 1))

        # Should not be able to modify frozen dataclass
        with pytest.raises(AttributeError):
            event.date = datetime(2020, 1, 2)


class TestPersonWithSosa:
    """Test Person integration with Sosa numbering."""

    def test_person_with_sosa(self):
        """Test person with Sosa number."""
        person = Person(
            first_name="Root", surname="Person", sex=Sex.MALE, sosa=Sosa.one()
        )

        assert person.sosa is not None
        assert person.sosa.value == 1
        assert person.sosa.generation() == 1


class TestPersonValidation:
    """Test validation and edge cases to reach 100% coverage."""

    def test_empty_first_name_validation(self):
        """Test validation error for empty first name (line 222)."""
        with pytest.raises(ValueError, match="First name cannot be empty"):
            Person(first_name="", surname="Doe", sex=Sex.MALE)

    def test_whitespace_first_name_validation(self):
        """Test validation error for whitespace-only first name (line 222)."""
        with pytest.raises(ValueError, match="First name cannot be empty"):
            Person(first_name="   ", surname="Doe", sex=Sex.MALE)

    def test_empty_surname_validation(self):
        """Test validation error for empty surname (line 225)."""
        with pytest.raises(ValueError, match="Surname cannot be empty"):
            Person(first_name="John", surname="", sex=Sex.MALE)

    def test_whitespace_surname_validation(self):
        """Test validation error for whitespace-only surname (line 225)."""
        with pytest.raises(ValueError, match="Surname cannot be empty"):
            Person(first_name="John", surname="   ", sex=Sex.MALE)

    def test_negative_occurrence_validation(self):
        """Test validation error for negative occurrence (line 228)."""
        with pytest.raises(ValueError, match="Occurrence must be non-negative"):
            Person(first_name="John", surname="Doe", sex=Sex.MALE, occ=-1)


class TestPersonStringMethods:
    """Test string representation methods for complete coverage."""

    def test_str_with_occurrence(self):
        """Test __str__ method with occurrence > 0 (line 232)."""
        person = Person(first_name="John", surname="Doe", sex=Sex.MALE, occ=2)
        assert str(person) == "John Doe (2)"

    def test_str_without_occurrence(self):
        """Test __str__ method with occurrence = 0 (line 234)."""
        person = Person(first_name="John", surname="Doe", sex=Sex.MALE)
        assert str(person) == "John Doe"

    def test_repr_method(self):
        """Test __repr__ method for debugging (line 238)."""
        person = Person(first_name="John", surname="Doe", occ=1, sex=Sex.MALE)
        expected = "Person(first_name='John', surname='Doe', occ=1, sex=MALE)"
        assert repr(person) == expected

    def test_hash_method(self):
        """Test __hash__ method for sets and dicts (line 245)."""
        person1 = Person(first_name="John", surname="Doe", sex=Sex.MALE, occ=1)
        person2 = Person(first_name="John", surname="Doe", sex=Sex.FEMALE, occ=1)
        person3 = Person(first_name="Jane", surname="Doe", sex=Sex.MALE, occ=1)

        # Same persons should have same hash
        assert hash(person1) == hash(person2)
        # Different persons should typically have different hash
        assert hash(person1) != hash(person3)

    def test_eq_with_non_person_object(self):
        """Test equality with non-Person object (line 249)."""
        person = Person(first_name="John", surname="Doe", sex=Sex.MALE)
        assert person != "not a person"
        assert person != 42
        assert person is not None

    def test_eq_with_different_persons(self):
        """Test equality with different persons (line 251)."""
        person1 = Person(first_name="John", surname="Doe", sex=Sex.MALE, occ=1)
        person2 = Person(first_name="Jane", surname="Doe", sex=Sex.MALE, occ=1)
        person3 = Person(first_name="John", surname="Smith", sex=Sex.MALE, occ=1)
        person4 = Person(first_name="John", surname="Doe", sex=Sex.MALE, occ=2)

        assert person1 != person2  # Different first name
        assert person1 != person3  # Different surname
        assert person1 != person4  # Different occurrence


class TestPersonUtilityMethods:
    """Test utility methods for complete coverage."""

    def test_full_name_with_public_name(self):
        """Test full_name method when public_name is set (line 259)."""
        person = Person(
            first_name="John", surname="Doe", sex=Sex.MALE, public_name="Johnny D"
        )
        assert person.full_name() == "Johnny D"

    def test_full_name_without_public_name(self):
        """Test full_name method when public_name is empty (line 261)."""
        person = Person(first_name="John", surname="Doe", sex=Sex.MALE, occ=2)
        assert person.full_name() == "John Doe (2)"

    def test_is_dead_with_different_statuses(self):
        """Test is_dead method with various death statuses (line 293)."""
        # Test DEAD_YOUNG
        person1 = Person(
            first_name="John",
            surname="Doe",
            sex=Sex.MALE,
            death=DeathInfo(status=Death.DEAD_YOUNG),
        )
        assert person1.is_dead()

        # Test DEAD_DONT_KNOW_WHEN
        person2 = Person(
            first_name="Jane",
            surname="Doe",
            sex=Sex.FEMALE,
            death=DeathInfo(status=Death.DEAD_DONT_KNOW_WHEN),
        )
        assert person2.is_dead()

        # Test OF_COURSE_DEAD
        person3 = Person(
            first_name="Bob",
            surname="Smith",
            sex=Sex.MALE,
            death=DeathInfo(status=Death.OF_COURSE_DEAD),
        )
        assert person3.is_dead()

    def test_death_status_unknown(self):
        """Test death_status_unknown method (line 313)."""
        person = Person(
            first_name="John",
            surname="Doe",
            sex=Sex.MALE,
            death=DeathInfo(status=Death.DONT_KNOW_IF_DEAD),
        )
        assert person.death_status_unknown()

        # Test with known status
        person_alive = Person(first_name="Jane", surname="Doe", sex=Sex.FEMALE)
        assert not person_alive.death_status_unknown()

    def test_birth_year_extraction_no_match(self):
        """Test birth_year when no year pattern matches (line 323)."""
        person = Person(
            first_name="John",
            surname="Doe",
            sex=Sex.MALE,
            birth=Event.from_date_string("sometime in the past"),
        )
        assert person.birth_year() is None

    def test_birth_year_extraction_no_date(self):
        """Test birth_year when no date available (line 325)."""
        person = Person(first_name="John", surname="Doe", sex=Sex.MALE)
        assert person.birth_year() is None

    def test_death_year_extraction_no_date(self):
        """Test death_year when no death date available (line 329)."""
        person = Person(
            first_name="John",
            surname="Doe",
            sex=Sex.MALE,
            death=DeathInfo(status=Death.DEAD_YOUNG),  # No event date
        )
        assert person.death_year() is None

    def test_has_burial_info_with_burial(self):
        """Test has_burial_info method with burial data (line 293)."""
        person = Person(
            first_name="John",
            surname="Doe",
            sex=Sex.MALE,
            burial=BurialInfo(burial_type=Burial.BURIED),
        )
        assert person.has_burial_info()

    def test_birth_year_extraction_with_match(self):
        """Test birth_year when regex matches a year (line 323)."""
        person = Person(
            first_name="John",
            surname="Doe",
            sex=Sex.MALE,
            birth=Event.from_datetime(datetime(1990, 1, 1)),
        )
        assert person.birth_year() == "1990"

    def test_death_year_extraction_with_match(self):
        """Test death_year when regex matches a year (line 329)."""
        person = Person(
            first_name="John",
            surname="Doe",
            sex=Sex.MALE,
            death=DeathInfo(
                status=Death.DEAD_YOUNG, event=Event.from_datetime(datetime(2020, 1, 1))
            ),
        )
        assert person.death_year() == "2020"

    def test_death_year_extraction_no_match_with_date(self):
        """Test death_year when date exists but no year pattern matches (line 312)."""
        person = Person(
            first_name="John",
            surname="Doe",
            sex=Sex.MALE,
            death=DeathInfo(
                status=Death.DEAD_YOUNG, event=Event.from_date_string("died long ago")
            ),
        )
        assert person.death_year() is None

    def test_lifespan_birth_only_alive(self):
        """Test lifespan with birth year but alive (line 325)."""
        person = Person(
            first_name="John",
            surname="Doe",
            sex=Sex.MALE,
            birth=Event.from_datetime(datetime(1990, 1, 1)),
        )
        assert person.lifespan() == "1990 - "

    def test_lifespan_birth_only_dead(self):
        """Test lifespan with birth year but dead with unknown death date."""
        person = Person(
            first_name="John",
            surname="Doe",
            sex=Sex.MALE,
            birth=Event.from_datetime(datetime(1990, 1, 1)),
            death=DeathInfo(status=Death.DEAD_YOUNG),  # Dead but no death date
        )
        assert person.lifespan() == "1990 - ?"

    def test_lifespan_death_only(self):
        """Test lifespan with death year only."""
        person = Person(
            first_name="John",
            surname="Doe",
            sex=Sex.MALE,
            death=DeathInfo(
                status=Death.DEAD_YOUNG, event=Event.from_datetime(datetime(2020, 1, 1))
            ),
        )
        assert person.lifespan() == "? - 2020"

    def test_lifespan_returns_empty_string(self):
        """Test lifespan returns empty string when no birth or death info."""
        person = Person(first_name="John", surname="Doe", sex=Sex.MALE)
        assert person.lifespan() == ""
