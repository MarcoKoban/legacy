"""
Secure logging configuration for Geneweb API
Filters sensitive data and provides structured logging
"""

import logging
import logging.handlers
import re
import sys
from typing import Any, Dict

import structlog

from ..config import settings


class SensitiveDataFilter(logging.Filter):
    """
    Filter to remove sensitive data from log records
    """

    def __init__(self):
        super().__init__()
        self.sensitive_patterns = [
            # Password patterns
            re.compile(r'("password"\s*:\s*")[^"]*(")', re.IGNORECASE),
            re.compile(r'("passwd"\s*:\s*")[^"]*(")', re.IGNORECASE),
            re.compile(r'("pwd"\s*:\s*")[^"]*(")', re.IGNORECASE),
            # Token patterns
            re.compile(r'("token"\s*:\s*")[^"]*(")', re.IGNORECASE),
            re.compile(r'("access_token"\s*:\s*")[^"]*(")', re.IGNORECASE),
            re.compile(r'("refresh_token"\s*:\s*")[^"]*(")', re.IGNORECASE),
            re.compile(r'("bearer"\s*:\s*")[^"]*(")', re.IGNORECASE),
            # API Key patterns
            re.compile(r'("api_key"\s*:\s*")[^"]*(")', re.IGNORECASE),
            re.compile(r'("apikey"\s*:\s*")[^"]*(")', re.IGNORECASE),
            re.compile(r'("key"\s*:\s*")[^"]*(")', re.IGNORECASE),
            # Secret patterns
            re.compile(r'("secret"\s*:\s*")[^"]*(")', re.IGNORECASE),
            re.compile(r'("client_secret"\s*:\s*")[^"]*(")', re.IGNORECASE),
            # Authorization header
            re.compile(r'("authorization"\s*:\s*")[^"]*(")', re.IGNORECASE),
            # Email patterns (PII)
            re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
            # Credit card patterns
            re.compile(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"),
            # SSN patterns
            re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
        ]

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter sensitive data from log record
        """
        if hasattr(record, "getMessage"):
            message = record.getMessage()

            # Apply filters to message
            for pattern in self.sensitive_patterns:
                if pattern.groups >= 2:
                    # Replace with masked value, keeping structure
                    message = pattern.sub(r"\1***MASKED***\2", message)
                else:
                    # Simple replacement
                    message = pattern.sub("***MASKED***", message)

            # Update the record message
            record.msg = message
            record.args = ()

        # Filter sensitive data from extra fields
        if hasattr(record, "__dict__"):
            for key, value in record.__dict__.items():
                if any(
                    sensitive in key.lower()
                    for sensitive in settings.logging.sensitive_fields
                ):
                    setattr(record, key, "***MASKED***")
                elif isinstance(value, str):
                    for pattern in self.sensitive_patterns:
                        if pattern.search(value):
                            setattr(record, key, "***MASKED***")

        return True


class SecurityEventProcessor:
    """
    Processor for security-related events
    """

    def __call__(self, logger, name, event_dict):
        """
        Process security events and add metadata
        """
        # Add security context
        if "event" in event_dict:
            event_type = event_dict["event"]

            # Add security classification
            if event_type in [
                "login",
                "logout",
                "auth_failure",
                "rate_limit",
                "security_violation",
            ]:
                event_dict["security_event"] = True
                event_dict["priority"] = "high"

            # Add compliance tags
            if event_type in ["data_access", "data_modification", "admin_action"]:
                event_dict["compliance_relevant"] = True

        return event_dict


def setup_logging():
    """
    Configure structured logging with security features
    """
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            SecurityEventProcessor(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            (
                structlog.processors.JSONRenderer()
                if settings.logging.log_format == "json"
                else structlog.dev.ConsoleRenderer()
            ),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.logging.log_level.upper()),
    )

    # Add sensitive data filter to all handlers
    sensitive_filter = SensitiveDataFilter()

    # Configure root logger
    root_logger = logging.getLogger()

    # Remove default handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.addFilter(sensitive_filter)

    # File handler with rotation (if configured)
    if settings.logging.log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            settings.logging.log_file,
            maxBytes=settings.logging.log_max_size,
            backupCount=settings.logging.log_backup_count,
        )
        file_handler.addFilter(sensitive_filter)
        root_logger.addHandler(file_handler)

    root_logger.addHandler(console_handler)
    root_logger.setLevel(getattr(logging, settings.logging.log_level.upper()))

    # Configure specific loggers

    # FastAPI/Uvicorn loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)

    # Security logger
    security_logger = logging.getLogger("geneweb.security")
    security_logger.setLevel(logging.INFO)

    # API logger
    api_logger = logging.getLogger("geneweb.api")
    api_logger.setLevel(logging.INFO)

    # Database logger (set to WARNING to avoid query logging in production)
    if not settings.debug:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    return root_logger


def get_security_logger():
    """
    Get configured security logger
    """
    return structlog.get_logger("geneweb.security")


def get_api_logger():
    """
    Get configured API logger
    """
    return structlog.get_logger("geneweb.api")


def log_security_event(
    event_type: str, details: Dict[str, Any], request_info: Dict[str, Any] = None
):
    """
    Log security-related events with proper context
    """
    logger = get_security_logger()

    log_data = {
        "event": event_type,
        "timestamp": None,  # Will be added by TimeStamper
        **details,
    }

    if request_info:
        # Add request context (filtered for security)
        safe_request_info = {
            "method": request_info.get("method"),
            "path": request_info.get("path"),
            "user_agent": request_info.get("user_agent", "")[:100],  # Truncate
            "client_ip": request_info.get("client_ip"),
            "request_id": request_info.get("request_id"),
        }
        log_data["request"] = safe_request_info

    logger.info("Security event", **log_data)
