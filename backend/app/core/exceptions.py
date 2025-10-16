"""
Centralized exception handling for the application.
Provides custom exception classes and consistent error responses.

Usage Example:
    from app.core.exceptions import ResourceNotFoundError, ValidationError
    
    # Raise a 404 error
    raise ResourceNotFoundError("Order", order_id)
    
    # Raise a validation error
    raise ValidationError("Invalid email format", field="email")
    
    # Raise a custom error
    raise AppException("Custom error message", status_code=418, details={"reason": "teapot"})
"""
from typing import Any, Dict, Optional


class AppException(Exception):
    """
    Base application exception with status code and message.
    
    All custom exceptions should inherit from this class to ensure
    consistent error handling across the application.
    
    Attributes:
        message (str): Human-readable error message
        status_code (int): HTTP status code (default: 500)
        details (dict): Additional context about the error
    
    Example:
        raise AppException("Something went wrong", status_code=500, details={"context": "value"})
    """
    
    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message='{self.message}', status_code={self.status_code})"


class ResourceNotFoundError(AppException):
    """
    Raised when a requested resource is not found (HTTP 404).
    
    Args:
        resource (str): Type of resource (e.g., "Order", "MenuItem", "Table")
        identifier (Any): The identifier used to search for the resource
    
    Example:
        raise ResourceNotFoundError("Order", order_id)
        # Returns: Order with identifier '123' not found
    """
    
    def __init__(self, resource: str, identifier: Any):
        message = f"{resource} with identifier '{identifier}' not found"
        super().__init__(message, status_code=404, details={"resource": resource, "identifier": str(identifier)})


class ValidationError(AppException):
    """
    Raised when input validation fails (HTTP 400).
    
    Args:
        message (str): Description of the validation error
        field (str, optional): The specific field that failed validation
    
    Example:
        raise ValidationError("Email format is invalid", field="email")
        raise ValidationError("Price must be greater than 0", field="price")
    """
    
    def __init__(self, message: str, field: Optional[str] = None):
        details = {"field": field} if field else {}
        super().__init__(message, status_code=400, details=details)


class UnauthorizedError(AppException):
    """
    Raised when authentication is required but not provided (HTTP 401).
    
    Args:
        message (str): Custom authentication error message
    
    Example:
        raise UnauthorizedError("Invalid or expired token")
        raise UnauthorizedError()  # Uses default message
    """
    
    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, status_code=401, details={"auth_required": True})


class ForbiddenError(AppException):
    """
    Raised when user doesn't have permission for the requested action (HTTP 403).
    
    Args:
        message (str): Custom permission error message
        required_permission (str, optional): The permission that was required
    
    Example:
        raise ForbiddenError("Admin access required", required_permission="admin")
        raise ForbiddenError()  # Uses default message
    """
    
    def __init__(self, message: str = "You don't have permission to perform this action", required_permission: Optional[str] = None):
        details = {"required_permission": required_permission} if required_permission else {}
        super().__init__(message, status_code=403, details=details)


class ConflictError(AppException):
    """
    Raised when there's a conflict with the current state (HTTP 409).
    
    Args:
        message (str): Description of the conflict
        resource (str, optional): The resource type involved in the conflict
    
    Example:
        raise ConflictError("Order already exists for this table", resource="Order")
        raise ConflictError("Table is already occupied")
    """
    
    def __init__(self, message: str, resource: Optional[str] = None):
        details = {"resource": resource} if resource else {}
        super().__init__(message, status_code=409, details=details)


class DatabaseError(AppException):
    """
    Raised when a database operation fails (HTTP 500).
    
    Args:
        message (str): Description of the database error
        operation (str, optional): The operation that failed (e.g., "insert", "update", "delete")
    
    Example:
        raise DatabaseError("Failed to save order", operation="insert")
        raise DatabaseError()  # Uses default message
    """
    
    def __init__(self, message: str = "Database operation failed", operation: Optional[str] = None):
        details = {"operation": operation} if operation else {}
        super().__init__(message, status_code=500, details=details)


class ExternalServiceError(AppException):
    """
    Raised when an external service call fails (HTTP 503).
    
    Args:
        service (str): Name of the external service that failed
        message (str): Description of the service error
    
    Example:
        raise ExternalServiceError("payment_gateway", "Payment processing timeout")
        raise ExternalServiceError("email_service")  # Uses default message
    """
    
    def __init__(self, service: str, message: str = "External service unavailable"):
        details = {"service": service}
        super().__init__(message, status_code=503, details=details)
