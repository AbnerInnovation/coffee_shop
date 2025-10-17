# SYSADMIN Role Implementation Guide

## Overview

A new **SYSADMIN** (System Administrator) role has been added to the Coffee Shop Admin system. This role has exclusive access to restaurant management endpoints, providing a clear separation between system-level administration and restaurant-level administration.

## Role Hierarchy

```
SYSADMIN (System Administrator)
  └─ Full system access
  └─ Manage all restaurants (create, read, update, delete)
  └─ All permissions of ADMIN + restaurant management

ADMIN (Restaurant Administrator)
  └─ Manage restaurant operations
  └─ Full access to menu, orders, tables, cash register
  └─ Cannot manage restaurants

STAFF
  └─ Day-to-day operations
  └─ Create/manage orders, tables, cash register

CUSTOMER
  └─ View-only access
  └─ View menu and their own orders
```

## Changes Made

### 1. User Model (`app/models/user.py`)
Added `SYSADMIN` to the `UserRole` enum:
```python
class UserRole(str, PyEnum):
    SYSADMIN = "sysadmin"  # NEW
    ADMIN = "admin"
    STAFF = "staff"
    CUSTOMER = "customer"
```

### 2. User Schema (`app/schemas/user.py`)
Updated the schema enum to match:
```python
class UserRole(str, Enum):
    SYSADMIN = "sysadmin"  # NEW
    ADMIN = "admin"
    STAFF = "staff"
    CUSTOMER = "customer"
```

### 3. Restaurant Endpoints (`app/api/routers/restaurants.py`)
- Changed `require_admin` dependency to `require_sysadmin`
- All restaurant management endpoints now require SYSADMIN role:
  - `GET /api/v1/restaurants/` - List all restaurants
  - `GET /api/v1/restaurants/{id}` - Get specific restaurant
  - `POST /api/v1/restaurants/` - Create restaurant
  - `PUT /api/v1/restaurants/{id}` - Update restaurant
  - `DELETE /api/v1/restaurants/{id}` - Delete restaurant

**Exception:** `GET /api/v1/restaurants/current` remains public (no auth required)

### 4. Authentication (`app/api/routers/auth.py`)
Added enhanced scopes for SYSADMIN users:
```python
if user.role == UserRole.SYSADMIN:
    scopes = [
        "read:items", 
        "write:items", 
        "read:orders", 
        "write:orders", 
        "admin", 
        "sysadmin", 
        "manage:restaurants"  # Exclusive to SYSADMIN
    ]
```

### 5. Database Migration
Created migration file: `migrations/versions/add_sysadmin_role.py`
- Adds 'sysadmin' to the user role ENUM in the database

## How to Use

### Step 1: Run the Migration

```bash
cd backend
alembic upgrade head
```

This will update the database to support the new SYSADMIN role.

### Step 2: Create a SYSADMIN User

**Option A: Use the secure script (Recommended)**
```bash
cd backend
SYSADMIN_EMAIL=admin@example.com SYSADMIN_PASSWORD=YourSecurePassword123! python create_sysadmin.py
```

**⚠️ SECURITY WARNING:** Never commit credentials to version control!

**Option B: Register via API**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "sysadmin@example.com",
    "password": "SecurePassword123!",
    "full_name": "System Administrator",
    "role": "sysadmin"
  }'
```

**Option C: Update existing user in database**
```sql
UPDATE users 
SET role = 'sysadmin' 
WHERE email = 'admin@example.com';
```

### Step 3: Login and Get Token

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=sysadmin@example.com&password=SecurePassword123!"
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "scopes": [
    "read:items",
    "write:items",
    "read:orders",
    "write:orders",
    "admin",
    "sysadmin",
    "manage:restaurants"
  ],
  "refresh_token": "..."
}
```

### Step 4: Access Restaurant Endpoints

