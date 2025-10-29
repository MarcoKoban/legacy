"""Configuration management for Geneweb API using environment variables."""

from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class SecuritySettings(BaseSettings):
    """Security configuration from environment variables."""

    secret_key: str = Field(default="dev-secret-key", description="JWT secret key")
    encryption_key: str = Field(
        default="dev-encryption-key", description="Data encryption key"
    )
    rate_limit_per_minute: int = Field(default=100, description="Rate limit per minute")
    rate_limit_burst: int = Field(default=20, description="Rate limit burst")
    cors_origins: List[str] = Field(
        default=[
            "http://localhost:2316",
            "http://127.0.0.1:2316",
            "http://localhost:4200",
            "http://127.0.0.1:4200",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "https://geneweb.surge.sh",
        ],
    )
    cors_methods: List[str] = Field(
        default=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    )
    cors_headers: List[str] = Field(default=["*"])
    force_https: bool = Field(default=False, description="Force HTTPS redirects")
    cert_pins: List[str] = Field(default=[], description="Certificate pins for HPKP")
    hsts_max_age: int = Field(default=31536000, description="HSTS max age in seconds")
    hsts_include_subdomains: bool = Field(
        default=True, description="Include subdomains in HSTS"
    )
    hsts_preload: bool = Field(default=False, description="Enable HSTS preload")
    csp_policy: str = Field(
        default=(
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'"
        ),
        description="Content Security Policy",
    )

    model_config = {
        "env_prefix": "GENEWEB_SECURITY_",
        "env_file": ".env",
        "extra": "ignore",
    }


class LoggingSettings(BaseSettings):
    """Logging configuration from environment variables."""

    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format")
    log_file: Optional[str] = Field(default=None, description="Log file path")
    sensitive_fields: List[str] = Field(
        default=["password", "secret", "token", "key", "auth"],
        description="Sensitive field names to mask in logs",
    )

    model_config = {"env_prefix": "GENEWEB_LOG_", "env_file": ".env", "extra": "ignore"}


class MonitoringSettings(BaseSettings):
    """Monitoring configuration from environment variables."""

    enable_metrics: bool = Field(default=True, description="Enable Prometheus metrics")
    metrics_path: str = Field(default="/metrics", description="Metrics endpoint path")

    model_config = {
        "env_prefix": "GENEWEB_MONITORING_",
        "env_file": ".env",
        "extra": "ignore",
    }


class AppSettings(BaseSettings):
    """Main application settings from environment variables."""

    app_name: str = Field(default="Geneweb API", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(
        default=8080, description="Server port"
    )  # Changed from 8000 to 8080 for Fly.io
    workers: int = Field(default=4, description="Number of worker processes")

    # SSL configuration
    ssl_certfile: Optional[str] = Field(
        default=None, description="SSL certificate file path"
    )
    ssl_keyfile: Optional[str] = Field(default=None, description="SSL key file path")
    ssl_ca_certs: Optional[str] = Field(
        default=None, description="SSL CA certificates file path"
    )

    # Nested settings as properties (not fields)
    security: Optional[SecuritySettings] = None
    logging: Optional[LoggingSettings] = None
    monitoring: Optional[MonitoringSettings] = None

    model_config = {"env_prefix": "GENEWEB_API_", "env_file": ".env", "extra": "ignore"}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize nested settings after parent initialization
        object.__setattr__(self, "security", SecuritySettings())
        object.__setattr__(self, "logging", LoggingSettings())
        object.__setattr__(self, "monitoring", MonitoringSettings())


# Global settings instance that loads from .env
settings = AppSettings()


def get_settings():
    """Get application settings."""
    return settings
