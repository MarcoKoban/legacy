"""
Sosa genealogical numbering system implementation.

The Sosa numbering system (also known as Ahnentafel) is a genealogical
numbering system used to identify a person's ancestors. The system assigns
numbers as follows:
- The root person (proband) is assigned number 1
- For any person numbered n:
  - Their father is numbered 2n
  - Their mother is numbered 2n+1

This module provides a Python implementation compatible with the OCaml
Geneweb version.
"""

from dataclasses import dataclass


@dataclass(frozen=True, eq=True)
class Sosa:
    """
    Sosa genealogical number representation.

    This class represents a Sosa number used in genealogical trees
    to uniquely identify ancestors of a given person.

    Attributes:
        value: The integer value of the Sosa number
    """

    value: int

    def __post_init__(self) -> None:
        """Validate Sosa number constraints."""
        if self.value < 0:
            raise ValueError(f"Sosa number must be non-negative, got {self.value}")

    @classmethod
    def zero(cls) -> "Sosa":
        """
        Create Sosa number zero.

        Returns:
            Sosa object representing zero (used for invalid/null references)
        """
        return cls(0)

    @classmethod
    def one(cls) -> "Sosa":
        """
        Create Sosa number one.

        Returns:
            Sosa object representing one (the root person/proband)
        """
        return cls(1)

    @classmethod
    def from_int(cls, value: int) -> "Sosa":
        """
        Create Sosa number from integer.

        Args:
            value: Integer value for the Sosa number

        Returns:
            Sosa object with the given value

        Raises:
            ValueError: If value is negative
        """
        return cls(value)

    @classmethod
    def from_string(cls, value: str) -> "Sosa":
        """
        Create Sosa number from string.

        Args:
            value: String representation of the Sosa number

        Returns:
            Sosa object with the parsed value

        Raises:
            ValueError: If string cannot be parsed as integer or is negative
        """
        try:
            int_value = int(value.strip())
            return cls(int_value)
        except ValueError as e:
            raise ValueError(f"Cannot parse '{value}' as Sosa number") from e

    def divide_by(self, divisor: int) -> "Sosa":
        """
        Divide this Sosa number by an integer.

        Args:
            divisor: Integer to divide by

        Returns:
            New Sosa object with the division result

        Raises:
            ValueError: If divisor is zero
        """
        if divisor == 0:
            raise ValueError("Cannot divide by zero")

        result = self.value // divisor  # Integer division
        return Sosa(result)

    def format_with_separator(self, separator: str = ",") -> str:
        """
        Format the Sosa number with thousands separator.

        Args:
            separator: String to use as thousands separator (default: ",")

        Returns:
            Formatted string with thousands separators

        Examples:
            Sosa(1000).format_with_separator(",") -> "1,000"
            Sosa(1000000).format_with_separator(",") -> "1,000,000"
        """
        # Convert to string and reverse for easier processing
        num_str = str(self.value)

        # Handle negative numbers (though Sosa shouldn't be negative)
        if num_str.startswith("-"):
            sign = "-"
            num_str = num_str[1:]
        else:
            sign = ""

        # Add separators every 3 digits from the right
        if len(num_str) <= 3:
            return sign + num_str

        # Process groups of 3 digits from right to left
        groups = []
        for i in range(len(num_str), 0, -3):
            start = max(0, i - 3)
            groups.append(num_str[start:i])

        # Reverse the groups and join with separator
        groups.reverse()
        return sign + separator.join(groups)

    def __eq__(self, other: object) -> bool:
        """
        Test equality with another Sosa number.

        Args:
            other: Object to compare with

        Returns:
            True if both represent the same Sosa number, False otherwise
        """
        if not isinstance(other, Sosa):
            return False
        return self.value == other.value

    def __hash__(self) -> int:
        """Return hash value for use in sets and dictionaries."""
        return hash(self.value)

    def __repr__(self) -> str:
        """Return string representation for debugging."""
        return f"Sosa({self.value})"

    def __str__(self) -> str:
        """Return string representation for display."""
        return str(self.value)

    def generation(self) -> int:
        """
        Calculate the generation level of this Sosa number in the genealogical tree.

        In genealogical trees using Sosa numbering:
        - Generation 1: Sosa 1 (the proband/root person)
        - Generation 2: Sosa 2-3 (parents)
        - Generation 3: Sosa 4-7 (grandparents)
        - Generation 4: Sosa 8-15 (great-grandparents)
        - etc.

        Formula: generation = floor(log2(sosa_number)) + 1
        Special case: Sosa 0 returns generation 0 (no ancestor)

        Returns:
            Generation level (1-based for Sosa 1+, 0 for Sosa 0)

        Examples:
            >>> Sosa(1).generation()
            1
            >>> Sosa(2).generation()
            2
            >>> Sosa(4).generation()
            3
            >>> Sosa(8).generation()
            4
        """
        if self.value == 0:
            return 0

        # Pour Sosa >= 1, calcul basé sur log2
        import math

        return int(math.floor(math.log2(self.value))) + 1

    def branch_path(self) -> list[int]:
        """
        Calculate the branch path for navigating to this ancestor in the tree.

        The branch path represents the sequence of father/mother choices needed to reach
        this specific ancestor from the root person (Sosa 1). Each element in the path
        represents a navigation choice:
        - 0: go to father (even Sosa numbers in binary)
        - 1: go to mother (odd Sosa numbers in binary)

        Algorithm:
        1. Convert Sosa number to binary representation
        2. Remove the leftmost bit (which indicates the generation)
        3. The remaining bits form the navigation path from root to ancestor
        4. Read bits from left to right: each bit is a father(0)/mother(1) choice

        Returns:
            List of integers (0 or 1) representing the navigation path.
            Empty list for Sosa 1 (root) and Sosa 0 (invalid).

        Examples:
            >>> Sosa(1).branch_path()
            []
            >>> Sosa(2).branch_path()  # Father: binary 10 -> remove 1 -> [0]
            [0]
            >>> Sosa(3).branch_path()  # Mother: binary 11 -> remove 1 -> [1]
            [1]
            >>> Sosa(4).branch_path()  # Pat. grandfather: binary 100 -> [0,0]
            [0, 0]
            >>> Sosa(38).branch_path() # binary 100110 -> [0,0,1,1,0]
            [0, 0, 1, 1, 0]
        """
        # Special cases
        if self.value <= 1:
            return []

        # Convert to binary and remove '0b' prefix
        binary_str = bin(self.value)[2:]

        # Remove the leftmost bit (generation marker) to get the navigation path
        navigation_bits = binary_str[1:]

        # Convert each bit to integer: '0' -> 0 (father), '1' -> 1 (mother)
        return [int(bit) for bit in navigation_bits]

    def father_sosa(self) -> "Sosa":
        """
        Calculate the Sosa number of this person's father.

        In the Sosa system: father of person n is 2n

        Returns:
            Sosa number of the father

        Examples:
            >>> Sosa(1).father_sosa()
            Sosa(2)
            >>> Sosa(5).father_sosa()
            Sosa(10)
        """
        return Sosa(self.value * 2)

    def mother_sosa(self) -> "Sosa":
        """
        Calculate the Sosa number of this person's mother.

        In the Sosa system: mother of person n is 2n+1

        Returns:
            Sosa number of the mother

        Examples:
            >>> Sosa(1).mother_sosa()
            Sosa(3)
            >>> Sosa(5).mother_sosa()
            Sosa(11)
        """
        return Sosa(self.value * 2 + 1)

    def child_sosa(self) -> "Sosa":
        """
        Calculate the Sosa number of the child whose parent this represents.

        In the Sosa system: if parent is n, then child is n//2
        Only works if this is a parent Sosa (n >= 2)

        Returns:
            Sosa number of the child

        Raises:
            ValueError: If called on Sosa 0 or 1 (not valid parent Sosa numbers)

        Examples:
            >>> Sosa(2).child_sosa()  # Father -> child
            Sosa(1)
            >>> Sosa(3).child_sosa()  # Mother -> child
            Sosa(1)
            >>> Sosa(10).child_sosa()
            Sosa(5)
        """
        if self.value < 2:
            raise ValueError(f"Sosa {self.value} cannot have a child (must be >= 2)")
        return Sosa(self.value // 2)

    def is_father_sosa(self) -> bool:
        """
        Check if this Sosa number represents a father.

        In the Sosa system, fathers have even numbers (except 0)

        Returns:
            True if this represents a father position
        """
        return self.value > 0 and self.value % 2 == 0

    def is_mother_sosa(self) -> bool:
        """
        Check if this Sosa number represents a mother.

        In the Sosa system, mothers have odd numbers (except 1)

        Returns:
            True if this represents a mother position
        """
        return self.value > 1 and self.value % 2 == 1
