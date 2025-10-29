"""
Tests for input validation module
"""

import pytest
from pydantic import ValidationError

from geneweb.api.security.validation import (
    EmailModel,
    InputValidator,
    PersonNameModel,
    SecureBaseModel,
    URLModel,
    validate_request_data,
)


class TestInputValidator:
    """Test InputValidator class"""

    def test_is_safe_input_valid_string(self):
        """Test is_safe_input with valid input"""
        assert InputValidator.is_safe_input("John Doe") is True
        assert InputValidator.is_safe_input("test@example.com") is True
        assert InputValidator.is_safe_input("123 Main Street") is True

    def test_is_safe_input_sql_injection(self):
        """Test is_safe_input detects SQL injection"""
        assert InputValidator.is_safe_input("'; DROP TABLE users--") is False
        assert InputValidator.is_safe_input("1' OR '1'='1") is False
        assert InputValidator.is_safe_input("SELECT * FROM users") is False
        assert InputValidator.is_safe_input("UNION SELECT password") is False

    def test_is_safe_input_xss_attack(self):
        """Test is_safe_input detects XSS attacks"""
        assert InputValidator.is_safe_input("<script>alert('XSS')</script>") is False
        assert InputValidator.is_safe_input("javascript:alert(1)") is False
        assert InputValidator.is_safe_input("<iframe src='evil.com'>") is False
        assert InputValidator.is_safe_input("onclick=alert(1)") is False

    def test_is_safe_input_command_injection(self):
        """Test is_safe_input detects command injection"""
        assert InputValidator.is_safe_input("test; rm -rf /") is False
        assert InputValidator.is_safe_input("test && malicious") is False
        assert InputValidator.is_safe_input("test | cat /etc/passwd") is False

    def test_is_safe_input_path_traversal(self):
        """Test is_safe_input detects path traversal"""
        assert InputValidator.is_safe_input("../../../etc/passwd") is False
        assert InputValidator.is_safe_input("..\\..\\windows\\system32") is False
        assert InputValidator.is_safe_input("%2e%2e%2f") is False

    def test_is_safe_input_max_length(self):
        """Test is_safe_input respects max length"""
        long_string = "a" * 1001
        assert InputValidator.is_safe_input(long_string, max_length=1000) is False

        # Should pass with higher limit
        assert InputValidator.is_safe_input(long_string, max_length=2000) is True

    def test_is_safe_input_non_string(self):
        """Test is_safe_input with non-string input"""
        assert InputValidator.is_safe_input(123) is False
        assert InputValidator.is_safe_input(None) is False
        assert InputValidator.is_safe_input([]) is False

    def test_sanitize_string(self):
        """Test string sanitization"""
        result = InputValidator.sanitize_string("Hello World")
        assert result == "Hello World"

    def test_sanitize_string_removes_dangerous_chars(self):
        """Test sanitization removes dangerous characters"""
        result = InputValidator.sanitize_string("<script>alert('test')</script>")
        assert "<" not in result
        assert ">" not in result
        assert '"' not in result

    def test_sanitize_string_truncates_long_input(self):
        """Test sanitization truncates long strings"""
        long_string = "a" * 2000
        result = InputValidator.sanitize_string(long_string, max_length=100)
        assert len(result) == 100

    def test_sanitize_string_removes_control_chars(self):
        """Test sanitization removes control characters"""
        text_with_control = "Hello\x00\x01\x02World"
        result = InputValidator.sanitize_string(text_with_control)
        assert "\x00" not in result
        assert "\x01" not in result
        assert result == "HelloWorld"

    def test_sanitize_string_preserves_whitespace(self):
        """Test sanitization preserves normal whitespace"""
        text = "Hello\nWorld\t!"
        result = InputValidator.sanitize_string(text)
        assert "\n" in result
        assert "\t" in result

    def test_sanitize_string_strips_whitespace(self):
        """Test sanitization strips leading/trailing whitespace"""
        text = "  Hello World  "
        result = InputValidator.sanitize_string(text)
        assert result == "Hello World"

    def test_sanitize_string_non_string_raises_error(self):
        """Test sanitization raises error for non-string"""
        with pytest.raises(ValueError, match="Value must be a string"):
            InputValidator.sanitize_string(123)

    def test_validate_email_valid(self):
        """Test email validation with valid emails"""
        assert InputValidator.validate_email("user@example.com") is True
        assert InputValidator.validate_email("test.user@domain.co.uk") is True
        assert InputValidator.validate_email("user+tag@example.com") is True

    def test_validate_email_invalid(self):
        """Test email validation with invalid emails"""
        assert InputValidator.validate_email("not_an_email") is False
        assert InputValidator.validate_email("@example.com") is False
        assert InputValidator.validate_email("user@") is False
        assert InputValidator.validate_email("user @example.com") is False

    def test_validate_email_too_long(self):
        """Test email validation rejects too long emails"""
        long_email = "a" * 250 + "@test.com"
        assert InputValidator.validate_email(long_email) is False

    def test_validate_ip_address_ipv4(self):
        """Test IP validation with IPv4 addresses"""
        assert InputValidator.validate_ip_address("192.168.1.1") is True
        assert InputValidator.validate_ip_address("127.0.0.1") is True
        assert InputValidator.validate_ip_address("8.8.8.8") is True

    def test_validate_ip_address_ipv6(self):
        """Test IP validation with IPv6 addresses"""
        assert InputValidator.validate_ip_address("::1") is True
        assert InputValidator.validate_ip_address("2001:0db8::1") is True

    def test_validate_ip_address_invalid(self):
        """Test IP validation with invalid addresses"""
        # These should return False, not raise exceptions
        assert InputValidator.validate_ip_address("not_an_ip") is False
        assert InputValidator.validate_ip_address("192.168.1") is False

        # Test with clearly invalid IP
        try:
            result = InputValidator.validate_ip_address("999.999.999.999")
            assert result is False
        except ValueError:
            # If it raises ValueError, that's also acceptable
            pass

    def test_validate_domain_valid(self):
        """Test domain validation with valid domains"""
        assert InputValidator.validate_domain("example.com") is True
        assert InputValidator.validate_domain("sub.example.com") is True
        assert InputValidator.validate_domain("test-domain.co.uk") is True

    def test_validate_domain_invalid(self):
        """Test domain validation with invalid domains"""
        assert InputValidator.validate_domain("-invalid.com") is False
        assert InputValidator.validate_domain("invalid-.com") is False
        assert InputValidator.validate_domain("invalid..com") is False

    def test_validate_domain_too_long(self):
        """Test domain validation rejects too long domains"""
        long_domain = "a" * 250 + ".com"
        assert InputValidator.validate_domain(long_domain) is False

    def test_validate_filename_valid(self):
        """Test filename validation with valid names"""
        assert InputValidator.validate_filename("document.txt") is True
        assert InputValidator.validate_filename("my-file.pdf") is True
        assert InputValidator.validate_filename("file_name.jpg") is True

    def test_validate_filename_invalid_chars(self):
        """Test filename validation rejects dangerous chars"""
        assert InputValidator.validate_filename("file<>.txt") is False
        assert InputValidator.validate_filename("file:name.txt") is False
        assert InputValidator.validate_filename("file\\path.txt") is False
        assert InputValidator.validate_filename("file/path.txt") is False

    def test_validate_filename_reserved_names(self):
        """Test filename validation rejects Windows reserved names"""
        assert InputValidator.validate_filename("CON") is False
        assert InputValidator.validate_filename("PRN.txt") is False
        assert InputValidator.validate_filename("AUX.pdf") is False
        assert InputValidator.validate_filename("NUL") is False
        assert InputValidator.validate_filename("COM1.txt") is False
        assert InputValidator.validate_filename("LPT1.doc") is False

    def test_validate_filename_empty(self):
        """Test filename validation rejects empty names"""
        assert InputValidator.validate_filename("") is False
        assert InputValidator.validate_filename(None) is False

    def test_validate_filename_too_long(self):
        """Test filename validation rejects too long names"""
        long_name = "a" * 256 + ".txt"
        assert InputValidator.validate_filename(long_name) is False


