"""
Security headers middl        # HTTPS enforcement
        if (
            settings.security.force_https
            and not request.url.scheme == "https"
        ):
            # In production, this should be handled by reverse proxy
            # but we add the header for completeness
            response.headers["Strict-Transport-Security"] = (
                f"max-age={settings.security.hsts_max_age}; "
                f"includeSubDomains={
                    'true' if settings.security.hsts_include_subdomains
                    else 'false'
                }; "
                f"preload={
                    'true' if settings.security.hsts_preload else 'false'
                }"
            ) Geneweb API
Implements HSTS, CSP, X-Frame-Options and other security headers
"""

import asyncio
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from ..config import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Add security headers to response
        """
        response = await call_next(request)

        # HTTPS enforcement
        if settings.security.force_https and not request.url.scheme == "https":
            # In production, this should be handled by reverse proxy
            # but we add the header for completeness
            hsts_subs = "true" if settings.security.hsts_include_subdomains else "false"
            hsts_preload = "true" if settings.security.hsts_preload else "false"
            response.headers["Strict-Transport-Security"] = (
                f"max-age={settings.security.hsts_max_age}; "
                f"includeSubDomains={hsts_subs}; "
                f"preload={hsts_preload}"
            )

        # HSTS Header (only for HTTPS)
        if request.url.scheme == "https":
            hsts_value = f"max-age={settings.security.hsts_max_age}"
            if settings.security.hsts_include_subdomains:
                hsts_value += "; includeSubDomains"
            if settings.security.hsts_preload:
                hsts_value += "; preload"
            response.headers["Strict-Transport-Security"] = hsts_value

        # Content Security Policy
        response.headers["Content-Security-Policy"] = settings.security.csp_policy

        # Frame options
        response.headers["X-Frame-Options"] = "DENY"

        # Content type options
        response.headers["X-Content-Type-Options"] = "nosniff"

        # XSS Protection
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions Policy
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=(), "
            "payment=(), usb=(), magnetometer=(), gyroscope=(), "
            "accelerometer=(), ambient-light-sensor=(), autoplay=(), "
            "encrypted-media=(), fullscreen=(), picture-in-picture=()"
        )

        # Certificate pinning (HPKP) - Only if pins are configured
        if settings.security.cert_pins:
            pins = "; ".join(
                [f'pin-sha256="{pin}"' for pin in settings.security.cert_pins]
            )
            response.headers["Public-Key-Pins"] = (
                f"{pins}; max-age=2592000; includeSubDomains"
            )

        # Server header removal
        if "server" in response.headers:
            del response.headers["server"]

        # Add custom server header
        response.headers["Server"] = "Geneweb-API"

        return response


class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    """
    Middleware to redirect HTTP requests to HTTPS
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Redirect HTTP to HTTPS if force_https is enabled
        """
        if (
            settings.security.force_https
            and request.url.scheme == "http"
            and request.url.hostname not in ["localhost", "127.0.0.1"]
        ):

            # Redirect to HTTPS
            https_url = request.url.replace(scheme="https")
            return Response(status_code=301, headers={"Location": str(https_url)})

        response = await call_next(request)
        return response


class RequestSizeMiddleware(BaseHTTPMiddleware):
    """
    Middleware to limit request size for DDoS protection
    """

    def __init__(self, app, max_size: int = 1024 * 1024):  # 1MB default
        super().__init__(app)
        self.max_size = max_size

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Check request size and reject if too large
        """
        content_length = request.headers.get("content-length")

        if content_length:
            content_length = int(content_length)
            if content_length > self.max_size:
                return Response(
                    content="Request too large",
                    status_code=413,
                    headers={"Content-Type": "text/plain"},
                )

        response = await call_next(request)
        return response


class TimingAttackMiddleware(BaseHTTPMiddleware):
    """
    Middleware to prevent timing attacks by adding random delay
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Add random timing to prevent timing attacks
        """
        import random

        response = await call_next(request)

        # Add small random delay for authentication endpoints
        if "/auth" in str(request.url) or "/login" in str(request.url):
            # Add 10-50ms random delay
            delay = random.uniform(0.01, 0.05)
            await asyncio.sleep(delay)

        return response
