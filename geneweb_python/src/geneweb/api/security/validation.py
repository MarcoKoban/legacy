"""
Input validation for Geneweb API
Provides global input validation and sanitization
"""

import re
from ipaddress import AddressValueError, ip_address
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class InputValidator:
    """
    Global input validator for security
    """

    # Dangerous patterns to block
    DANGEROUS_PATTERNS = [
        # SQL Injection patterns
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
        r"([\';\"]\s*(\b(OR|AND)\b\s+[\'\"]?\d+[\'\"]?\s*=\s*[\'\"]?\d+[\'\"]?))",
        r"(UNION\s+SELECT)",
        r"(--|\#|/\*)",
        # XSS patterns
        r"(<script[^>]*>.*?</script>)",
        r"(javascript:)",
        r"(on\w+\s*=)",
        r"(<iframe[^>]*>)",
        r"(<object[^>]*>)",
        r"(<embed[^>]*>)",
        # Command injection patterns
        r"(\b(exec|eval|system|shell_exec|passthru|proc_open|popen)\b)",
        r"(\||\&\&|\|\|)",
        r"(;\s*(rm|del|format|shutdown|reboot))",
        # Path traversal patterns
        r"(\.\.\/|\.\.\\)",
        r"(%2e%2e%2f|%2e%2e%5c)",
        # LDAP injection patterns
        r"(\(\s*\|\s*\()",
        r"(\)\s*\(\s*\|)",
    ]

    # Compiled regex patterns for efficiency
    _compiled_patterns = None

    @classmethod
    def _get_patterns(cls):
        """Get compiled regex patterns"""
        if cls._compiled_patterns is None:
            cls._compiled_patterns = [
                re.compile(pattern, re.IGNORECASE | re.MULTILINE)
                for pattern in cls.DANGEROUS_PATTERNS
            ]
        return cls._compiled_patterns

    @classmethod
    def is_safe_input(cls, value: str, max_length: int = 1000) -> bool:
        """
        Check if input is safe from common injection attacks
        """
        if not isinstance(value, str):
            return False

        # Check length
        if len(value) > max_length:
            return False

        # Check for dangerous patterns
        patterns = cls._get_patterns()
        for pattern in patterns:
            if pattern.search(value):
                return False

        return True

    @classmethod
    def sanitize_string(cls, value: str, max_length: int = 1000) -> str:
        """
        Sanitize string input
        """
        if not isinstance(value, str):
            raise ValueError("Value must be a string")

        # Truncate if too long
        if len(value) > max_length:
            value = value[:max_length]

        # Remove dangerous characters
        value = re.sub(r'[<>"\']', "", value)

        # Remove control characters except common whitespace
        value = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", value)

        return value.strip()

    @classmethod
    def validate_email(cls, email: str) -> bool:
        """
        Validate email format
        """
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email)) and len(email) <= 254

    @classmethod
    def validate_ip_address(cls, ip: str) -> bool:
        """
        Validate IP address format
        """
        try:
            ip_address(ip)
            return True
        except (AddressValueError, ValueError):
            return False

    @classmethod
    def validate_domain(cls, domain: str) -> bool:
        """
        Validate domain name format
        """
        pattern = (
            r"^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?"
            r"(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$"
        )
        return bool(re.match(pattern, domain)) and len(domain) <= 253

    @classmethod
    def validate_filename(cls, filename: str) -> bool:
        """
        Validate filename for safe file operations
        """
        if not filename or len(filename) > 255:
            return False

        # Check for dangerous patterns
        dangerous_chars = r'[<>:"/\\|?*\x00-\x1f]'
        if re.search(dangerous_chars, filename):
            return False

        # Check for reserved names (Windows)
        reserved_names = {
            "CON",
            "PRN",
            "AUX",
            "NUL",
            "COM1",
            "COM2",
            "COM3",
            "COM4",
            "COM5",
            "COM6",
            "COM7",
            "COM8",
            "COM9",
            "LPT1",
            "LPT2",
            "LPT3",
            "LPT4",
            "LPT5",
            "LPT6",
            "LPT7",
            "LPT8",
            "LPT9",
        }

        base_name = filename.split(".")[0].upper()
        if base_name in reserved_names:
            return False

        return True


class SecureBaseModel(BaseModel):
    """
    Base model with security validation
    """

    @model_validator(mode="before")
    @classmethod
    def validate_string_fields(cls, values):
        """
        Validate all string fields for security
        """
        if isinstance(values, dict):
            for field_name, v in values.items():
                if isinstance(v, str):
                    if not InputValidator.is_safe_input(v):
                        raise ValueError(
                            f"Field {field_name} contains potentially dangerous content"
                        )

                    # Basic max length check
                    if len(v) > 1000:  # Default max length
                        raise ValueError(
                            f"Field {field_name} exceeds maximum length of 1000"
                        )
        return values

    model_config = ConfigDict(
        # Prevent extra fields
        extra="forbid",
        # Validate assignment
        validate_assignment=True,
        # Use enum values
        use_enum_values=True,
    )


class PersonNameModel(SecureBaseModel):
    """
    Secure model for person names
    """

    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    middle_names: Optional[str] = Field(None, max_length=200)

    @field_validator("first_name", "last_name", "middle_names")
    @classmethod
    def validate_name_format(cls, v):
        """Validate name contains only allowed characters"""
        if v and not re.match(r"^[a-zA-ZÀ-ÿ\s\-\'\.]+$", v):
            raise ValueError("Name contains invalid characters")
        return v


class EmailModel(SecureBaseModel):
    """
    Secure model for email addresses
    """

    email: str = Field(..., max_length=254)

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v):
        """Validate email format"""
        if not InputValidator.validate_email(v):
            raise ValueError("Invalid email format")
        return v.lower()


class URLModel(SecureBaseModel):
    """
    Secure model for URLs
    """

    url: str = Field(..., max_length=2048)

    @field_validator("url")
    @classmethod
    def validate_url_format(cls, v):
        """Validate URL format and scheme"""
        import urllib.parse

        try:
            parsed = urllib.parse.urlparse(v)

            # Only allow safe schemes
            if parsed.scheme not in ["http", "https", "ftp", "ftps"]:
                raise ValueError("URL scheme not allowed")

            # Validate domain
            if parsed.netloc and not InputValidator.validate_domain(
                parsed.netloc.split(":")[0]
            ):
                raise ValueError("Invalid domain in URL")

        except Exception:
            raise ValueError("Invalid URL format")

        return v


# Input validation middleware function
def validate_request_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate request data for security issues
    """
    validated_data = {}

    for key, value in data.items():
        # Validate key name
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", key):
            raise ValueError(f"Invalid field name: {key}")

        # Validate value
        if isinstance(value, str):
            if not InputValidator.is_safe_input(value):
                raise ValueError(f"Field {key} contains potentially dangerous content")
            validated_data[key] = InputValidator.sanitize_string(value)
        elif isinstance(value, (int, float, bool)):
            validated_data[key] = value
        elif isinstance(value, dict):
            validated_data[key] = validate_request_data(value)
        elif isinstance(value, list):
            validated_data[key] = [
                (
                    validate_request_data(item)
                    if isinstance(item, dict)
                    else (
                        InputValidator.sanitize_string(item)
                        if isinstance(item, str)
                        else item
                    )
                )
                for item in value
            ]
        else:
            validated_data[key] = value

    return validated_data
