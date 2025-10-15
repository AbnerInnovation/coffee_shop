"""
Rate limiting configuration using slowapi.
Protects API endpoints from abuse and DDoS attacks.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

# Create limiter instance
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],  # Default rate limit for all endpoints
    storage_uri="memory://",  # Use memory storage (upgrade to Redis for production)
    application_limits=["100/minute"],  # Apply to all routes in the app
    headers_enabled=True,  # Send rate limit info in response headers
)
