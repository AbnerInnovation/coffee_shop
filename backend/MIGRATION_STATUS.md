# Error Handling Migration Status

## ✅ Completed Routers

### 1. auth.py - COMPLETE
- ✅ Replaced all `HTTPException` with appropriate custom exceptions
- ✅ `ValidationError` for invalid input
- ✅ `UnauthorizedError` for authentication failures
- ✅ `ConflictError` for duplicate users

### 2. tables.py - COMPLETE
- ✅ Replaced all `HTTPException` with appropriate custom exceptions
- ✅ `ResourceNotFoundError` for missing tables
- ✅ `ConflictError` for duplicate table numbers and active orders
- ✅ `ValidationError` for invalid input

### 3. orders.py - COMPLETE
- ✅ Replaced all `HTTPException` with appropriate custom exceptions
- ✅ `ResourceNotFoundError` for missing orders, tables, menu items, order items
- ✅ `ValidationError` for invalid payment methods and status
- ✅ `ConflictError` for already paid orders
- ✅ `DatabaseError` for database operation failures

## 🔄 Remaining Routers

### 4. menu.py - PENDING
**HTTPException Count:** 23
**Common Patterns:**
- 404: Menu item not found
- 403: Permission denied (admin only)
- 400: Invalid input/validation
- 409: Duplicate menu items

**Recommended Replacements:**
```python
# 404 errors
raise ResourceNotFoundError("MenuItem", item_id)
raise ResourceNotFoundError("MenuItemVariant", variant_id)

# 403 errors
raise ForbiddenError("Admin access required", required_permission="admin")

# 400 errors
raise ValidationError("Invalid price", field="price")

# 409 errors
raise ConflictError("Menu item already exists", resource="MenuItem")
```

### 5. cash_register.py - PENDING
**HTTPException Count:** 24
**Common Patterns:**
- 404: Session/transaction not found
- 403: Permission denied
- 400: Invalid amounts/validation
- 409: Session already closed/conflicts

**Recommended Replacements:**
```python
# 404 errors
raise ResourceNotFoundError("CashRegisterSession", session_id)
raise ResourceNotFoundError("Transaction", transaction_id)

# 403 errors
raise ForbiddenError("Only session owner can close it", required_permission="session_owner")

# 400 errors
raise ValidationError("Amount must be positive", field="amount")

# 409 errors
raise ConflictError("Session is already closed", resource="CashRegisterSession")
```

### 6. categories.py - PENDING
**HTTPException Count:** 7
**Common Patterns:**
- 404: Category not found
- 409: Duplicate category names

**Recommended Replacements:**
```python
# 404 errors
raise ResourceNotFoundError("Category", category_id)

# 409 errors
raise ConflictError("Category name already exists", resource="Category")
```

### 7. restaurants.py - PENDING
**HTTPException Count:** 7
**Common Patterns:**
- 404: Restaurant not found
- 403: Permission denied
- 409: Duplicate restaurant

**Recommended Replacements:**
```python
# 404 errors
raise ResourceNotFoundError("Restaurant", restaurant_id)

# 403 errors
raise ForbiddenError("Admin access required", required_permission="admin")

# 409 errors
raise ConflictError("Restaurant already exists", resource="Restaurant")
```

### 8. users.py - PENDING
**HTTPException Count:** 5
**Common Patterns:**
- 404: User not found
- 403: Permission denied

**Recommended Replacements:**
```python
# 404 errors
raise ResourceNotFoundError("User", user_id)

# 403 errors
raise ForbiddenError("Admin access required", required_permission="admin")
```

### 9. user.py - PENDING
**HTTPException Count:** 1
**Common Patterns:**
- 404: User not found

**Recommended Replacements:**
```python
# 404 errors
raise ResourceNotFoundError("User", user_id)
```

## Migration Checklist

For each router file:

1. ✅ Add import statement:
   ```python
   from ...core.exceptions import (
       ResourceNotFoundError,
       ValidationError,
       UnauthorizedError,
       ForbiddenError,
       ConflictError,
       DatabaseError
   )
   ```

2. ✅ Remove `HTTPException` from imports (if not used elsewhere)

3. ✅ Replace each `HTTPException` with appropriate custom exception:
   - 404 → `ResourceNotFoundError(resource_type, identifier)`
   - 400 → `ValidationError(message, field=field_name)`
   - 401 → `UnauthorizedError(message)`
   - 403 → `ForbiddenError(message, required_permission=permission)`
   - 409 → `ConflictError(message, resource=resource_type)`
   - 500 → `DatabaseError(message, operation=operation_type)`

4. ✅ Update error messages to be more descriptive and user-friendly

5. ✅ Test the endpoint to ensure errors are handled correctly

## Quick Migration Commands

To find all HTTPException usage in a file:
```bash
grep -n "HTTPException" backend/app/api/routers/menu.py
```

To count HTTPExceptions:
```bash
grep -c "HTTPException" backend/app/api/routers/*.py
```

## Testing After Migration

1. Test each endpoint with invalid data
2. Verify error responses match the new format
3. Check logs for proper error logging
4. Ensure status codes are correct
5. Verify error messages are user-friendly

## Benefits After Migration

- ✅ Consistent error responses across all endpoints
- ✅ Better error messages with context
- ✅ Improved logging with structured information
- ✅ Easier debugging
- ✅ Type-safe error handling
- ✅ Better API documentation
