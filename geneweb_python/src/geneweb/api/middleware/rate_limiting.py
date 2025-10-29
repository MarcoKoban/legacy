"""
Rate limiting middleware for DDoS protection
"""

import time
from collections import defaultdict, deque
from typing import Deque, Dict

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from ..config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using sliding window algorithm
    Provides DDoS protection with configurable limits per IP
    """

    def __init__(self, app, requests_per_minute: int = None, burst_limit: int = None):
        super().__init__(app)
        self.requests_per_minute = (
            requests_per_minute or settings.security.rate_limit_per_minute
        )
        self.burst_limit = burst_limit or settings.security.rate_limit_burst

        # Store request timestamps per IP
        self.request_times: Dict[str, Deque[float]] = defaultdict(deque)

        # Burst tracking
        self.burst_counts: Dict[str, int] = defaultdict(int)
        self.burst_reset_times: Dict[str, float] = defaultdict(float)

    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP from request, considering proxy headers
        """
        # Check for forwarded headers (reverse proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP (client IP)
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fallback to direct connection
        if request.client:
            return request.client.host

        return "unknown"

    def _clean_old_requests(self, ip: str, current_time: float):
        """
        Remove request timestamps older than 1 minute
        """
        cutoff_time = current_time - 60  # 60 seconds

        while self.request_times[ip] and self.request_times[ip][0] < cutoff_time:
            self.request_times[ip].popleft()

    def _check_burst_limit(self, ip: str, current_time: float) -> bool:
        """
        Check if client has exceeded burst limit
        """
        # Reset burst count every minute
        if current_time - self.burst_reset_times[ip] >= 60:
            self.burst_counts[ip] = 0
            self.burst_reset_times[ip] = current_time

        return self.burst_counts[ip] < self.burst_limit

    def _is_rate_limited(self, ip: str) -> bool:
        """
        Check if IP should be rate limited
        """
        current_time = time.time()

        # Clean old requests
        self._clean_old_requests(ip, current_time)

        # Check burst limit
        if not self._check_burst_limit(ip, current_time):
            return True

        # Check requests per minute
        if len(self.request_times[ip]) >= self.requests_per_minute:
            return True

        return False

    def _record_request(self, ip: str):
        """
        Record a new request for the IP
        """
        current_time = time.time()
        self.request_times[ip].append(current_time)
        self.burst_counts[ip] += 1

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Apply rate limiting based on client IP
        """
        client_ip = self._get_client_ip(request)

        # Skip rate limiting for health checks and metrics
        if request.url.path in [
            "/health",
            "/health/",
            "/metrics",
            "/docs",
            "/openapi.json",
        ]:
            return await call_next(request)

        # Check if rate limited
        if self._is_rate_limited(client_ip):
            # Calculate time until reset
            current_time = time.time()
            if self.request_times[client_ip]:
                oldest_request = self.request_times[client_ip][0]
                reset_time = oldest_request + 60
                retry_after = max(1, int(reset_time - current_time))
            else:
                retry_after = 60

            return Response(
                content=f"Rate limit exceeded. Try again in {retry_after} seconds.",
                status_code=429,
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(current_time + retry_after)),
                },
            )

        # Record the request
        self._record_request(client_ip)

        # Process request
        response = await call_next(request)

        # Add rate limit headers to response
        current_time = time.time()
        self._clean_old_requests(client_ip, current_time)
        remaining = max(
            0, self.requests_per_minute - len(self.request_times[client_ip])
        )

        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(current_time + 60))

        return response


class IPWhitelistMiddleware(BaseHTTPMiddleware):
    """
    Middleware to whitelist specific IPs from rate limiting
    """

    def __init__(self, app, whitelist: list = None):
        super().__init__(app)
        self.whitelist = set(whitelist or ["127.0.0.1", "::1", "localhost"])

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        if request.client:
            return request.client.host

        return "unknown"

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Skip to next middleware if IP is whitelisted
        """
        client_ip = self._get_client_ip(request)

        # Add header to indicate if IP is whitelisted
        response = await call_next(request)

        if client_ip in self.whitelist:
            response.headers["X-IP-Whitelisted"] = "true"

        return response
