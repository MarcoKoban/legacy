"""
Calendar module for handling multiple calendar systems and date conversions.

This module provides support for various calendar systems used in genealogical records:
- Gregorian calendar (modern standard)
- Julian calendar (pre-1582 historical dates)
- French Revolutionary calendar (1792-1805)
- Hebrew calendar (religious/cultural dates)

Each calendar system supports conversion to/from Serial Day Number (SDN) format
and provides round-trip conversion capabilities with other calendar systems.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class CalendarType(Enum):
    """Enumeration of supported calendar types."""

    GREGORIAN = "gregorian"
    JULIAN = "julian"
    FRENCH = "french"
    HEBREW = "hebrew"


@dataclass
class CalendarDate:
    """Represents a date in any calendar system with optional incomplete components."""

    year: Optional[int] = None
    month: Optional[int] = None
    day: Optional[int] = None
    calendar_type: CalendarType = CalendarType.GREGORIAN

    def is_complete(self) -> bool:
        """Check if the date has all components (year, month, day)."""
        return all(
            [self.year is not None, self.month is not None, self.day is not None]
        )

    def is_valid(self) -> bool:
        """Check if the date components are within valid ranges."""
        # Check for zero or negative values which are invalid
        if self.year is not None and self.year <= 0:
            return False
        if self.month is not None and (self.month <= 0 or self.month > 12):
            return False
        if self.day is not None and (self.day <= 0 or self.day > 31):
            return False

        # If all non-None components are valid, the date is considered valid
        return True


class CalendarError(Exception):
    """Base exception for calendar-related errors."""

    pass


class SDNConversionError(CalendarError):
    """Exception raised when SDN conversion fails due to incomplete or invalid data."""

    pass


class CalendarSystem(ABC):
    """Abstract base class for calendar system implementations."""

    @property
    @abstractmethod
    def calendar_type(self) -> CalendarType:
        """Return the calendar type this system implements."""
        pass

    @abstractmethod
    def to_sdn(self, cal_date: CalendarDate) -> int:
        """
        Convert a calendar date to Serial Day Number (SDN).

        Args:
            cal_date: The calendar date to convert

        Returns:
            Serial Day Number as integer

        Raises:
            SDNConversionError: If conversion fails due to incomplete/invalid data
        """
        pass

    @abstractmethod
    def from_sdn(self, sdn: int) -> CalendarDate:
        """
        Convert a Serial Day Number to this calendar system.

        Args:
            sdn: Serial Day Number to convert

        Returns:
            CalendarDate in this calendar system
        """
        pass

    def convert_to(
        self, cal_date: CalendarDate, target_system: "CalendarSystem"
    ) -> CalendarDate:
        """
        Convert a date from this calendar to another calendar system.

        Args:
            cal_date: Date in this calendar system
            target_system: Target calendar system

        Returns:
            Date in target calendar system
        """
        sdn = self.to_sdn(cal_date)
        return target_system.from_sdn(sdn)


class GregorianCalendar(CalendarSystem):
    """Gregorian calendar system (modern standard calendar)."""

    @property
    def calendar_type(self) -> CalendarType:
        return CalendarType.GREGORIAN

    def to_sdn(self, cal_date: CalendarDate) -> int:
        """Convert Gregorian date to SDN."""
        if not cal_date.is_complete():
            raise SDNConversionError(
                f"Cannot convert incomplete Gregorian date to SDN: "
                f"year={cal_date.year}, month={cal_date.month}, day={cal_date.day}"
            )

        if not cal_date.is_valid():
            raise SDNConversionError(
                f"Cannot convert incomplete Gregorian date to SDN: "
                f"year={cal_date.year}, month={cal_date.month}, day={cal_date.day}"
            )

        # Simplified SDN calculation for Gregorian calendar
        year, month, day = cal_date.year, cal_date.month, cal_date.day

        # Use a simple linear approximation for SDN
        # This is a simplified algorithm - real implementations would be more complex

        # At this point we know year, month, day are not None due to is_complete() check
        if year is None or month is None or day is None:
            raise SDNConversionError(
                "Year, month, and day must be specified for SDN conversion."
            )

        # Approximate days since a reference date (year 1 AD = SDN 1721426)
        days_from_year_1 = (
            (year - 1) * 365 + (year - 1) // 4 - (year - 1) // 100 + (year - 1) // 400
        )

        # Days for months (approximate)
        days_in_months = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
        days_from_months = days_in_months[month - 1]

        # Add leap day if after February in a leap year
        if month > 2 and year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
            days_from_months += 1

        sdn = 1721426 + days_from_year_1 + days_from_months + day - 1
        return sdn

    def from_sdn(self, sdn: int) -> CalendarDate:
        """Convert SDN to Gregorian date."""
        # Simplified reverse calculation
        days_since_year_1 = sdn - 1721426

        # Approximate year (not accounting for leap years precisely)
        year = max(1, int(days_since_year_1 / 365.25) + 1)

        # Refine year calculation
        while True:
            year_start_sdn = self.to_sdn(
                CalendarDate(
                    year=year, month=1, day=1, calendar_type=CalendarType.GREGORIAN
                )
            )
            if year_start_sdn <= sdn:
                next_year_start_sdn = self.to_sdn(
                    CalendarDate(
                        year=year + 1,
                        month=1,
                        day=1,
                        calendar_type=CalendarType.GREGORIAN,
                    )
                )
                if next_year_start_sdn > sdn:
                    break
                year += 1
            else:
                year -= 1

        # Find month and day
        days_into_year = sdn - year_start_sdn + 1

        # Days in each month (non-leap year)
        days_in_months = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

        # Adjust for leap year
        if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
            days_in_months[1] = 29

        month = 1
        while month <= 12 and days_into_year > days_in_months[month - 1]:
            days_into_year -= days_in_months[month - 1]
            month += 1

        day = days_into_year

        return CalendarDate(
            year=year, month=month, day=day, calendar_type=CalendarType.GREGORIAN
        )


class JulianCalendar(CalendarSystem):
    """Julian calendar system (pre-1582 historical calendar)."""

    @property
    def calendar_type(self) -> CalendarType:
        return CalendarType.JULIAN

    def to_sdn(self, cal_date: CalendarDate) -> int:
        """Convert Julian date to SDN."""
        if not cal_date.is_complete():
            raise SDNConversionError(
                f"Cannot convert incomplete Julian date to SDN: "
                f"year={cal_date.year}, month={cal_date.month}, day={cal_date.day}"
            )

        if not cal_date.is_valid():
            raise SDNConversionError(
                f"Cannot convert incomplete Julian date to SDN: "
                f"year={cal_date.year}, month={cal_date.month}, day={cal_date.day}"
            )

        # Julian calendar SDN conversion (simplified)
        year, month, day = cal_date.year, cal_date.month, cal_date.day

        # At this point we know year, month, day are not None due to is_complete() check
        if year is None or month is None or day is None:
            raise SDNConversionError(
                "Year, month, and day must be specified for SDN conversion."
            )

        # Julian calendar: simpler leap year rules (every 4 years)
        days_from_year_1 = (year - 1) * 365 + (year - 1) // 4

        # Days for months (approximate)
        days_in_months = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
        days_from_months = days_in_months[month - 1]

        # Add leap day if after February in a leap year (Julian: every 4 years)
        if month > 2 and year % 4 == 0:
            days_from_months += 1

        # Julian calendar reference point (different from Gregorian)
        sdn = 1721424 + days_from_year_1 + days_from_months + day - 1
        return sdn

    def from_sdn(self, sdn: int) -> CalendarDate:
        """Convert SDN to Julian date."""
        # Simplified reverse calculation for Julian calendar
        days_since_year_1 = sdn - 1721424

        # Approximate year (Julian leap years every 4 years)
        year = max(1, int(days_since_year_1 / 365.25) + 1)

        # Refine year calculation
        while True:
            year_start_sdn = self.to_sdn(
                CalendarDate(
                    year=year, month=1, day=1, calendar_type=CalendarType.JULIAN
                )
            )
            if year_start_sdn <= sdn:
                next_year_start_sdn = self.to_sdn(
                    CalendarDate(
                        year=year + 1, month=1, day=1, calendar_type=CalendarType.JULIAN
                    )
                )
                if next_year_start_sdn > sdn:
                    break
                year += 1
            else:
                year -= 1

        # Find month and day
        days_into_year = sdn - year_start_sdn + 1

        # Days in each month (non-leap year)
        days_in_months = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

        # Adjust for leap year (Julian: every 4 years)
        if year % 4 == 0:
            days_in_months[1] = 29

        month = 1
        while month <= 12 and days_into_year > days_in_months[month - 1]:
            days_into_year -= days_in_months[month - 1]
            month += 1

        day = days_into_year

        return CalendarDate(
            year=year, month=month, day=day, calendar_type=CalendarType.JULIAN
        )


class FrenchCalendar(CalendarSystem):
    """French Revolutionary calendar system (1792-1805)."""

    @property
    def calendar_type(self) -> CalendarType:
        return CalendarType.FRENCH

    def to_sdn(self, cal_date: CalendarDate) -> int:
        """Convert French Revolutionary date to SDN."""
        if not cal_date.is_complete():
            raise SDNConversionError(
                f"Cannot convert incomplete French Revolutionary date to SDN: "
                f"year={cal_date.year}, month={cal_date.month}, day={cal_date.day}"
            )

        if not cal_date.is_valid():
            raise SDNConversionError(
                f"Cannot convert incomplete French Revolutionary date to SDN: "
                f"year={cal_date.year}, month={cal_date.month}, day={cal_date.day}"
            )

        # French Revolutionary calendar conversion (simplified)
        # Year 1 began September 22, 1792 (Gregorian)
        year, month, day = cal_date.year, cal_date.month, cal_date.day

        # At this point we know year, month, day are not None due to is_complete() check
        if year is None or month is None or day is None:
            raise SDNConversionError(
                "Year, month, and day must be specified for SDN conversion."
            )

        # Convert to equivalent Gregorian date first
        # French Revolutionary calendar has 12 months of 30 days + 5/6 extra days
        total_days = (month - 1) * 30 + day - 1

        # Add days to September 22, 1792
        base_sdn = GregorianCalendar().to_sdn(
            CalendarDate(
                year=1792, month=9, day=22, calendar_type=CalendarType.GREGORIAN
            )
        )
        return base_sdn + total_days

    def from_sdn(self, sdn: int) -> CalendarDate:
        """Convert SDN to French Revolutionary date."""
        # Convert from base date of September 22, 1792
        base_sdn = GregorianCalendar().to_sdn(
            CalendarDate(
                year=1792, month=9, day=22, calendar_type=CalendarType.GREGORIAN
            )
        )

        days_since_base = sdn - base_sdn
        year = (
            days_since_base // 365
        ) + 1  # Simplified - doesn't account for leap years
        remaining_days = days_since_base % 365

        month = (remaining_days // 30) + 1
        day = (remaining_days % 30) + 1

        return CalendarDate(
            year=year, month=month, day=day, calendar_type=CalendarType.FRENCH
        )


class HebrewCalendar(CalendarSystem):
    """Hebrew calendar system (lunisolar religious calendar)."""

    @property
    def calendar_type(self) -> CalendarType:
        return CalendarType.HEBREW

    def to_sdn(self, cal_date: CalendarDate) -> int:
        """Convert Hebrew date to SDN."""
        if not cal_date.is_complete():
            raise SDNConversionError(
                f"Cannot convert incomplete Hebrew date to SDN: "
                f"year={cal_date.year}, month={cal_date.month}, day={cal_date.day}"
            )

        if not cal_date.is_valid():
            raise SDNConversionError(
                f"Cannot convert incomplete Hebrew date to SDN: "
                f"year={cal_date.year}, month={cal_date.month}, day={cal_date.day}"
            )

        # Hebrew calendar conversion (very simplified)
        # In reality, this is extremely complex due to lunisolar calculations
        year, month, day = cal_date.year, cal_date.month, cal_date.day

        # Approximate conversion using average Hebrew year length
        # Hebrew year 1 corresponds to 3761 BCE
        if year is None:
            raise ValueError("Year is required for Hebrew calendar conversion")
        gregorian_year = year - 3761

        # Use approximate conversion via Gregorian calendar
        gregorian_date = CalendarDate(
            year=gregorian_year,
            month=month,
            day=day,
            calendar_type=CalendarType.GREGORIAN,
        )
        return GregorianCalendar().to_sdn(gregorian_date)

    def from_sdn(self, sdn: int) -> CalendarDate:
        """Convert SDN to Hebrew date."""
        # Simplified reverse conversion
        gregorian_date = GregorianCalendar().from_sdn(sdn)
        if gregorian_date.year is None:
            raise SDNConversionError(
                "Failed to convert SDN to Gregorian date for Hebrew conversion."
            )
        hebrew_year = gregorian_date.year + 3761

        if gregorian_date.month is None or gregorian_date.day is None:
            raise SDNConversionError(
                "Failed to convert SDN to Gregorian date for Hebrew conversion."
            )
        return CalendarDate(
            year=hebrew_year,
            month=gregorian_date.month,
            day=gregorian_date.day,
            calendar_type=CalendarType.HEBREW,
        )


class CalendarConverter:
    """Main interface for calendar system conversions."""

    def __init__(self) -> None:
        """Initialize calendar converter with all supported systems."""
        self._systems = {
            CalendarType.GREGORIAN: GregorianCalendar(),
            CalendarType.JULIAN: JulianCalendar(),
            CalendarType.FRENCH: FrenchCalendar(),
            CalendarType.HEBREW: HebrewCalendar(),
        }

    def get_system(self, calendar_type: CalendarType) -> CalendarSystem:
        """Get calendar system by type."""
        return self._systems[calendar_type]

    def convert(
        self, cal_date: CalendarDate, target_type: CalendarType
    ) -> CalendarDate:
        """
        Convert a date between calendar systems.

        Args:
            cal_date: Source date
            target_type: Target calendar system

        Returns:
            Date converted to target calendar system
        """
        source_system = self.get_system(cal_date.calendar_type)
        target_system = self.get_system(target_type)
        return source_system.convert_to(cal_date, target_system)

    def detect_calendar_type(self, cal_date: CalendarDate) -> CalendarType:
        """
        Detect the most likely calendar type based on date characteristics.

        Args:
            cal_date: Date to analyze

        Returns:
            Most likely calendar type
        """
        # Simple heuristic-based detection
        if cal_date.calendar_type != CalendarType.GREGORIAN:
            return cal_date.calendar_type

        if cal_date.year and cal_date.year > 5000:
            return CalendarType.HEBREW
        elif cal_date.year and 1792 <= cal_date.year <= 1805:
            return CalendarType.FRENCH
        elif cal_date.year and cal_date.year < 1582:
            return CalendarType.JULIAN
        else:
            return CalendarType.GREGORIAN
