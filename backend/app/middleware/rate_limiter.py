from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from time import time
from collections import defaultdict
import asyncio


class RateLimiter:
    """
    Simple in-memory rate limiter
    For production, use Redis-based rate limiting
    """
    
    def __init__(self, requests_per_minute: int = 60, requests_per_hour: int = 500):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.minute_buckets = defaultdict(list)
        self.hour_buckets = defaultdict(list)
        self._cleanup_task = None
    
    async def check_rate_limit(self, client_id: str) -> bool:
        """
        Check if client has exceeded rate limits
        Returns True if allowed, False if rate limited
        """
        current_time = time()
        
        # Clean old entries
        self._cleanup_old_entries(client_id, current_time)
        
        # Check minute limit
        minute_requests = len(self.minute_buckets[client_id])
        if minute_requests >= self.requests_per_minute:
            return False
        
        # Check hour limit
        hour_requests = len(self.hour_buckets[client_id])
        if hour_requests >= self.requests_per_hour:
            return False
        
        # Add new request
        self.minute_buckets[client_id].append(current_time)
        self.hour_buckets[client_id].append(current_time)
        
        return True
    
    def _cleanup_old_entries(self, client_id: str, current_time: float):
        """
        Remove entries older than time windows
        """
        # Remove entries older than 1 minute
        minute_cutoff = current_time - 60
        self.minute_buckets[client_id] = [
            t for t in self.minute_buckets[client_id] if t > minute_cutoff
        ]
        
        # Remove entries older than 1 hour
        hour_cutoff = current_time - 3600
        self.hour_buckets[client_id] = [
            t for t in self.hour_buckets[client_id] if t > hour_cutoff
        ]
    
    def get_remaining_requests(self, client_id: str) -> dict:
        """
        Get remaining requests for client
        """
        current_time = time()
        self._cleanup_old_entries(client_id, current_time)
        
        minute_used = len(self.minute_buckets[client_id])
        hour_used = len(self.hour_buckets[client_id])
        
        return {
            "minute": {
                "limit": self.requests_per_minute,
                "remaining": max(0, self.requests_per_minute - minute_used),
                "used": minute_used
            },
            "hour": {
                "limit": self.requests_per_hour,
                "remaining": max(0, self.requests_per_hour - hour_used),
                "used": hour_used
            }
        }


# Global rate limiter instance
rate_limiter = RateLimiter(requests_per_minute=60, requests_per_hour=500)


async def rate_limit_middleware(request: Request, call_next):
    """
    Middleware to enforce rate limiting
    """
    # Skip rate limiting for health check
    if request.url.path in ["/", "/health", "/docs", "/openapi.json"]:
        return await call_next(request)
    
    # Get client identifier (IP address)
    client_id = request.client.host
    
    # Check rate limit
    allowed = await rate_limiter.check_rate_limit(client_id)
    
    if not allowed:
        remaining = rate_limiter.get_remaining_requests(client_id)
        return JSONResponse(
            status_code=429,
            content={
                "detail": "Rate limit exceeded. Please try again later.",
                "rate_limit": remaining
            }
        )
    
    # Add rate limit headers to response
    response = await call_next(request)
    remaining = rate_limiter.get_remaining_requests(client_id)
    
    response.headers["X-RateLimit-Limit-Minute"] = str(rate_limiter.requests_per_minute)
    response.headers["X-RateLimit-Remaining-Minute"] = str(remaining["minute"]["remaining"])
    response.headers["X-RateLimit-Limit-Hour"] = str(rate_limiter.requests_per_hour)
    response.headers["X-RateLimit-Remaining-Hour"] = str(remaining["hour"]["remaining"])
    
    return response