class TestSecureBaseModel:
    """Test SecureBaseModel validation"""

    def test_secure_base_model_valid_data(self):
        """Test SecureBaseModel accepts valid data"""

        class TestModel(SecureBaseModel):
            name: str
            value: int

        model = TestModel(name="test", value=123)
        assert model.name == "test"
        assert model.value == 123

    def test_secure_base_model_rejects_dangerous_input(self):
        """Test SecureBaseModel rejects dangerous input"""

        class TestModel(SecureBaseModel):
            name: str

        with pytest.raises(ValidationError):
            TestModel(name="<script>alert('XSS')</script>")

    def test_secure_base_model_rejects_too_long_input(self):
        """Test SecureBaseModel rejects too long strings"""

        class TestModel(SecureBaseModel):
            name: str

        long_string = "a" * 1001
        with pytest.raises(ValidationError):
            TestModel(name=long_string)

    def test_secure_base_model_forbids_extra_fields(self):
        """Test SecureBaseModel forbids extra fields"""

        class TestModel(SecureBaseModel):
            name: str

        with pytest.raises(ValidationError):
            TestModel(name="test", extra_field="not allowed")


class TestPersonNameModel:
    """Test PersonNameModel validation"""

    def test_person_name_model_valid(self):
        """Test PersonNameModel with valid names"""
        model = PersonNameModel(first_name="John", last_name="Doe")
        assert model.first_name == "John"
        assert model.last_name == "Doe"

    def test_person_name_model_with_middle_names(self):
        """Test PersonNameModel with middle names"""
        model = PersonNameModel(
            first_name="John", last_name="Doe", middle_names="William James"
        )
        assert model.middle_names == "William James"

    def test_person_name_model_accepts_accented_chars(self):
        """Test PersonNameModel accepts accented characters"""
        model = PersonNameModel(first_name="François", last_name="Müller")
        assert model.first_name == "François"
        assert model.last_name == "Müller"

    def test_person_name_model_accepts_hyphens(self):
        """Test PersonNameModel accepts hyphens"""
        model = PersonNameModel(first_name="Mary-Jane", last_name="Smith-Jones")
        assert model.first_name == "Mary-Jane"
        assert model.last_name == "Smith-Jones"

    def test_person_name_model_rejects_numbers(self):
        """Test PersonNameModel rejects numbers in names"""
        with pytest.raises(ValidationError):
            PersonNameModel(first_name="John123", last_name="Doe")

    def test_person_name_model_rejects_special_chars(self):
        """Test PersonNameModel rejects special characters"""
        with pytest.raises(ValidationError):
            PersonNameModel(first_name="John@", last_name="Doe")

    def test_person_name_model_min_length(self):
        """Test PersonNameModel enforces minimum length"""
        with pytest.raises(ValidationError):
            PersonNameModel(first_name="", last_name="Doe")


