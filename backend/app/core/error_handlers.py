"""
Centralized error handling utilities for consistent error processing across the application.
"""
from app.core.exceptions import ConflictError, ValidationError


def handle_duplicate_error(e: Exception, resource: str) -> None:
    """
    Handle duplicate/already exists errors consistently across all endpoints.
    
    Checks if the exception message contains common duplicate error indicators
    and raises the appropriate custom exception.
    
    Args:
        e: The original exception
        resource: The resource type (e.g., "User", "Category", "Table")
        
    Raises:
        ConflictError: If the error is a duplicate/conflict error (409)
        ValidationError: For all other validation errors (400)
        
    Example:
        try:
            create_category(db, category)
        except ValueError as e:
            handle_duplicate_error(e, "Category")
    """
    error_msg = str(e).lower()
    
    # Check for common duplicate error patterns
    duplicate_indicators = [
        "already exists",
        "duplicate",
        "already registered"
    ]
    
    if any(indicator in error_msg for indicator in duplicate_indicators):
        raise ConflictError(str(e), resource=resource)
    
    # Default to validation error for other cases
    raise ValidationError(str(e))
