"""
Event system for genealogical records.

This module provides the Event class for representing dated events
like births, deaths, baptisms, marriages, etc. with associated metadata.
"""

from typing import Optional

from geneweb.core.calendar import CalendarDate, CalendarType
from geneweb.core.place import Place


class Event:
    """
    Generic event information for genealogical records.

    This class represents any dated event (birth, death, baptism, burial, etc.)
    with associated metadata like place, notes, and sources.

    Attributes:
        calendar_date: Date of the event using CalendarDate system
                      (can be partial, approximate, etc.)
        place: Location where the event occurred
        note: Additional notes about the event
        src: Sources documenting this event
    """

    def __init__(self, place: Optional[Place] = None, note: str = "", src: str = ""):
        """
        Initialize an Event.

        Args:
            place: Location where the event occurred
            note: Additional notes about the event
            src: Sources documenting this event
        """
        self.calendar_date: Optional[CalendarDate] = None
        self.place = place if place is not None else Place("")
        self.note = note
        self.src = src

    @property
    def date(self) -> Optional[str]:
        """
        Return date as string for backward compatibility.

        Returns:
            Date string in YYYY-MM-DD format or None if no date
        """
        if self.calendar_date is None:
            return None

        # Format the CalendarDate as a string
        if self.calendar_date.is_complete():
            return (
                f"{self.calendar_date.year:04d}-"
                f"{self.calendar_date.month:02d}-"
                f"{self.calendar_date.day:02d}"
            )
        elif self.calendar_date.year:
            if self.calendar_date.month:
                return f"{self.calendar_date.year:04d}-{self.calendar_date.month:02d}"
            else:
                return f"{self.calendar_date.year:04d}"
        return None

    @property
    def calendar_date_obj(self) -> Optional[CalendarDate]:
        """
        Return CalendarDate object (replaces datetime_obj).

        Returns:
            CalendarDate object if available, None otherwise
        """
        return self.calendar_date

    def set_date_from_string(
        self, date_str: str, calendar_type: CalendarType = CalendarType.GREGORIAN
    ) -> None:
        """
        Set date from string representation.

        Args:
            date_str: Date string in various formats
            calendar_type: Calendar system to use
        """
        if not date_str:
            self.calendar_date = None
            return

        # Try to parse the date string
        # Simple parsing - can be enhanced later
        parts = date_str.replace("-", "/").replace(".", "/").split("/")

        year = None
        month = None
        day = None

        if len(parts) >= 1:
            try:
                year = int(parts[0])
            except ValueError:
                pass

        if len(parts) >= 2:
            try:
                month = int(parts[1])
            except ValueError:
                pass

        if len(parts) >= 3:
            try:
                day = int(parts[2])
            except ValueError:
                pass

        self.calendar_date = CalendarDate(
            year=year, month=month, day=day, calendar_type=calendar_type
        )

    def set_date_from_components(
        self,
        year: int,
        month: Optional[int] = None,
        day: Optional[int] = None,
        calendar_type: CalendarType = CalendarType.GREGORIAN,
    ) -> None:
        """
        Set date from individual components.

        Args:
            year: Year component
            month: Month component (optional)
            day: Day component (optional)
            calendar_type: Calendar system to use
        """
        if year is None:
            self.calendar_date = None
            return

        self.calendar_date = CalendarDate(
            year=year, month=month, day=day, calendar_type=calendar_type
        )

    @classmethod
    def from_datetime(
        cls,
        dt,  # Accept any object with year, month, day attributes
        place: Optional[Place] = None,
        note: str = "",
        src: str = "",
        calendar_type: CalendarType = CalendarType.GREGORIAN,
    ) -> "Event":
        """
        Create Event from datetime-like object (backward compatibility helper).

        Args:
            dt: Object with year, month, day attributes (like datetime)
            place: Event place (Place object)
            note: Event note
            src: Event source
            calendar_type: Calendar system

        Returns:
            Event instance
        """
        if place is None:
            place = Place("")
        event = cls(place=place, note=note, src=src)
        if dt is not None:
            event.set_date_from_components(dt.year, dt.month, dt.day, calendar_type)
        return event

    @classmethod
    def from_date_string(
        cls,
        date_str: str,
        place: Optional[Place] = None,
        note: str = "",
        src: str = "",
        calendar_type: CalendarType = CalendarType.GREGORIAN,
    ) -> "Event":
        """
        Create Event from date string (backward compatibility helper).

        Args:
            date_str: Date string
            place: Event place (Place object)
            note: Event note
            src: Event source
            calendar_type: Calendar system

        Returns:
            Event instance
        """
        if place is None:
            place = Place("")
        event = cls(place=place, note=note, src=src)
        if date_str:
            event.set_date_from_string(date_str, calendar_type)
        return event

    def __bool__(self) -> bool:
        """Return True if event has any meaningful data."""
        return bool(self.date or self.place.name or self.note or self.src)

    def __str__(self) -> str:
        """Return string representation for display."""
        parts = []
        if self.date:
            parts.append(f"Date: {self.date}")
        if self.place.name:
            parts.append(f"Place: {self.place.name}")
        if self.note:
            parts.append(f"Note: {self.note}")
        return ", ".join(parts) if parts else "No information"

    def __repr__(self) -> str:
        """Return detailed string representation for debugging."""
        return (
            f"Event(date='{self.date}', place='{self.place.name}', "
            f"note='{self.note}', src='{self.src}')"
        )