class TestEmailModel:
    """Test EmailModel validation"""

    def test_email_model_valid(self):
        """Test EmailModel with valid email"""
        model = EmailModel(email="user@example.com")
        assert model.email == "user@example.com"

    def test_email_model_converts_to_lowercase(self):
        """Test EmailModel converts email to lowercase"""
        model = EmailModel(email="User@EXAMPLE.COM")
        assert model.email == "user@example.com"

    def test_email_model_invalid_format(self):
        """Test EmailModel rejects invalid email"""
        with pytest.raises(ValidationError):
            EmailModel(email="not_an_email")


class TestURLModel:
    """Test URLModel validation"""

    def test_url_model_valid_http(self):
        """Test URLModel with valid HTTP URL"""
        model = URLModel(url="http://example.com")
        assert model.url == "http://example.com"

    def test_url_model_valid_https(self):
        """Test URLModel with valid HTTPS URL"""
        model = URLModel(url="https://secure.example.com/path")
        assert model.url == "https://secure.example.com/path"

    def test_url_model_invalid_scheme(self):
        """Test URLModel rejects invalid schemes"""
        with pytest.raises(ValidationError):
            URLModel(url="javascript:alert(1)")

        with pytest.raises(ValidationError):
            URLModel(url="file:///etc/passwd")


class TestValidateRequestData:
    """Test validate_request_data function"""

    def test_validate_request_data_simple(self):
        """Test validating simple request data"""
        data = {"name": "John", "age": 30}
        result = validate_request_data(data)

        assert result["name"] == "John"
        assert result["age"] == 30

    def test_validate_request_data_sanitizes_strings(self):
        """Test validation sanitizes string values"""
        data = {"name": "  John  ", "description": "Test<>"}
        result = validate_request_data(data)

        assert result["name"] == "John"
        assert "<" not in result["description"]
        assert ">" not in result["description"]

    def test_validate_request_data_nested_dict(self):
        """Test validation with nested dictionaries"""
        data = {"user": {"name": "John", "email": "john@example.com"}}
        result = validate_request_data(data)

        assert result["user"]["name"] == "John"
        assert result["user"]["email"] == "john@example.com"

    def test_validate_request_data_with_list(self):
        """Test validation with lists"""
        data = {"tags": ["tag1", "tag2", "tag3"]}
        result = validate_request_data(data)

        assert result["tags"] == ["tag1", "tag2", "tag3"]

    def test_validate_request_data_list_with_dicts(self):
        """Test validation with list of dictionaries"""
        data = {"items": [{"name": "item1"}, {"name": "item2"}]}
        result = validate_request_data(data)

        assert len(result["items"]) == 2
        assert result["items"][0]["name"] == "item1"

    def test_validate_request_data_invalid_field_name(self):
        """Test validation rejects invalid field names"""
        data = {"invalid-field": "value"}

        with pytest.raises(ValueError, match="Invalid field name"):
            validate_request_data(data)

    def test_validate_request_data_dangerous_content(self):
        """Test validation rejects dangerous content"""
        data = {"script": "<script>alert('XSS')</script>"}

        with pytest.raises(ValueError, match="dangerous content"):
            validate_request_data(data)

    def test_validate_request_data_preserves_numbers(self):
        """Test validation preserves numeric types"""
        data = {"int_val": 42, "float_val": 3.14, "bool_val": True}
        result = validate_request_data(data)

        assert result["int_val"] == 42
        assert result["float_val"] == 3.14
        assert result["bool_val"] is True


class TestPatternCaching:
    """Test regex pattern compilation caching"""

    def test_patterns_are_compiled_once(self):
        """Test that patterns are compiled and cached"""
        # First call compiles patterns
        InputValidator._compiled_patterns = None
        patterns1 = InputValidator._get_patterns()

        # Second call returns cached patterns
        patterns2 = InputValidator._get_patterns()

        assert patterns1 is patterns2
        assert len(patterns1) > 0
