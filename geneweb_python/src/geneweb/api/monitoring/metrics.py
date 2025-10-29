"""
Prometheus metrics for Geneweb API
Provides secure monitoring without exposing sensitive data
"""

import time
from typing import Any, Dict

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)
from prometheus_client.registry import REGISTRY

from ..config import settings

# Metrics instances
request_count = Counter(
    "geneweb_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
)

request_duration = Histogram(
    "geneweb_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
)

active_connections = Gauge("geneweb_active_connections", "Number of active connections")

rate_limit_hits = Counter(
    "geneweb_rate_limit_hits_total",
    "Total rate limit hits",
    ["client_ip_hash"],  # Hash IP for privacy
)

security_events = Counter(
    "geneweb_security_events_total", "Total security events", ["event_type", "severity"]
)

database_operations = Counter(
    "geneweb_database_operations_total",
    "Total database operations",
    ["operation_type", "status"],
)

application_info = Gauge(
    "geneweb_application_info", "Application information", ["version", "environment"]
)


class MetricsMiddleware:
    """
    Middleware to collect HTTP metrics
    """

    def __init__(self, app: FastAPI):
        self.app = app

    async def __call__(self, request: Request, call_next):
        """
        Collect metrics for each request
        """
        # Skip metrics collection for metrics endpoint itself
        if request.url.path == settings.monitoring.metrics_path:
            return await call_next(request)

        start_time = time.time()

        # Increment active connections
        active_connections.inc()

        try:
            response = await call_next(request)

            # Record metrics
            method = request.method
            endpoint = self._get_endpoint_pattern(request)
            status_code = str(response.status_code)

            # Increment request counter
            request_count.labels(
                method=method, endpoint=endpoint, status_code=status_code
            ).inc()

            # Record request duration
            duration = time.time() - start_time
            request_duration.labels(method=method, endpoint=endpoint).observe(duration)

            return response

        except Exception:
            # Record error metrics
            request_count.labels(
                method=request.method,
                endpoint=self._get_endpoint_pattern(request),
                status_code="500",
            ).inc()
            raise

        finally:
            # Decrement active connections
            active_connections.dec()

    def _get_endpoint_pattern(self, request: Request) -> str:
        """
        Get endpoint pattern without exposing sensitive path parameters
        """
        path = request.url.path

        # Common patterns to normalize
        patterns = [
            (r"/users/\d+", "/users/{id}"),
            (r"/families/\d+", "/families/{id}"),
            (r"/persons/\d+", "/persons/{id}"),
            (r"/api/v\d+", "/api/v{version}"),
        ]

        for pattern, replacement in patterns:
            import re

            path = re.sub(pattern, replacement, path)

        return path


def setup_metrics(app: FastAPI):
    """
    Setup metrics collection for the FastAPI application
    """
    if not settings.monitoring.enable_metrics:
        return

    # Set application info
    application_info.labels(
        version=settings.app_version,
        environment="development" if settings.debug else "production",
    ).set(1)

    # Add metrics middleware
    app.middleware("http")(MetricsMiddleware(app))

    # Add metrics endpoint
    @app.get(
        settings.monitoring.metrics_path,
        response_class=PlainTextResponse,
        include_in_schema=False,
        tags=["Monitoring"],
    )
    async def metrics():
        """
        Prometheus metrics endpoint
        """
        return PlainTextResponse(
            generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST
        )


def record_security_event(event_type: str, severity: str = "info"):
    """
    Record a security event metric
    """
    security_events.labels(event_type=event_type, severity=severity).inc()


def record_rate_limit_hit(client_ip: str):
    """
    Record a rate limit hit (with IP hashing for privacy)
    """
    import hashlib

    # Hash IP for privacy while maintaining uniqueness
    ip_hash = hashlib.sha256(client_ip.encode()).hexdigest()[:8]

    rate_limit_hits.labels(client_ip_hash=ip_hash).inc()


def record_database_operation(operation_type: str, status: str = "success"):
    """
    Record database operation metrics
    """
    database_operations.labels(operation_type=operation_type, status=status).inc()


def get_metrics_summary() -> Dict[str, Any]:
    """
    Get a summary of key metrics (for health checks)
    """
    try:
        # Collect samples from metrics
        samples = list(REGISTRY.collect())

        summary = {
            "total_requests": 0,
            "active_connections": 0,
            "rate_limit_hits": 0,
            "security_events": 0,
        }

        for metric_family in samples:
            for sample in metric_family.samples:
                if sample.name == "geneweb_http_requests_total":
                    summary["total_requests"] += sample.value
                elif sample.name == "geneweb_active_connections":
                    summary["active_connections"] = sample.value
                elif sample.name == "geneweb_rate_limit_hits_total":
                    summary["rate_limit_hits"] += sample.value
                elif sample.name == "geneweb_security_events_total":
                    summary["security_events"] += sample.value

        return summary

    except Exception:
        # Return empty summary if metrics collection fails
        return {
            "total_requests": 0,
            "active_connections": 0,
            "rate_limit_hits": 0,
            "security_events": 0,
            "error": "metrics_collection_failed",
        }
