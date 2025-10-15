"""
Security headers middleware.
Adds security headers to all HTTP responses to protect against common web vulnerabilities.
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware that adds security headers to all responses.
    
    Headers added:
    - X-Content-Type-Options: Prevents MIME type sniffing
    - X-Frame-Options: Prevents clickjacking attacks
    - X-XSS-Protection: Enables browser XSS protection
    - Strict-Transport-Security: Enforces HTTPS connections
    - Content-Security-Policy: Restricts resource loading
    """
    
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Prevent clickjacking by denying iframe embedding
        response.headers["X-Frame-Options"] = "DENY"
        
        # Enable XSS protection in browsers
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Enforce HTTPS for 1 year (only in production)
        # Note: Only enable this if you're serving over HTTPS
        # response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Content Security Policy - restrict resource loading
        # Adjust this based on your frontend needs
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        # Referrer policy - control referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions policy - control browser features
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        return response
