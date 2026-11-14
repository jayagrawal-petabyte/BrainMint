"""
In-memory sliding-window rate limiter.

Suitable for single-process deployments (dev + small prod).
For multi-process/multi-worker deployments, swap the storage backend
for Redis (e.g. slowapi + redis).

Usage in a FastAPI endpoint::

    from app.core.rate_limit import RateLimiter

    limiter = RateLimiter(max_requests=5, window_seconds=60)

    @router.post("/submit")
    def submit(request: Request, ...):
        limiter.check(request.client.host)
        ...
"""

import time
from collections import defaultdict, deque
from typing import Deque, Dict

from fastapi import HTTPException, Request, status


class RateLimiter:
    """
    Sliding-window counter rate limiter keyed on an arbitrary string (usually IP).

    Parameters
    ----------
    max_requests : int
        Maximum number of requests allowed within *window_seconds*.
    window_seconds : int
        Length of the sliding window in seconds.
    """

    def __init__(self, max_requests: int = 5, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # Maps key → deque of timestamps (float)
        self._windows: Dict[str, Deque[float]] = defaultdict(deque)

    def _evict_old(self, key: str, now: float) -> None:
        window = self._windows[key]
        cutoff = now - self.window_seconds
        while window and window[0] < cutoff:
            window.popleft()

    def is_allowed(self, key: str) -> bool:
        """Return True if the request is within limits."""
        now = time.monotonic()
        self._evict_old(key, now)
        if len(self._windows[key]) >= self.max_requests:
            return False
        self._windows[key].append(now)
        return True

    def check(self, key: str) -> None:
        """Raise HTTP 429 if the rate limit is exceeded."""
        if not self.is_allowed(key):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "success": False,
                    "error": {
                        "code": "RATE_LIMITED",
                        "message": (
                            f"Too many requests. Please wait before trying again. "
                            f"Limit: {self.max_requests} per {self.window_seconds}s."
                        ),
                        "details": None,
                    },
                },
            )


def get_client_ip(request: Request) -> str:
    """
    Extract the real client IP, honoring X-Forwarded-For set by a reverse proxy.
    Falls back to the direct connection address.
    """
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


# ---------------------------------------------------------------------------
# Pre-configured limiters for enquiry endpoints
# ---------------------------------------------------------------------------

# Public form submission: 5 per IP per 60 s
enquiry_limiter = RateLimiter(max_requests=5, window_seconds=60)

# Admin endpoints: 100 per IP per 60 s (much more lenient)
admin_enquiry_limiter = RateLimiter(max_requests=100, window_seconds=60)
