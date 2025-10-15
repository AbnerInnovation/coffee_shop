"""
Centralized exception handling for the application.
Provides custom exception classes and consistent error responses.
"""
from typing import Any, Dict, Optional


class AppException(Exception):
    """Base application exception with status code and message."""
    
    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ResourceNotFoundError(AppException):
    """Raised when a requested resource is not found."""
    
    def __init__(self, resource: str, identifier: Any):
        message = f"{resource} with identifier '{identifier}' not found"
        super().__init__(message, status_code=404)


class ValidationError(AppException):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None):
        details = {"field": field} if field else {}
        super().__init__(message, status_code=400, details=details)


class UnauthorizedError(AppException):
    """Raised when authentication is required but not provided."""
    
    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, status_code=401)


class ForbiddenError(AppException):
    """Raised when user doesn't have permission for the requested action."""
    
    def __init__(self, message: str = "You don't have permission to perform this action"):
        super().__init__(message, status_code=403)


class ConflictError(AppException):
    """Raised when there's a conflict with the current state."""
    
    def __init__(self, message: str, resource: Optional[str] = None):
        details = {"resource": resource} if resource else {}
        super().__init__(message, status_code=409, details=details)


class DatabaseError(AppException):
    """Raised when a database operation fails."""
    
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, status_code=500)


class ExternalServiceError(AppException):
    """Raised when an external service call fails."""
    
    def __init__(self, service: str, message: str = "External service unavailable"):
        details = {"service": service}
        super().__init__(message, status_code=503, details=details)
