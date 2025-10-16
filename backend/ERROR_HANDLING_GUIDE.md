# Centralized Error Handling Guide

## Overview

The Coffee Shop Admin API uses a centralized error handling system that provides consistent error responses across all endpoints. This guide explains how to use custom exceptions and handle errors properly.

## Exception Classes

All custom exceptions inherit from `AppException` and are located in `app/core/exceptions.py`.

### Available Exception Classes

| Exception | HTTP Status | Use Case |
|-----------|-------------|----------|
| `AppException` | 500 (default) | Base exception for custom errors |
| `ResourceNotFoundError` | 404 | Resource not found |
| `ValidationError` | 400 | Input validation failures |
| `UnauthorizedError` | 401 | Authentication required |
| `ForbiddenError` | 403 | Insufficient permissions |
| `ConflictError` | 409 | State conflicts (e.g., duplicate records) |
| `DatabaseError` | 500 | Database operation failures |
| `ExternalServiceError` | 503 | External service unavailable |

## Usage Examples

### 1. ResourceNotFoundError (404)

Use when a requested resource doesn't exist:

```python
from app.core.exceptions import ResourceNotFoundError
from sqlalchemy.orm import Session

def get_order(db: Session, order_id: int):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise ResourceNotFoundError("Order", order_id)
    return order
```

**Response:**
```json
{
  "success": false,
  "error": {
    "message": "Order with identifier '123' not found",
    "type": "ResourceNotFoundError",
    "status_code": 404,
    "resource": "Order",
    "identifier": "123"
  }
}
```

### 2. ValidationError (400)

Use for input validation failures:

```python
from app.core.exceptions import ValidationError

def create_menu_item(data: dict):
    if data.get("price", 0) <= 0:
        raise ValidationError("Price must be greater than 0", field="price")
    
    if not data.get("name"):
        raise ValidationError("Name is required", field="name")
    
    # Continue with creation...
```

**Response:**
```json
{
  "success": false,
  "error": {
    "message": "Price must be greater than 0",
    "type": "ValidationError",
    "status_code": 400,
    "field": "price"
  }
}
```

### 3. UnauthorizedError (401)

Use when authentication is required:

```python
from app.core.exceptions import UnauthorizedError

def verify_token(token: str):
    if not token:
        raise UnauthorizedError("Access token is required")
    
    try:
        payload = decode_token(token)
    except Exception:
        raise UnauthorizedError("Invalid or expired token")
    
    return payload
```

**Response:**
```json
{
  "success": false,
  "error": {
    "message": "Invalid or expired token",
    "type": "UnauthorizedError",
    "status_code": 401,
    "auth_required": true
  }
}
```

### 4. ForbiddenError (403)

Use when user lacks permissions:

```python
from app.core.exceptions import ForbiddenError

def delete_restaurant(user: User, restaurant_id: int):
    if user.role != "admin":
        raise ForbiddenError(
            "Only administrators can delete restaurants",
            required_permission="admin"
        )
    
    # Proceed with deletion...
```

**Response:**
```json
{
  "success": false,
  "error": {
    "message": "Only administrators can delete restaurants",
    "type": "ForbiddenError",
    "status_code": 403,
    "required_permission": "admin"
  }
}
```

### 5. ConflictError (409)

Use for state conflicts:

```python
from app.core.exceptions import ConflictError

def create_order(db: Session, table_id: int):
    # Check if table already has an open order
    existing_order = db.query(Order).filter(
        Order.table_id == table_id,
        Order.status.in_(["pending", "preparing", "ready"])
    ).first()
    
    if existing_order:
        raise ConflictError(
            "Table already has an open order",
            resource="Order"
        )
    
    # Create new order...
```

**Response:**
```json
{
  "success": false,
  "error": {
    "message": "Table already has an open order",
    "type": "ConflictError",
    "status_code": 409,
    "resource": "Order"
  }
}
```

### 6. DatabaseError (500)

Use for database operation failures:

```python
from app.core.exceptions import DatabaseError
from sqlalchemy.exc import SQLAlchemyError

def save_order(db: Session, order: Order):
    try:
        db.add(order)
        db.commit()
        db.refresh(order)
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseError(
            "Failed to save order to database",
            operation="insert"
        )
    
    return order
```

**Response:**
```json
{
  "success": false,
  "error": {
    "message": "Failed to save order to database",
    "type": "DatabaseError",
    "status_code": 500,
    "operation": "insert"
  }
}
```

### 7. ExternalServiceError (503)

Use when external services fail:

