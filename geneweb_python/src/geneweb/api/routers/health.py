"""
Health check router for Geneweb API
Provides secure health monitoring without exposing sensitive information
"""

import sys
import time
from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..config import settings
from ..monitoring.metrics import get_metrics_summary


class HealthStatus(BaseModel):
    """Health check response model"""

    status: str
    timestamp: float
    version: str
    environment: str
    uptime: float
    checks: Dict[str, str]


class DetailedHealthStatus(BaseModel):
    """Detailed health check for internal monitoring"""

    status: str
    timestamp: float
    version: str
    environment: str
    uptime: float
    checks: Dict[str, str]
    metrics: Dict[str, Any]
    system: Dict[str, Any]


router = APIRouter(prefix="/health", tags=["health"])

# Track application start time
_start_time = time.time()


def get_basic_health_info() -> Dict[str, Any]:
    """
    Get basic health information (safe for public consumption)
    """
    current_time = time.time()

    return {
        "status": "healthy",
        "timestamp": current_time,
        "version": settings.app_version,
        "environment": "production" if not settings.debug else "development",
        "uptime": current_time - _start_time,
        "checks": {"api": "healthy", "configuration": "healthy"},
    }


def get_detailed_health_info() -> Dict[str, Any]:
    """
    Get detailed health information (for internal monitoring)
    """
    basic_info = get_basic_health_info()

    # Add metrics summary
    metrics = get_metrics_summary()

    # Add system information (non-sensitive)
    system_info = {
        "python_version": (
            f"{sys.version_info.major}.{sys.version_info.minor}."
            f"{sys.version_info.micro}"
        ),
        "platform": sys.platform,
    }

    return {**basic_info, "metrics": metrics, "system": system_info}


def check_internal_access(request) -> bool:
    """
    Check if request is from internal network
    (Simple implementation - in production use proper network checks)
    """
    client_ip = request.client.host if request.client else "unknown"

    # Allow internal IPs and localhost
    internal_ips = ["127.0.0.1", "::1", "localhost"]

    # Add your internal network ranges
    # internal_ips.extend(["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"])

    return client_ip in internal_ips


@router.get("/", response_model=HealthStatus, summary="Basic health check")
async def health_check():
    """
    Basic health check endpoint

    Returns minimal health information suitable for public consumption.
    Does not expose sensitive system details or metrics.
    """
    health_info = get_basic_health_info()

    return HealthStatus(
        status=health_info["status"],
        timestamp=health_info["timestamp"],
        version=health_info["version"],
        environment=health_info["environment"],
        uptime=health_info["uptime"],
        checks=health_info["checks"],
    )


@router.get("/live", summary="Liveness probe")
async def liveness_probe():
    """
    Kubernetes liveness probe endpoint

    Returns 200 if the application is running.
    Should not perform heavy checks.
    """
    return {"status": "live", "timestamp": time.time()}


@router.get("/ready", summary="Readiness probe")
async def readiness_probe():
    """
    Kubernetes readiness probe endpoint

    Returns 200 if the application is ready to serve traffic.
    Performs basic dependency checks.
    """
    checks = {}
    overall_status = "ready"

    # Check configuration
    try:
        _ = settings.app_name
        checks["configuration"] = "ready"
    except Exception:
        checks["configuration"] = "not_ready"
        overall_status = "not_ready"

    # Check database (when implemented)
    # try:
    #     db_health = await check_database_health()
    #     checks["database"] = "ready" if db_health else "not_ready"
    # except Exception:
    #     checks["database"] = "not_ready"
    #     overall_status = "not_ready"

    if overall_status == "not_ready":
        raise HTTPException(
            status_code=503,
            detail={
                "status": overall_status,
                "timestamp": time.time(),
                "checks": checks,
            },
        )

    return {"status": overall_status, "timestamp": time.time(), "checks": checks}


@router.get(
    "/detailed", response_model=DetailedHealthStatus, summary="Detailed health check"
)
async def detailed_health_check(request):
    """
    Detailed health check for internal monitoring

    Requires internal network access. Returns comprehensive health
    information including metrics and system details.
    """
    # Check for internal access
    if not check_internal_access(request):
        raise HTTPException(
            status_code=403,
            detail=(
                "Access denied. This endpoint is only available "
                "from internal networks."
            ),
        )

    health_info = get_detailed_health_info()

    return DetailedHealthStatus(
        status=health_info["status"],
        timestamp=health_info["timestamp"],
        version=health_info["version"],
        environment=health_info["environment"],
        uptime=health_info["uptime"],
        checks=health_info["checks"],
        metrics=health_info["metrics"],
        system=health_info["system"],
    )


# Legacy endpoint for backward compatibility
@router.get("/check", include_in_schema=False)
async def legacy_health_check():
    """Legacy health check endpoint for backward compatibility"""
    return await health_check()
