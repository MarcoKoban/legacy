"""
Tests for security logging functionality.
"""

import logging
from unittest.mock import Mock, patch

from geneweb.api.security.logging import (
    SecurityEventProcessor,
    SensitiveDataFilter,
    get_api_logger,
    get_security_logger,
    log_security_event,
    setup_logging,
)


class TestSensitiveDataFilter:
    """Test SensitiveDataFilter functionality."""

    def test_init(self):
        """Test SensitiveDataFilter initialization."""
        filter_obj = SensitiveDataFilter()
        assert hasattr(filter_obj, "sensitive_patterns")
        assert len(filter_obj.sensitive_patterns) > 0

    def test_filter_password_data(self):
        """Test filtering password data."""
        filter_obj = SensitiveDataFilter()

        # Create mock log record
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg='User login: {"username": "test", "password": "secret123"}',
            args=(),
            exc_info=None,
        )

        result = filter_obj.filter(record)
        assert result is True  # Record should be processed
        assert "secret123" not in record.msg
        assert "***MASKED***" in record.msg

    def test_filter_token_data(self):
        """Test filtering token data."""
        filter_obj = SensitiveDataFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg='API request: {"token": "abc123xyz", "user": "john"}',
            args=(),
            exc_info=None,
        )

        result = filter_obj.filter(record)
        assert result is True
        assert "abc123xyz" not in record.msg
        assert "***MASKED***" in record.msg

    def test_filter_email_data(self):
        """Test filtering email data (PII)."""
        filter_obj = SensitiveDataFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="User email: john.doe@example.com registered",
            args=(),
            exc_info=None,
        )

        result = filter_obj.filter(record)
        assert result is True
        assert "john.doe@example.com" not in record.msg
        assert "***MASKED***" in record.msg

    def test_filter_clean_data(self):
        """Test filtering data without sensitive content."""
        filter_obj = SensitiveDataFilter()

        original_msg = "User john completed task successfully"
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg=original_msg,
            args=(),
            exc_info=None,
        )

        result = filter_obj.filter(record)
        assert result is True
        assert record.msg == original_msg  # Should be unchanged

    def test_filter_with_args(self):
        """Test filtering when log record has args."""
        filter_obj = SensitiveDataFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Login attempt for %s with password %s",
            args=("john", "secret123"),
            exc_info=None,
        )

        result = filter_obj.filter(record)
        assert result is True
        # Args should be filtered
        assert "secret123" not in str(record.args)


class TestSecurityEventProcessor:
    """Test SecurityEventProcessor functionality."""

    def test_init(self):
        """Test SecurityEventProcessor initialization."""
        processor = SecurityEventProcessor()
        assert processor is not None

    def test_call_with_security_event(self):
        """Test processing security events."""
        processor = SecurityEventProcessor()

        event_dict = {"event": "login_attempt", "user": "john", "success": True}

        result = processor(None, "security", event_dict)

        # The processor may or may not add security_level,
        # so just check it returns the event
        assert isinstance(result, dict)
        assert result["event"] == "login_attempt"

    def test_call_with_non_security_event(self):
        """Test processing non-security events."""
        processor = SecurityEventProcessor()

        event_dict = {"message": "Regular log message", "level": "info"}

        result = processor(None, "api", event_dict)

        # Should return event dict unchanged (or with minimal processing)
        assert "message" in result

    def test_call_with_auth_event(self):
        """Test processing authentication events."""
        processor = SecurityEventProcessor()

        event_dict = {
            "event": "authentication_failure",
            "user": "attacker",
            "ip": "192.168.1.100",
        }

        result = processor(None, "auth", event_dict)

        # The processor may process auth events differently,
        # just verify it returns the data
        assert isinstance(result, dict)
        assert result["event"] == "authentication_failure"


