# Error Handling Migration - Complete Guide

## ✅ Completed Migrations (5/9 routers)

### 1. ✅ auth.py - COMPLETE
**Changes Made:**
- Replaced 8 HTTPExceptions with custom exceptions
- `ValidationError` for invalid input and inactive accounts
- `UnauthorizedError` for authentication failures
- `ConflictError` for duplicate users

### 2. ✅ tables.py - COMPLETE
**Changes Made:**
- Replaced 8 HTTPExceptions with custom exceptions
- `ResourceNotFoundError` for missing tables
- `ConflictError` for duplicate table numbers and active orders

### 3. ✅ orders.py - COMPLETE
**Changes Made:**
- Replaced 20 HTTPExceptions with custom exceptions
- `ResourceNotFoundError` for missing orders, tables, menu items, order items
- `ValidationError` for invalid payment methods and status
- `ConflictError` for already paid orders
- `DatabaseError` for database operation failures

### 4. ✅ user.py - COMPLETE
**Changes Made:**
- Removed unused HTTPException import (no exceptions used)

### 5. ✅ categories.py - COMPLETE
**Changes Made:**
- Replaced 7 HTTPExceptions with custom exceptions
- `ResourceNotFoundError` for missing categories
- `ValidationError` for invalid input
- `ConflictError` for duplicate categories and categories with menu items

## 🔄 Remaining Migrations (4/9 routers)

### 6. menu.py - PENDING (23 HTTPExceptions)

**Step-by-step migration:**

1. **Update imports:**
```python
# Change this:
from fastapi import APIRouter, Depends, HTTPException, status

# To this:
from fastapi import APIRouter, Depends, status
from app.core.exceptions import (
    ResourceNotFoundError,
    ValidationError,
    ForbiddenError,
    ConflictError
)
```

2. **Replace permission checks (403 errors):**
```python
# OLD:
def check_admin(user: User):
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

# NEW:
def check_admin(user: User):
    if user.role != UserRole.ADMIN:
        raise ForbiddenError("Admin access required", required_permission="admin")
```

3. **Replace 404 errors:**
```python
# OLD:
if not db_item:
    raise HTTPException(status_code=404, detail="Menu item not found")

# NEW:
if not db_item:
    raise ResourceNotFoundError("MenuItem", item_id)
```

4. **Replace 400 validation errors:**
```python
# OLD:
raise HTTPException(status_code=400, detail="Invalid price")

# NEW:
raise ValidationError("Price must be greater than 0", field="price")
```

5. **Replace 409 conflict errors:**
```python
# OLD:
raise HTTPException(status_code=409, detail="Menu item already exists")

# NEW:
raise ConflictError("Menu item with this name already exists", resource="MenuItem")
```

### 7. cash_register.py - PENDING (24 HTTPExceptions)

**Common patterns to replace:**

```python
# Import at top:
from ...core.exceptions import (
    ResourceNotFoundError,
    ValidationError,
    ForbiddenError,
    ConflictError,
    DatabaseError
)

# Session not found (404):
raise ResourceNotFoundError("CashRegisterSession", session_id)

# Transaction not found (404):
raise ResourceNotFoundError("Transaction", transaction_id)

# Permission denied (403):
raise ForbiddenError("Only session owner can close it", required_permission="session_owner")

# Invalid amounts (400):
raise ValidationError("Amount must be positive", field="amount")

# Session already closed (409):
raise ConflictError("Session is already closed", resource="CashRegisterSession")

# Database errors (500):
raise DatabaseError("Failed to create transaction", operation="insert")
```

### 8. restaurants.py - PENDING (7 HTTPExceptions)

**Common patterns:**

```python
# Import:
from ...core.exceptions import ResourceNotFoundError, ForbiddenError, ConflictError

# Restaurant not found (404):
raise ResourceNotFoundError("Restaurant", restaurant_id)

# Permission denied (403):
raise ForbiddenError("Admin access required", required_permission="admin")

# Duplicate restaurant (409):
raise ConflictError("Restaurant with this subdomain already exists", resource="Restaurant")
```

### 9. users.py - PENDING (5 HTTPExceptions)

**Common patterns:**

```python
# Import:
from ...core.exceptions import ResourceNotFoundError, ForbiddenError

# User not found (404):
raise ResourceNotFoundError("User", user_id)

# Permission denied (403):
raise ForbiddenError("Admin access required", required_permission="admin")
```

