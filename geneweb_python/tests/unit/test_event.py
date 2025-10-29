"""
Tests for the Event class.

This module contains all tests related to the Event class functionality,
including date handling, string representations, and data validation.
"""

from datetime import datetime

import pytest

from geneweb.core.calendar import CalendarDate, CalendarType
from geneweb.core.event import Event
from geneweb.core.place import Place


class TestEvent:
    """Test the Event class."""

    def test_event_empty(self):
        """Test empty event creation."""
        event = Event()
        assert event.calendar_date is None
        assert event.place.name == ""
        assert event.note == ""
        assert event.src == ""
        assert event.date is None
        assert not event  # Should be false when empty

    def test_event_with_calendar_date(self):
        """Test event with CalendarDate data."""
        event = Event(
            place=Place("Paris, France"),
            note="Hospital birth",
            src="Birth certificate",
        )
        cal_date = CalendarDate(
            year=1990, month=1, day=15, calendar_type=CalendarType.GREGORIAN
        )
        event.calendar_date = cal_date

        assert event.date == "1990-01-15"
        assert event.place.name == "Paris, France"
        assert event.note == "Hospital birth"
        assert event.src == "Birth certificate"
        assert bool(event)  # Should be true when has data

    def test_event_str_representation(self):
        """Test event string representation."""
        event = Event(place=Place("Paris"))
        cal_date = CalendarDate(year=1990, month=1, day=15)
        event.calendar_date = cal_date

        assert "Date: 1990-01-15" in str(event)
        assert "Place: Paris" in str(event)

        empty_event = Event()
        assert str(empty_event) == "No information"

    def test_event_date_helper_methods(self):
        """Test Event date helper methods."""
        event = Event()

        # Test set_date_from_string method
        event.set_date_from_string("1990-01-15")
        assert event.date == "1990-01-15"
        assert event.calendar_date.year == 1990
        assert event.calendar_date.month == 1
        assert event.calendar_date.day == 15

        # Test set_date_from_components method
        event.set_date_from_components(2022, 12, 25)
        assert event.date == "2022-12-25"

        # Test calendar_date_obj property
        assert event.calendar_date_obj.year == 2022
        assert event.calendar_date_obj.month == 12
        assert event.calendar_date_obj.day == 25

    def test_event_partial_dates(self):
        """Test Event with partial dates."""
        # Test year-only date
        event = Event()
        event.set_date_from_string("1990")
        assert event.date == "1990"

        # Test year-month date
        event.set_date_from_string("1990-05")
        assert event.date == "1990-05"

        # Test calendar_date_obj returns the CalendarDate for partial dates
        partial_date = CalendarDate(year=1990, month=5)
        event.calendar_date = partial_date
        assert event.calendar_date_obj == partial_date
        assert not event.calendar_date_obj.is_complete()

    def test_event_clear_date(self):
        """Test clearing event date."""
        event = Event()
        event.set_date_from_string("1990-01-15")
        assert event.date is not None

        # Clear date by setting to None
        event.set_date_from_string("")
        assert event.calendar_date is None
        assert event.date is None

    def test_event_from_datetime(self):
        """Test Event creation from datetime object."""
        dt = datetime(1990, 5, 15)
        event = Event.from_datetime(
            dt, place=Place("Hospital"), note="Birth", src="Certificate"
        )

        assert event.date == "1990-05-15"
        assert event.place.name == "Hospital"
        assert event.note == "Birth"
        assert event.src == "Certificate"

    def test_event_from_date_string(self):
        """Test Event creation from date string."""
        event = Event.from_date_string(
            "1990-05-15", place=Place("Hospital"), note="Birth"
        )

        assert event.date == "1990-05-15"
        assert event.place.name == "Hospital"
        assert event.note == "Birth"

    def test_event_repr(self):
        """Test Event __repr__ method."""
        event = Event(place=Place("Paris"), note="Birth")
        event.set_date_from_string("1990-01-01")

        repr_str = repr(event)
        assert "Event(" in repr_str
        assert "date='1990-01-01'" in repr_str
        assert "place='Paris'" in repr_str
        assert "note='Birth'" in repr_str


class TestEventStringRepresentation:
    """Test Event __str__ method for missing coverage."""

    def test_event_str_with_note_only(self):
        """Test Event __str__ when only note is present."""
        event = Event(note="Important note")
        assert str(event) == "Note: Important note"

    def test_event_str_multiple_fields(self):
        """Test Event __str__ with multiple fields."""
        event = Event.from_datetime(
            datetime(1990, 1, 1), place=Place("Paris"), note="Birth certificate"
        )
        expected = "Date: 1990-01-01, Place: Paris, Note: Birth certificate"
        assert str(event) == expected

    def test_event_str_with_place_only(self):
        """Test Event __str__ when only place is present."""
        event = Event(place=Place("London"))
        assert str(event) == "Place: London"


class TestEventEdgeCases:
    """Test edge cases and error conditions for Event class."""

    def test_event_with_none_datetime(self):
        """Test Event.from_datetime with None datetime."""
        event = Event.from_datetime(None, place=Place("Unknown"))
        assert event.date is None
        assert event.place.name == "Unknown"

    def test_event_set_date_from_components_with_none_year(self):
        """Test set_date_from_components with None year."""
        event = Event()
        event.set_date_from_components(None, 5, 15)
        assert event.calendar_date is None
        assert event.date is None

    @pytest.mark.parametrize(
        "field,value",
        [("place", "Paris"), ("note", "Important note"), ("src", "Source document")],
    )
    def test_event_bool_with_single_field(self, field, value):
        """Test Event __bool__ when only one field is set."""
        if field == "place":
            event = Event(place=Place(value))
        else:
            kwargs = {field: value}
            event = Event(**kwargs)
        assert bool(event) is True
