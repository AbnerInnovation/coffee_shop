from fastapi import Request, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from urllib.parse import urlparse

from ..models.restaurant import Restaurant
from ..db.base import SessionLocal

logger = logging.getLogger(__name__)

RESERVED_SUBDOMAINS = {"www", "localhost", "api"}


def extract_subdomain(host: str) -> Optional[str]:
    """
    Extract subdomain from host header.
    
    Examples:
        - restaurant1.example.com -> restaurant1
        - restaurant1.localhost:8000 -> restaurant1
        - localhost:8000 -> None (no subdomain)
        - example.com -> None (no subdomain)
    """
    # Remove port if present
    host_without_port = host.split(':')[0]
    
    # Split by dots
    parts = host_without_port.split('.')
    
    # If we have at least 2 parts (subdomain.domain) or 3 parts (subdomain.domain.tld)
    if len(parts) >= 2:
        # Check if it's not just domain.tld or a reserved subdomain
        first = parts[0].lower()
        if first not in RESERVED_SUBDOMAINS and len(first) > 0:
            return first
    
    return None


async def get_restaurant_from_request(request: Request) -> Optional[Restaurant]:
    """
    Extract restaurant from request subdomain.
    Returns None if no subdomain or restaurant not found.
    """
    # Get host from request
    host = request.headers.get('host', '')
    
    # Extract subdomain from Host
    subdomain = extract_subdomain(host)

    # Treat reserved subdomains as non-tenant so we can resolve via Origin/Referer/header
    if subdomain in RESERVED_SUBDOMAINS:
        subdomain = None
    
    # If no subdomain on Host, try Origin then Referer headers
    if not subdomain:
        origin = request.headers.get('origin') or ''
        referer = request.headers.get('referer') or ''
        for hdr in (origin, referer):
            if hdr:
                try:
                    parsed = urlparse(hdr)
                    origin_host = parsed.hostname or ''
                    subdomain = extract_subdomain(origin_host)
                    if subdomain:
                        logger.debug(f"Resolved subdomain from header ({'Origin' if hdr==origin else 'Referer'}): {subdomain}")
                        break
                except Exception:
                    # ignore parse errors
                    pass
    
    # Final fallback: allow explicit override via header for server-to-server calls
    if not subdomain:
        hdr_sub = request.headers.get('x-restaurant-subdomain')
        if hdr_sub:
            subdomain = hdr_sub.strip().lower()
    
    if not subdomain:
        logger.debug(f"No subdomain found in host: {host}")
        return None
    
    # Query database for restaurant
    db = SessionLocal()
    try:
        restaurant = db.query(Restaurant).filter(
            Restaurant.subdomain == subdomain,
            Restaurant.is_active == True
        ).first()
        
        if restaurant:
            logger.debug(f"Found restaurant: {restaurant.name} (subdomain: {subdomain})")
        else:
            logger.warning(f"No active restaurant found for subdomain: {subdomain}")
        
        return restaurant
    finally:
        db.close()


async def require_restaurant(request: Request) -> Restaurant:
    """
    Dependency that requires a valid restaurant subdomain.
    Raises HTTPException if no restaurant found.
    """
    restaurant = await get_restaurant_from_request(request)
    
    if not restaurant:
        host = request.headers.get('host', '')
        subdomain = extract_subdomain(host)
        
        if subdomain:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Restaurant not found for subdomain: {subdomain}"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Restaurant subdomain is required. Please access via subdomain (e.g., restaurant1.example.com)"
            )
    
    return restaurant

class RestaurantMiddleware(BaseHTTPMiddleware):
    """
    Middleware to attach restaurant context to request.state.restaurant.
    """

    async def dispatch(self, request: Request, call_next):
        try:
            restaurant = await get_restaurant_from_request(request)
            if restaurant:
                request.state.restaurant = restaurant
                logger.debug(f"Restaurant context set: {restaurant.name}")
        except Exception as e:
            logger.exception("Error resolving restaurant from request: %s", e)
        response = await call_next(request)
        return response
