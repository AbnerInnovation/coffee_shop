# Multi-Restaurant Support Setup Guide

This guide explains how to set up and use the multi-restaurant (multi-tenant) feature using subdomains.

## Overview

The application now supports multiple restaurants, each accessible via a unique subdomain. Each restaurant has its own isolated data including:
- Menu items and categories
- Orders and order items
- Tables
- Users (staff members)

## Architecture

### Database Schema
- **restaurants** table: Stores restaurant information (name, subdomain, settings)
- All main tables (users, menu_items, categories, orders, tables) have a `restaurant_id` foreign key
- Data is automatically filtered by restaurant context based on the subdomain

### Subdomain Routing
- Each restaurant is accessed via: `{subdomain}.yourdomain.com`
- Example: `restaurant1.example.com`, `coffeeshop2.example.com`
- The subdomain is extracted from the HTTP Host header
- Restaurant context is automatically injected into all API requests

## Setup Instructions

### 1. Run Database Migration

```bash
cd backend
alembic upgrade head
```

This will:
- Create the `restaurants` table
- Add `restaurant_id` columns to existing tables
- Create a default restaurant with subdomain "default"
- Migrate existing data to the default restaurant

### 2. Create New Restaurants (Admin Only)

Use the API to create new restaurants:

```bash
POST /api/v1/restaurants/
Authorization: Bearer {admin_token}

{
  "name": "My Coffee Shop",
  "subdomain": "mycoffee",
  "description": "Best coffee in town",
  "address": "123 Main St",
  "phone": "+1234567890",
  "email": "info@mycoffee.com",
  "timezone": "America/Los_Angeles",
  "currency": "USD",
  "tax_rate": 0.08
}
```

### 3. Configure DNS/Hosts

For local development, add entries to your hosts file:

**Windows:** `C:\Windows\System32\drivers\etc\hosts`
**Linux/Mac:** `/etc/hosts`

```
127.0.0.1 restaurant1.localhost
127.0.0.1 restaurant2.localhost
127.0.0.1 default.localhost
```

For production, configure DNS wildcard records:
```
*.yourdomain.com -> Your server IP
```

### 4. Update CORS Settings

Update `backend/app/main.py` to allow subdomain origins:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://*.localhost:3000",  # For local development
        "https://*.yourdomain.com"   # For production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## API Usage

### Restaurant Context

All API endpoints automatically filter data by the restaurant subdomain:

```bash
# Access restaurant1's menu
GET http://restaurant1.localhost:8000/api/v1/menu/items

# Access restaurant2's orders
GET http://restaurant2.localhost:8000/api/v1/orders
```

### Restaurant Management Endpoints (Admin Only)

```bash
# List all restaurants
GET /api/v1/restaurants/

# Get current restaurant info (public)
GET /api/v1/restaurants/current

# Get specific restaurant
GET /api/v1/restaurants/{id}

# Update restaurant
PUT /api/v1/restaurants/{id}

# Delete restaurant (WARNING: Cascades to all related data)
DELETE /api/v1/restaurants/{id}
```

## Frontend Integration

### 1. Detect Subdomain

Create a utility to extract the subdomain:

```typescript
// src/utils/subdomain.ts
export function getSubdomain(): string | null {
  const host = window.location.hostname;
  const parts = host.split('.');
  
  // For localhost development
  if (host.includes('localhost')) {
    const subdomain = parts[0];
    return subdomain !== 'localhost' ? subdomain : null;
  }
  
  // For production (subdomain.domain.com)
  if (parts.length >= 3) {
    return parts[0];
  }
  
  return null;
}

export function getApiBaseUrl(): string {
  const subdomain = getSubdomain();
  const protocol = window.location.protocol;
  const port = import.meta.env.VITE_API_PORT || '8000';
  
  if (subdomain) {
    return `${protocol}//${subdomain}.localhost:${port}`;
  }
  
  return `${protocol}//localhost:${port}`;
}
```

### 2. Configure Axios

Update your API client to use the subdomain-aware base URL:

```typescript
// src/api/client.ts
import axios from 'axios';
import { getApiBaseUrl } from '@/utils/subdomain';

const apiClient = axios.create({
  baseURL: getApiBaseUrl() + '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

export default apiClient;
```

### 3. Display Restaurant Info

Fetch and display current restaurant information:

```typescript
// src/composables/useRestaurant.ts
import { ref, onMounted } from 'vue';
import apiClient from '@/api/client';

export function useRestaurant() {
  const restaurant = ref(null);
  const loading = ref(true);
  
  const fetchRestaurant = async () => {
    try {
      const response = await apiClient.get('/restaurants/current');
      restaurant.value = response.data;
    } catch (error) {
      console.error('Failed to fetch restaurant:', error);
    } finally {
      loading.value = false;
    }
  };
  
  onMounted(fetchRestaurant);
  
  return { restaurant, loading, fetchRestaurant };
}
```

## Testing

### Local Testing

1. Start the backend:
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2. Start the frontend:
```bash
cd frontend
npm run dev -- --host
```

3. Access different restaurants:
- http://default.localhost:3000
- http://restaurant1.localhost:3000
- http://restaurant2.localhost:3000

### Creating Test Data

Use the seed script or API to create test restaurants and data:

```python
# backend/seed_restaurants.py
from app.db.base import SessionLocal
from app.models.restaurant import Restaurant

db = SessionLocal()

restaurants = [
    Restaurant(
        name="Coffee Shop 1",
        subdomain="coffee1",
        description="First coffee shop",
        timezone="America/Los_Angeles",
        currency="USD"
    ),
    Restaurant(
        name="Coffee Shop 2",
        subdomain="coffee2",
        description="Second coffee shop",
        timezone="America/New_York",
        currency="USD"
    ),
]

for restaurant in restaurants:
    db.add(restaurant)

db.commit()
```

## Security Considerations

1. **Data Isolation**: All queries automatically filter by `restaurant_id`
2. **User Access**: Users are associated with a specific restaurant
3. **Admin Access**: Only admin users can manage restaurants
4. **Subdomain Validation**: Invalid subdomains return 404 errors

## Troubleshooting

### "Restaurant not found" Error
- Verify the subdomain exists in the database
- Check the restaurant's `is_active` status
- Ensure DNS/hosts file is configured correctly

### CORS Issues
- Update CORS settings to allow subdomain origins
- Check that credentials are enabled

### Data Not Showing
- Verify the user's `restaurant_id` matches the subdomain
- Check that data has the correct `restaurant_id`

## Migration from Single Restaurant

If you have existing data:

1. Run the migration (creates default restaurant)
2. Existing data is automatically assigned to the default restaurant
3. Create new restaurants as needed
4. Optionally migrate specific data to new restaurants:

```sql
-- Move specific menu items to a new restaurant
UPDATE menu_items 
SET restaurant_id = (SELECT id FROM restaurants WHERE subdomain = 'newrestaurant')
WHERE id IN (1, 2, 3);
```

## Production Deployment

1. Configure wildcard SSL certificate for `*.yourdomain.com`
2. Set up DNS wildcard record
3. Update environment variables for production domains
4. Configure reverse proxy (nginx/Apache) to handle subdomains
5. Update CORS settings for production domains

Example nginx configuration:

```nginx
server {
    listen 80;
    server_name *.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```