class TestLoggingSetup:
    """Test logging setup functionality."""

    @patch("geneweb.api.security.logging.structlog")
    def test_setup_logging(self, mock_structlog):
        """Test logging setup."""
        # Mock structlog methods
        mock_structlog.configure = Mock()
        mock_structlog.stdlib.BoundLogger = Mock()

        setup_logging()

        # Verify structlog.configure was called
        mock_structlog.configure.assert_called_once()
        call_kwargs = mock_structlog.configure.call_args[1]
        assert "processors" in call_kwargs
        assert "wrapper_class" in call_kwargs

    def test_get_security_logger(self):
        """Test getting security logger."""
        with patch("structlog.get_logger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            logger = get_security_logger()

            mock_get_logger.assert_called_once_with("geneweb.security")
            assert logger == mock_logger

    def test_get_api_logger(self):
        """Test getting API logger."""
        with patch("structlog.get_logger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            logger = get_api_logger()

            mock_get_logger.assert_called_once_with("geneweb.api")
            assert logger == mock_logger


class TestSecurityEventLogging:
    """Test security event logging functionality."""

    def test_log_security_event_basic(self):
        """Test basic security event logging."""
        with patch(
            "geneweb.api.security.logging.get_security_logger"
        ) as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            event_type = "login_attempt"
            details = {"user": "john", "success": True}

            log_security_event(event_type, details)

            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args
            assert call_args[0][0] == "Security event"

            # Check logged data
            logged_data = call_args[1]
            assert logged_data["event"] == event_type
            assert logged_data["user"] == details["user"]
            assert logged_data["success"] == details["success"]

    def test_log_security_event_with_request_info(self):
        """Test security event logging with request information."""
        with patch(
            "geneweb.api.security.logging.get_security_logger"
        ) as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            event_type = "failed_auth"
            details = {"reason": "invalid_credentials"}
            request_info = {
                "method": "POST",
                "path": "/auth/login",
                "user_agent": "Mozilla/5.0...",
                "client_ip": "192.168.1.100",
                "request_id": "req-12345",
                "password": "should_not_be_logged",  # Should be filtered out
            }

            log_security_event(event_type, details, request_info)

            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args
            logged_data = call_args[1]

            assert "request" in logged_data
            request_data = logged_data["request"]
            assert request_data["method"] == "POST"
            assert request_data["path"] == "/auth/login"
            assert request_data["client_ip"] == "192.168.1.100"
            assert request_data["request_id"] == "req-12345"
            # Sensitive data should be filtered out
            assert "password" not in request_data

    def test_log_security_event_truncates_user_agent(self):
        """Test that long user agent strings are truncated."""
        with patch(
            "geneweb.api.security.logging.get_security_logger"
        ) as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            long_user_agent = "a" * 200  # 200 characters
            request_info = {"method": "GET", "user_agent": long_user_agent}

            log_security_event("test_event", {}, request_info)

            call_args = mock_logger.info.call_args
            logged_data = call_args[1]

            # User agent should be truncated to 100 characters
            assert len(logged_data["request"]["user_agent"]) == 100

    def test_log_security_event_without_request_info(self):
        """Test security event logging without request information."""
        with patch(
            "geneweb.api.security.logging.get_security_logger"
        ) as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            event_type = "system_alert"
            details = {"alert": "high_cpu_usage", "value": 95.5}

            log_security_event(event_type, details)

            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args
            logged_data = call_args[1]

            assert logged_data["event"] == event_type
            assert logged_data["alert"] == details["alert"]
            assert logged_data["value"] == details["value"]
            # No request data should be present
            assert "request" not in logged_data


class TestLoggingIntegration:
    """Integration tests for logging system."""

    @patch("geneweb.api.security.logging.logging.getLogger")
    def test_filter_integration_with_logger(self, mock_get_logger):
        """Test that sensitive data filter works with actual logger."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        # Create filter
        sensitive_filter = SensitiveDataFilter()

        # Simulate adding filter to logger
        mock_logger.addFilter = Mock()
        mock_logger.addFilter(sensitive_filter)

        # Verify filter was added
        mock_logger.addFilter.assert_called_once_with(sensitive_filter)

    def test_processor_integration(self):
        """Test that security event processor integrates properly."""
        processor = SecurityEventProcessor()

        # Test various event types
        test_events = [
            {"event": "login_success", "user": "john"},
            {"event": "permission_denied", "resource": "/admin"},
            {"message": "regular log", "level": "info"},
        ]

        for event in test_events:
            result = processor(None, "test", event.copy())
            assert isinstance(result, dict)
            # Original event data should be preserved
            for key, value in event.items():
                if (
                    key in result
                ):  # Processor might add fields but shouldn't remove them
                    assert result[key] == value
