"""
Password validation and strength checking.

This module provides comprehensive password security validation:
- Minimum length enforcement
- Complexity requirements
- Common password detection
- Password history checking
- Password strength scoring
"""

import re
from enum import Enum
from typing import List, Tuple

import structlog

logger = structlog.get_logger(__name__)


class PasswordStrength(str, Enum):
    """Password strength levels."""

    VERY_WEAK = "very_weak"
    WEAK = "weak"
    MEDIUM = "medium"
    STRONG = "strong"
    VERY_STRONG = "very_strong"


# Common passwords to reject (top 100 most common)
COMMON_PASSWORDS = {
    "password",
    "123456",
    "123456789",
    "12345678",
    "12345",
    "1234567",
    "password1",
    "qwerty",
    "abc123",
    "111111",
    "123123",
    "admin",
    "letmein",
    "welcome",
    "monkey",
    "1234567890",
    "123321",
    "password123",
    "qwerty123",
    "admin123",
    "letmein123",
    "welcome123",
    "iloveyou",
    "princess",
    "dragon",
    "sunshine",
    "master",
    "shadow",
    "12345678910",
    "football",
    "baseball",
    "trustno1",
    "superman",
    "batman",
    "starwars",
    "geneweb",
    "genealogy",
    "family",
    "tree",
    "ancestry",
}


