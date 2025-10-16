# Exception Handling Quick Reference

## Import Statement
```python
from app.core.exceptions import (
    ResourceNotFoundError,
    ValidationError,
    UnauthorizedError,
    ForbiddenError,
    ConflictError,
    DatabaseError,
    ExternalServiceError
)
```

## Quick Reference Table

| Scenario | Exception | Example |
|----------|-----------|---------|
| Resource doesn't exist | `ResourceNotFoundError` | `raise ResourceNotFoundError("Order", order_id)` |
| Invalid input | `ValidationError` | `raise ValidationError("Invalid email", field="email")` |
| Not authenticated | `UnauthorizedError` | `raise UnauthorizedError("Token expired")` |
| No permission | `ForbiddenError` | `raise ForbiddenError("Admin only", required_permission="admin")` |
| Duplicate/conflict | `ConflictError` | `raise ConflictError("Order already exists", resource="Order")` |
| Database error | `DatabaseError` | `raise DatabaseError("Save failed", operation="insert")` |
| External API fails | `ExternalServiceError` | `raise ExternalServiceError("payment_api", "Timeout")` |

## Common Patterns

### Check if resource exists (404)
```python
item = db.query(Model).filter(Model.id == id).first()
if not item:
    raise ResourceNotFoundError("ModelName", id)
```

### Validate input (400)
```python
if price <= 0:
    raise ValidationError("Price must be positive", field="price")
```

### Check authentication (401)
```python
if not token or not is_valid(token):
    raise UnauthorizedError("Invalid or expired token")
```

### Check permissions (403)
```python
if not user.is_admin:
    raise ForbiddenError("Admin access required", required_permission="admin")
```

### Check for duplicates (409)
```python
existing = db.query(Model).filter(Model.email == email).first()
if existing:
    raise ConflictError("Email already registered", resource="User")
```

### Handle database errors (500)
```python
try:
    db.add(item)
    db.commit()
except Exception:
    db.rollback()
    raise DatabaseError("Failed to save item", operation="insert")
```

## Error Response Format

All errors return:
```json
{
  "success": false,
  "error": {
    "message": "Error description",
    "type": "ExceptionClassName",
    "status_code": 400,
    // ... additional context fields
  }
}
```

## HTTP Status Codes

- **400** - ValidationError (bad input)
- **401** - UnauthorizedError (not authenticated)
- **403** - ForbiddenError (no permission)
- **404** - ResourceNotFoundError (not found)
- **409** - ConflictError (duplicate/conflict)
- **422** - Pydantic validation error
- **500** - DatabaseError, AppException
- **503** - ExternalServiceError

## Tips

✅ **DO**:
- Use specific exception classes
- Include field names in ValidationError
- Provide clear, actionable messages
- Add context in details parameter

❌ **DON'T**:
- Use generic HTTPException
- Expose sensitive information
- Catch and re-raise unnecessarily
- Use wrong exception types

## Full Documentation

See `ERROR_HANDLING_GUIDE.md` for complete documentation and examples.
