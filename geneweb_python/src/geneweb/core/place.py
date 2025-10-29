"""Place module for handling geographical locations in genealogical records.

This module provides functionality for normalizing place names, extracting suburbs,
and comparing places for sorting in genealogical applications.
"""

import re
from dataclasses import dataclass
from typing import Tuple


@dataclass
class Place:
    """Represents a geographical place with optional suburb information.

    Attributes:
        name: The full place name as originally provided
        suburb: The suburb/district part if present
        main_place: The main place name without suburb
    """

    name: str
    suburb: str = ""
    main_place: str = ""

    def __post_init__(self):
        """Parse the place name to extract suburb and main place components."""
        if not self.suburb and not self.main_place:
            # Parse the name to extract components
            self.suburb, self.main_place = self.split_place(self.name)

    @staticmethod
    def split_place(place: str) -> Tuple[str, str]:
        """Split a place string into suburb and main place components.

        Handles various dash types:
        - Regular dash "-" (U+002D)
        - Em-dash "–" (U+2013)
        - En-dash "—" (U+2014)

        Args:
            place: Place string potentially containing "[suburb] - main_place" format

        Returns:
            Tuple of (suburb, main_place). If no suburb found, returns ("", place)
        """
        if not place:
            return ("", "")

        # Pattern to match [suburb] followed by space, dash (various types), space
        # Using character class for different dash types: hyphen-minus, en-dash, em-dash
        pattern = r"^\[([^\]]*)\]\s*[-–—]\s*(.+)$"
        match = re.match(pattern, place)

        if match:
            suburb = match.group(1)
            main_place = match.group(2)
            return (suburb, main_place)

        # No suburb found - return empty suburb and original place
        return ("", place)

    def normalize(self) -> str:
        """Normalize place name by standardizing format.

        Converts "[suburb] - main place" format to "suburb, main place".
        Only applies transformation if the pattern exactly matches.

        Returns:
            Normalized place string
        """
        # Pattern to match [suburb] - main_place format
        pattern = r"^\[([^\]]*)\] - (.+)$"
        match = re.match(pattern, self.name)

        if match:
            suburb = match.group(1)
            main_place = match.group(2)
            return f"{suburb}, {main_place}"

        # Return unchanged if pattern doesn't match
        return self.name

    def get_suburb(self) -> str:
        """Get the suburb part of the place.

        Returns:
            The suburb part if found, empty string otherwise
        """
        return self.suburb

    def get_main_place(self) -> str:
        """Get the main place without the suburb part.

        Returns:
            The main place part (without suburb)
        """
        return self.main_place

    def compare_to(self, other: "Place") -> int:
        """Compare this place to another for sorting purposes.

        For genealogical applications, places with suburbs should be sorted
        by their main place name, with suburbs coming before the same place
        without suburb.

        Args:
            other: Another Place instance to compare with

        Returns:
            -1 if self < other, 0 if equal, 1 if self > other
        """
        # If main places are different, compare them
        if self.main_place != other.main_place:
            if self.main_place < other.main_place:
                return -1
            else:
                return 1

        # If main places are same, place with suburb comes first
        if self.suburb and not other.suburb:
            return -1  # Place with suburb comes first
        elif not self.suburb and other.suburb:
            return 1  # Place without suburb comes after
        elif self.suburb and other.suburb:
            # Both have suburbs, compare the suburbs
            if self.suburb < other.suburb:
                return -1
            elif self.suburb > other.suburb:
                return 1
            else:
                return 0
        else:
            # Neither has suburb, they are equal
            return 0

    def __str__(self) -> str:
        """Return the original place name."""
        return self.name

    def __lt__(self, other: "Place") -> bool:
        """Less than comparison for sorting."""
        return self.compare_to(other) < 0

    def __eq__(self, other: object) -> bool:
        """Check equality with another Place."""
        if not isinstance(other, Place):
            return NotImplemented
        return self.compare_to(other) == 0

    def __gt__(self, other: "Place") -> bool:
        """Greater than comparison for sorting."""
        return self.compare_to(other) > 0