## Quick Migration Template

For each router file, follow these steps:

### Step 1: Update Imports
```python
# Remove HTTPException from imports
from fastapi import APIRouter, Depends, status  # Remove HTTPException

# Add custom exceptions
from ...core.exceptions import (
    ResourceNotFoundError,
    ValidationError,
    UnauthorizedError,
    ForbiddenError,
    ConflictError,
    DatabaseError
)
```

### Step 2: Replace Each HTTPException

Use this decision tree:

```
Is it a 404 error (not found)?
├─ YES → ResourceNotFoundError(resource_type, identifier)
└─ NO → Continue...

Is it a 400 error (bad request/validation)?
├─ YES → Is it a duplicate/conflict?
│   ├─ YES → ConflictError(message, resource=type)
│   └─ NO → ValidationError(message, field=field_name)
└─ NO → Continue...

Is it a 401 error (unauthorized)?
├─ YES → UnauthorizedError(message)
└─ NO → Continue...

Is it a 403 error (forbidden)?
├─ YES → ForbiddenError(message, required_permission=permission)
└─ NO → Continue...

Is it a 409 error (conflict)?
├─ YES → ConflictError(message, resource=type)
└─ NO → Continue...

Is it a 500 error (server error)?
├─ YES → DatabaseError(message, operation=operation_type)
└─ NO → AppException(message, status_code=code)
```

### Step 3: Improve Error Messages

Make messages more descriptive and user-friendly:

```python
# OLD:
raise HTTPException(status_code=404, detail="Not found")

# NEW:
raise ResourceNotFoundError("MenuItem", item_id)
# Returns: "MenuItem with identifier '123' not found"

# OLD:
raise HTTPException(status_code=400, detail="Invalid")

# NEW:
raise ValidationError("Price must be greater than 0", field="price")
# Returns structured error with field information
```

## Testing After Migration

### 1. Test each endpoint with invalid data:
```bash
# Test 404 errors
curl -X GET http://localhost:8000/api/v1/menu/items/99999

# Test 400 errors
curl -X POST http://localhost:8000/api/v1/menu/items \
  -H "Content-Type: application/json" \
  -d '{"name": "", "price": -10}'

# Test 403 errors (as non-admin user)
curl -X DELETE http://localhost:8000/api/v1/menu/items/1 \
  -H "Authorization: Bearer <non-admin-token>"
```

### 2. Verify error response format:
```json
{
  "success": false,
  "error": {
    "message": "MenuItem with identifier '123' not found",
    "type": "ResourceNotFoundError",
    "status_code": 404,
    "resource": "MenuItem",
    "identifier": "123"
  }
}
```

### 3. Check logs:
- 4xx errors should log as WARNING
- 5xx errors should log as ERROR
- All errors should include request context

## Verification Checklist

For each migrated router:

- [ ] All HTTPException imports removed (or kept if used elsewhere)
- [ ] Custom exception imports added
- [ ] All HTTPException raises replaced
- [ ] Error messages are descriptive and user-friendly
- [ ] Field names included in ValidationError where applicable
- [ ] Resource types included in ResourceNotFoundError
- [ ] Permission names included in ForbiddenError
- [ ] Tested with invalid data
- [ ] Error responses match expected format
- [ ] Logs show proper levels and context

## Benefits Summary

After completing all migrations:

✅ **Consistency**: All endpoints return errors in the same format
✅ **Better UX**: Clear, actionable error messages
✅ **Easier Debugging**: Structured errors with context
✅ **Better Logging**: Appropriate log levels and full context
✅ **Type Safety**: IDE support and autocomplete
✅ **Security**: No sensitive information in errors
✅ **Maintainability**: Centralized error handling logic

## Next Steps

1. Complete remaining router migrations (menu.py, cash_register.py, restaurants.py, users.py)
2. Run full test suite to verify all endpoints
3. Update API documentation if needed
4. Monitor logs in production for any issues
5. Consider adding more specific exception types if patterns emerge

## Support

- **Documentation**: See `ERROR_HANDLING_GUIDE.md` for detailed usage
- **Examples**: See `EXCEPTION_USAGE_EXAMPLE.py` for real-world patterns
- **Quick Reference**: See `EXCEPTION_QUICK_REFERENCE.md` for common cases
- **Tests**: See `tests/test_error_handling.py` for testing patterns