```bash
# List all restaurants
curl -X GET "http://127.0.0.1:8000/api/v1/restaurants/" \
  -H "Authorization: Bearer YOUR_SYSADMIN_TOKEN"

# Create a new restaurant
curl -X POST "http://127.0.0.1:8000/api/v1/restaurants/" \
  -H "Authorization: Bearer YOUR_SYSADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Coffee Shop",
    "subdomain": "newshop",
    "address": "123 Main St",
    "phone": "555-0100",
    "email": "contact@newshop.com",
    "currency": "USD",
    "timezone": "America/New_York"
  }'
```

## Permission Matrix

| Endpoint | SYSADMIN | ADMIN | STAFF | CUSTOMER |
|----------|----------|-------|-------|----------|
| **Restaurant Management** |
| List restaurants | ✅ | ❌ | ❌ | ❌ |
| Get restaurant | ✅ | ❌ | ❌ | ❌ |
| Create restaurant | ✅ | ❌ | ❌ | ❌ |
| Update restaurant | ✅ | ❌ | ❌ | ❌ |
| Delete restaurant | ✅ | ❌ | ❌ | ❌ |
| Get current restaurant (public) | ✅ | ✅ | ✅ | ✅ |
| **Other Operations** |
| Menu management | ✅ | ✅ | ✅ | ❌ |
| Order management | ✅ | ✅ | ✅ | 👁️ |
| Table management | ✅ | ✅ | ✅ | ❌ |
| Cash register | ✅ | ✅ | ✅ | ❌ |

✅ = Full Access | 👁️ = Read Only | ❌ = No Access

## Error Responses

### Non-SYSADMIN trying to access restaurant endpoints:
```json
{
  "success": false,
  "error": {
    "message": "Only system administrators can perform this action",
    "type": "HTTPException",
    "status_code": 403
  }
}
```

### Unauthenticated request:
```json
{
  "detail": "Not authenticated"
}
```

## Security Considerations

### Critical Security Rules

1. **NEVER commit credentials to Git**
   - The `create_sysadmin.py` script now uses environment variables
   - Never hardcode passwords in any file
   - Check Git history if credentials were previously committed

2. **SYSADMIN users should be limited**
   - Only create SYSADMIN accounts for trusted personnel
   - Use strong, unique passwords (minimum 12 characters)
   - Enable 2FA if available

3. **Restaurant isolation**
   - SYSADMIN can access all restaurants
   - ADMIN/STAFF are scoped to their restaurant
   - Review access regularly

4. **Audit logging**
   - Consider implementing audit logs for SYSADMIN actions
   - Monitor restaurant creation/deletion
   - Track configuration changes

5. **Password management**
   - Use a password manager for SYSADMIN credentials
   - Rotate passwords regularly (every 90 days)
   - Never share SYSADMIN credentials
   - Change default passwords immediately

6. **Environment variables**
   - Store credentials in `.env` files (already gitignored)
   - Use different credentials for dev/staging/production
   - Never log or display passwords

## Testing

### Test SYSADMIN Access
```bash
# Should succeed with SYSADMIN token
curl -X GET "http://127.0.0.1:8000/api/v1/restaurants/" \
  -H "Authorization: Bearer SYSADMIN_TOKEN"
```

### Test ADMIN Rejection
```bash
# Should fail with 403 Forbidden
curl -X GET "http://127.0.0.1:8000/api/v1/restaurants/" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

## Migration Rollback

If you need to rollback this change:

```bash
cd backend
alembic downgrade -1
```

**Warning:** This will fail if any users have the SYSADMIN role. You must first change those users to a different role.

## Files Modified

1. `backend/app/models/user.py` - Added SYSADMIN to UserRole enum
2. `backend/app/schemas/user.py` - Added SYSADMIN to schema enum
3. `backend/app/api/routers/restaurants.py` - Changed require_admin to require_sysadmin
4. `backend/app/api/routers/auth.py` - Added SYSADMIN scopes
5. `backend/migrations/versions/add_sysadmin_role.py` - Database migration

## Support

For questions or issues with the SYSADMIN role implementation, refer to:
- This documentation
- API documentation at `/docs` endpoint
- Error handling guide in `ERROR_HANDLING_GUIDE.md`