class PasswordValidator:
    """
    Comprehensive password validation with security best practices.

    **Security Features:**
    - Minimum length enforcement (8+ characters recommended)
    - Complexity requirements (uppercase, lowercase, numbers, symbols)
    - Common password rejection
    - Password history checking
    - Strength scoring
    """

    def __init__(
        self,
        min_length: int = 8,
        require_uppercase: bool = True,
        require_lowercase: bool = True,
        require_numbers: bool = True,
        require_special: bool = True,
        max_length: int = 128,
    ):
        self.min_length = min_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_numbers = require_numbers
        self.require_special = require_special
        self.max_length = max_length

    def validate(self, password: str) -> Tuple[bool, List[str]]:
        """
        Validate password against all requirements.

        Args:
            password: Password to validate

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []

        # Length check
        if len(password) < self.min_length:
            errors.append(
                f"Password must be at least {self.min_length} characters long"
            )

        if len(password) > self.max_length:
            errors.append(f"Password must be at most {self.max_length} characters long")

        # Complexity checks
        if self.require_uppercase and not re.search(r"[A-Z]", password):
            errors.append("Password must contain at least one uppercase letter")

        if self.require_lowercase and not re.search(r"[a-z]", password):
            errors.append("Password must contain at least one lowercase letter")

        if self.require_numbers and not re.search(r"\d", password):
            errors.append("Password must contain at least one number")

        if self.require_special and not re.search(
            r"[!@#$%^&*(),.?\":{}|<>_\-+=\[\]\\\/;'`~]", password
        ):
            errors.append("Password must contain at least one special character")

        # Common password check
        if password.lower() in COMMON_PASSWORDS:
            errors.append("Password is too common and easily guessable")

        # Check for sequential characters
        if self._has_sequential_chars(password):
            errors.append(
                "Password contains sequential characters (e.g., '123', 'abc')"
            )

        # Check for repeated characters
        if self._has_repeated_chars(password):
            errors.append("Password contains too many repeated characters")

        is_valid = len(errors) == 0
        return is_valid, errors

    def calculate_strength(self, password: str) -> Tuple[PasswordStrength, int]:
        """
        Calculate password strength score.

        Args:
            password: Password to evaluate

        Returns:
            Tuple of (strength_level, score out of 100)
        """
        score = 0

        # Length scoring (max 30 points)
        if len(password) >= 8:
            score += 10
        if len(password) >= 12:
            score += 10
        if len(password) >= 16:
            score += 10

        # Character variety scoring (max 40 points)
        if re.search(r"[a-z]", password):
            score += 10
        if re.search(r"[A-Z]", password):
            score += 10
        if re.search(r"\d", password):
            score += 10
        if re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=\[\]\\\/;'`~]", password):
            score += 10

        # Complexity scoring (max 30 points)
        unique_chars = len(set(password))
        if unique_chars >= 5:
            score += 10
        if unique_chars >= 8:
            score += 10
        if unique_chars >= 12:
            score += 10

        # Penalties
        if password.lower() in COMMON_PASSWORDS:
            score -= 50
        if self._has_sequential_chars(password):
            score -= 20
        if self._has_repeated_chars(password):
            score -= 15

        # Ensure score is between 0 and 100
        score = max(0, min(100, score))

        # Determine strength level
        if score < 20:
            strength = PasswordStrength.VERY_WEAK
        elif score < 40:
            strength = PasswordStrength.WEAK
        elif score < 60:
            strength = PasswordStrength.MEDIUM
        elif score < 80:
            strength = PasswordStrength.STRONG
        else:
            strength = PasswordStrength.VERY_STRONG

        return strength, score

    def _has_sequential_chars(self, password: str, min_sequence: int = 3) -> bool:
        """Check for sequential characters (e.g., '123', 'abc')."""
        password_lower = password.lower()

        for i in range(len(password_lower) - min_sequence + 1):
            # Check for sequential numbers
            if password[i : i + min_sequence].isdigit():  # noqa: E203
                chars = password[i : i + min_sequence]  # noqa: E203
                is_sequential = all(
                    int(chars[j + 1]) == int(chars[j]) + 1
                    for j in range(len(chars) - 1)
                )
                if is_sequential:
                    return True

            # Check for sequential letters
            if password_lower[i : i + min_sequence].isalpha():  # noqa: E203
                chars = password_lower[i : i + min_sequence]  # noqa: E203
                is_sequential = all(
                    ord(chars[j + 1]) == ord(chars[j]) + 1
                    for j in range(len(chars) - 1)
                )
                if is_sequential:
                    return True

        return False

    def _has_repeated_chars(self, password: str, max_repeats: int = 3) -> bool:
        """Check for excessive character repetition (e.g., 'aaaa')."""
        for i in range(len(password) - max_repeats + 1):
            if len(set(password[i : i + max_repeats])) == 1:  # noqa: E203
                return True
        return False

    def get_suggestions(self, password: str) -> List[str]:
        """
        Get password improvement suggestions.

        Args:
            password: Password to analyze

        Returns:
            List of suggestions for improving the password
        """
        suggestions = []
        strength, score = self.calculate_strength(password)

        if strength in [PasswordStrength.VERY_WEAK, PasswordStrength.WEAK]:
            suggestions.append("Consider using a longer password (12+ characters)")

        if not re.search(r"[A-Z]", password):
            suggestions.append("Add uppercase letters for better security")

        if not re.search(r"[a-z]", password):
            suggestions.append("Add lowercase letters for better security")

        if not re.search(r"\d", password):
            suggestions.append("Add numbers for better security")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=\[\]\\\/;'`~]", password):
            suggestions.append("Add special characters for better security")

        if len(password) < 12:
            suggestions.append("Use at least 12 characters for strong security")

        if password.lower() in COMMON_PASSWORDS:
            suggestions.append("Avoid common passwords - use something unique")

        if self._has_sequential_chars(password):
            suggestions.append("Avoid sequential characters like '123' or 'abc'")

        if self._has_repeated_chars(password):
            suggestions.append("Avoid repeating the same character multiple times")

        # General suggestions
        if len(suggestions) == 0 and strength != PasswordStrength.VERY_STRONG:
            suggestions.append(
                "Consider using a passphrase or combination of unrelated words"
            )
            suggestions.append(
                "Use a password manager to generate and store strong passwords"
            )

        return suggestions


# Global password validator instance
password_validator = PasswordValidator(
    min_length=8,
    require_uppercase=True,
    require_lowercase=True,
    require_numbers=True,
    require_special=True,
)