```python
from app.core.exceptions import ExternalServiceError
import requests

def send_order_notification(order_id: int):
    try:
        response = requests.post(
            "https://notification-service.example.com/notify",
            json={"order_id": order_id},
            timeout=5
        )
        response.raise_for_status()
    except requests.RequestException:
        raise ExternalServiceError(
            "notification_service",
            "Failed to send order notification"
        )
```

**Response:**
```json
{
  "success": false,
  "error": {
    "message": "Failed to send order notification",
    "type": "ExternalServiceError",
    "status_code": 503,
    "service": "notification_service"
  }
}
```

### 8. Custom AppException

For cases not covered by specific exceptions:

```python
from app.core.exceptions import AppException

def process_payment(amount: float):
    if amount > 10000:
        raise AppException(
            "Payment amount exceeds maximum limit",
            status_code=400,
            details={"max_amount": 10000, "requested_amount": amount}
        )
    
    # Process payment...
```

**Response:**
```json
{
  "success": false,
  "error": {
    "message": "Payment amount exceeds maximum limit",
    "type": "AppException",
    "status_code": 400,
    "max_amount": 10000,
    "requested_amount": 15000
  }
}
```

## Best Practices

### 1. Use Specific Exceptions

Always use the most specific exception class for your use case:

```python
# ❌ Bad - Too generic
raise AppException("Order not found", status_code=404)

# ✅ Good - Specific and clear
raise ResourceNotFoundError("Order", order_id)
```

### 2. Provide Context

Include relevant details to help with debugging:

```python
# ❌ Bad - No context
raise ValidationError("Invalid input")

# ✅ Good - Clear context
raise ValidationError("Email format is invalid", field="email")
```

### 3. Don't Expose Sensitive Information

Never include sensitive data in error messages:

```python
# ❌ Bad - Exposes internal details
raise DatabaseError(f"SQL Error: {sql_query}")

# ✅ Good - Generic message
raise DatabaseError("Failed to retrieve user data", operation="select")
```

### 4. Handle Exceptions at the Right Level

Let exceptions bubble up to the appropriate handler:

```python
# ❌ Bad - Catching and re-raising unnecessarily
def get_order(db: Session, order_id: int):
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise ResourceNotFoundError("Order", order_id)
    except ResourceNotFoundError:
        raise  # Unnecessary

# ✅ Good - Let it propagate naturally
def get_order(db: Session, order_id: int):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise ResourceNotFoundError("Order", order_id)
    return order
```

### 5. Log Before Raising (When Appropriate)

Add logging for important errors:

```python
import logging

logger = logging.getLogger(__name__)

def critical_operation():
    try:
        # Perform operation
        pass
    except Exception as e:
        logger.error(f"Critical operation failed: {str(e)}", exc_info=True)
        raise DatabaseError("Critical operation failed")
```

## Error Response Format

All errors follow a consistent format:

```json
{
  "success": false,
  "error": {
    "message": "Human-readable error message",
    "type": "ExceptionClassName",
    "status_code": 400,
    // Additional context fields...
  }
}
```

## Automatic Error Handling

The following errors are automatically handled by global exception handlers:

1. **SQLAlchemy Errors** - Database errors (500)
2. **IntegrityError** - Constraint violations (409)
3. **RequestValidationError** - Pydantic validation errors (422)
4. **Unhandled Exceptions** - Any other exceptions (500)

You don't need to catch these explicitly; they'll be handled automatically with proper logging.

## Testing Error Handling

Example test for error handling:

```python
import pytest
from app.core.exceptions import ResourceNotFoundError

def test_get_nonexistent_order(client):
    response = client.get("/api/v1/orders/99999")
    
    assert response.status_code == 404
    assert response.json()["success"] is False
    assert response.json()["error"]["type"] == "ResourceNotFoundError"
    assert "not found" in response.json()["error"]["message"].lower()
```

## Migration Guide

If you're updating existing code to use the new error handling:

### Before:
```python
from fastapi import HTTPException

def get_order(order_id: int):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
```

### After:
```python
from app.core.exceptions import ResourceNotFoundError

def get_order(order_id: int):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise ResourceNotFoundError("Order", order_id)
    return order
```

## Summary

- ✅ Use specific exception classes for different error types
- ✅ Provide clear, actionable error messages
- ✅ Include relevant context in the `details` parameter
- ✅ Let exceptions propagate to global handlers
- ✅ Don't expose sensitive information in error messages
- ✅ Log errors appropriately based on severity
- ✅ Test error handling in your endpoints

For more information, see:
- `backend/app/core/exceptions.py` - Exception class definitions
- `backend/app/main.py` - Global exception handlers
