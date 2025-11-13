# Coffee Shop Admin - Project Guide

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Tech Stack](#tech-stack)
3. [Architecture](#architecture)
4. [Development Standards](#development-standards)
5. [Project Structure](#project-structure)
6. [Key Features](#key-features)
7. [Business Rules](#business-rules)
8. [Error Handling](#error-handling)
9. [Testing Strategy](#testing-strategy)
10. [Git Workflow](#git-workflow)
11. [Deployment](#deployment)
12. [Common Patterns](#common-patterns)

---

## 🎯 Project Overview

**Coffee Shop Admin** is a multi-tenant SaaS platform for restaurant management with subscription-based access control.

### Mission
Cloud-based POS and management system for restaurants, cafes, and food service businesses.

### Key Differentiators
- **Multi-tenant architecture** with subdomain isolation
- **Subscription-based** feature access with tiered plans
- **Role-based permissions** (SYSADMIN, ADMIN, STAFF, CUSTOMER)
- **Real-time kitchen display** system
- **Comprehensive reporting** and analytics

---

## 🛠️ Tech Stack

### Frontend
```yaml
Framework: Vue 3 (Composition API with <script setup>)
Language: TypeScript
State Management: Pinia
Routing: Vue Router
Styling: TailwindCSS
HTTP Client: Axios
Icons: Heroicons
Charts: Chart.js + vue-chartjs
i18n: vue-i18n (Spanish primary)
Build Tool: Vite
```

### Backend
```yaml
Framework: FastAPI (Python 3.9+)
ORM: SQLAlchemy
Validation: Pydantic
Migrations: Alembic
Database: MySQL (via PyMySQL)
Authentication: JWT (HTTPOnly cookies)
Security: Bcrypt (password hashing)
```

### DevOps
```yaml
Version Control: Git
Package Manager (Frontend): npm
Package Manager (Backend): pip + venv
Environment: .env files
```

---

## 🏗️ Architecture

### Multi-Tenant Architecture
```
┌─────────────────────────────────────────┐
│         Main Domain (example.com)       │
│         - SYSADMIN Dashboard            │
│         - Restaurant Management         │
│         - Subscription Management       │
└─────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
┌───────▼──────┐       ┌───────▼──────┐
│ restaurant1  │       │ restaurant2  │
│ .example.com │       │ .example.com │
│              │       │              │
│ - Menu       │       │ - Menu       │
│ - Orders     │       │ - Orders     │
│ - Tables     │       │ - Tables     │
│ - Reports    │       │ - Reports    │
└──────────────┘       └──────────────┘
```

### Data Isolation
- Each restaurant has a unique `restaurant_id`
- All queries filtered by `restaurant_id` (except SYSADMIN)
- Subdomain extracted from request and validated
- Users assigned to specific restaurant

### Role Hierarchy
```
SYSADMIN (Global)
    └── Can access all restaurants
    └── Manages subscriptions and plans
    
ADMIN (Restaurant-level)
    └── Full access to their restaurant
    └── User management
    └── Subscription management
    
STAFF (Restaurant-level)
    └── staff_type: waiter, cashier, kitchen
    └── Limited access based on type
    
CUSTOMER (Restaurant-level)
    └── Order history only
```

---

## 📐 Development Standards

### Code Style

#### Frontend (TypeScript/Vue)
```typescript
// ✅ Naming: camelCase for variables/functions
const userName = "John";
const orderTotal = 100;

// ✅ PascalCase for components/classes
class OrderService {}
const MyComponent = defineComponent({});

// ✅ Composables: use prefix
function useOrderFilters() {}
function useAuth() {}

// ✅ Constants: UPPER_SNAKE_CASE
const MAX_RETRIES = 3;
const API_BASE_URL = "https://api.example.com";

// ✅ Interfaces/Types: PascalCase
interface Order {}
type OrderStatus = 'pending' | 'completed';
```

#### Backend (Python)
```python
# ✅ Naming: snake_case for variables/functions
user_name = "John"
order_total = 100

# ✅ PascalCase for classes
class OrderService:
    pass

class UserModel(Base):
    pass

# ✅ Constants: UPPER_SNAKE_CASE
MAX_RETRIES = 3
API_BASE_URL = "https://api.example.com"

# ✅ Private methods: _prefix
def _internal_helper():
    pass
```

### File Organization

#### Frontend Structure
```
frontend/src/
├── assets/          # Images, fonts, static files
├── components/      # Vue components
│   ├── ui/         # Reusable UI components (BaseButton, DropdownMenu)
│   ├── layout/     # Layout components (AppNavbar, Sidebar)
│   └── [feature]/  # Feature-specific components
├── composables/     # Reusable composition functions
│   ├── useAuth.ts
│   ├── useOrderFilters.ts
│   └── usePermissions.ts
├── locales/         # i18n translation files
│   └── es.json
├── services/        # API service layer
│   ├── api.ts      # Axios instance
│   ├── authService.ts
│   └── orderService.ts
├── stores/          # Pinia stores
│   ├── auth.ts
│   ├── menu.ts
│   └── orders.ts
├── utils/           # Helper functions
│   ├── permissions.ts
│   ├── validators.ts
│   └── orderHelpers.ts
├── views/           # Page components (routes)
│   ├── DashboardView.vue
│   ├── OrdersView.vue
│   └── MenuView.vue
├── App.vue          # Root component
├── main.ts          # App entry point
└── routes.ts        # Route definitions
```

#### Backend Structure
```
backend/
├── app/
│   ├── api/
│   │   ├── routers/      # API endpoints
│   │   │   ├── auth.py
│   │   │   ├── orders.py
│   │   │   └── menu.py
│   │   └── deps.py       # Dependencies (get_current_user, etc.)
│   ├── core/
│   │   ├── config.py     # Configuration
│   │   ├── security.py   # Auth, hashing
│   │   ├── exceptions.py # Custom exceptions
│   │   └── validators.py # Centralized validators
│   ├── db/
│   │   ├── base.py       # Base model
│   │   └── session.py    # DB session
│   ├── middleware/
│   │   ├── restaurant.py # Subdomain extraction
│   │   └── subscription_limits.py
│   ├── models/           # SQLAlchemy models
│   │   ├── user.py
│   │   ├── order.py
│   │   └── menu.py
│   ├── schemas/          # Pydantic schemas
│   │   ├── user.py
│   │   ├── order.py
│   │   └── menu.py
│   ├── services/         # Business logic
│   │   ├── user.py
│   │   ├── order.py
│   │   └── subscription_service.py
│   └── main.py           # FastAPI app
├── alembic/              # Database migrations
│   └── versions/
├── .env                  # Environment variables
├── requirements.txt      # Python dependencies
└── alembic.ini          # Alembic configuration
```

---

## 🎯 Key Features

### 1. Menu Management
- **CRUD operations** for menu items
- **Categories** with visibility control
- **Ingredients system:**
  - Ingredient options (e.g., Milk: Normal, Almond, Oat)
  - Removable ingredients (e.g., Remove onions)
  - Copy ingredients from other products
- **Variants** (sizes, types)
- **Pricing** with discount support
- **Availability** toggle

### 2. Order Management
- **Order types:** Dine-in, Takeout, Delivery
- **Multiple diners** per order
- **Order states:** Pending → Preparing → Ready → Completed
- **Payment tracking:** Paid/Unpaid, payment methods
- **Special instructions** per item
- **Add items** to existing orders
- **Kitchen display** with real-time updates

### 3. Table Management
- **Table CRUD** with capacity
- **Occupancy status** (Available/Occupied)
- **Location tracking** (Inside, Patio, Bar)
- **Order assignment** to tables

### 4. Cash Register
- **Sessions** with open/close times
- **Opening/closing balance**
- **Transaction tracking**
- **Reports** per session
- **Cashier isolation** (cashiers see only their sessions)

### 5. Reports & Analytics
- **Sales totals** (day, week, month)
- **Top products** with quantities and revenue
- **Payment method breakdown**
- **Average ticket** calculation
- **Sales trends** (charts)
- **Inventory alerts**
- **Export to CSV**

### 6. User Management
- **CRUD operations** for users
- **Role assignment** (ADMIN, STAFF, CUSTOMER)
- **Staff types** (waiter, cashier, kitchen)
- **Subscription limit** validation
- **Soft delete** (deleted_at field)

### 7. Subscription Management
- **Tiered plans:** Trial, Starter, Básico, Pro, Business, Enterprise
- **Feature limits:** Users, tables, products, categories
- **Module access:** Kitchen, Ingredients, Reports
- **Add-ons:** Extra users, tables, products
- **Usage tracking** with progress bars
- **Upgrade/downgrade** with validation
- **Trial creation** automatic on restaurant creation

---

## 📜 Business Rules

### Critical Rules

#### 1. Multi-Tenant Isolation
```python
# ✅ ALWAYS filter by restaurant_id
orders = db.query(Order).filter(
    Order.restaurant_id == current_restaurant.id
).all()

# ❌ NEVER query without restaurant filter (except SYSADMIN)
orders = db.query(Order).all()  # WRONG!
```

#### 2. Subscription Limits
```python
# ✅ Check limits BEFORE creating resources
check_table_limit(db, restaurant_id)
table = create_table(data)

# ❌ NEVER create without checking limits
table = create_table(data)  # WRONG!
```

#### 3. Soft Delete
```python
# ✅ Use deleted_at for deletion
user.deleted_at = datetime.now(timezone.utc)

# ✅ Filter out deleted records
users = db.query(User).filter(User.deleted_at.is_(None)).all()

# ❌ NEVER hard delete
db.delete(user)  # WRONG!
```

#### 4. Price Storage
```python
# ✅ Store prices in cents (integer)
price_cents = 1250  # $12.50

# ✅ Display with formatting
price_display = f"${price_cents / 100:.2f}"

# ❌ NEVER store as float
price = 12.50  # WRONG! Floating point errors
```

#### 5. Order State Transitions
```
Pending → Preparing → Ready → Completed
   ↓          ↓         ↓
   └──────────┴─────────┴──→ Cancelled
```

```python
# ✅ Valid transitions
if current_state == 'pending':
    new_state = 'preparing' or 'cancelled'
elif current_state == 'preparing':
    new_state = 'ready' or 'cancelled'
# etc.

# ❌ Invalid transitions
if current_state == 'completed':
    new_state = 'pending'  # WRONG! Can't reopen completed orders
```

#### 6. Authentication
```python
# ✅ Use HTTPOnly cookies for tokens
response.set_cookie(
    key="access_token",
    value=token,
    httponly=True,
    secure=True,  # Production only
    samesite="lax"
)

# ✅ Validate subdomain on login
if user.restaurant_id != restaurant.id:
    raise UnauthorizedError("Access denied")
```

---

## 🚨 Error Handling

### Custom Exceptions (Backend)
```python
# backend/app/core/exceptions.py
class AppException(Exception):
    """Base exception - 500"""
    
class ResourceNotFoundError(AppException):
    """Resource not found - 404"""
    
class ValidationError(AppException):
    """Validation failed - 400"""
    
class UnauthorizedError(AppException):
    """Authentication required - 401"""
    
class ForbiddenError(AppException):
    """Insufficient permissions - 403"""
```

### Usage Pattern
```python
# ✅ Raise specific exceptions
if not order:
    raise ResourceNotFoundError(f"Order {order_id} not found")

if not has_permission(user, 'edit_menu'):
    raise ForbiddenError("You don't have permission to edit menu")

# ✅ Handle in global exception handler (main.py)
@app.exception_handler(ResourceNotFoundError)
async def handle_not_found(request, exc):
    return JSONResponse(
        status_code=404,
        content={"success": False, "error": {"message": str(exc)}}
    )
```

### Frontend Error Handling
```typescript
// ✅ Always use try-catch for async operations
try {
  const order = await orderService.createOrder(data);
  toast.success(t('app.messages.order_created'));
  router.push('/orders');
} catch (error) {
  console.error('Order creation failed:', error);
  toast.error(t('app.errors.order_creation_failed'));
}

// ✅ Handle specific error codes
catch (error: any) {
  if (error.response?.status === 403) {
    toast.error(t('app.errors.subscription_limit_reached'));
  } else if (error.response?.status === 404) {
    toast.error(t('app.errors.resource_not_found'));
  } else {
    toast.error(t('app.errors.generic_error'));
  }
}
```

---

## 🧪 Testing Strategy

### Test Pyramid
```
        /\
       /E2E\      10% - Critical user flows
      /------\
     /  INT   \   20% - Component interactions
    /----------\
   /   UNIT     \ 70% - Functions, composables, services
  /--------------\
```

### What to Test

#### Frontend
```typescript
// ✅ Composables
describe('useOrderFilters', () => {
  it('should filter orders by status', () => {
    const orders = ref([...]);
    const status = ref('pending');
    const { filteredOrders } = useOrderFilters(orders, status);
    
    expect(filteredOrders.value).toHaveLength(2);
  });
});

// ✅ Helper functions
describe('transformOrderToLocal', () => {
  it('should transform API order to local format', () => {
    const apiOrder = { ... };
    const result = transformOrderToLocal(apiOrder, t);
    
    expect(result.statusText).toBe('Pendiente');
  });
});

// ✅ Components (user interactions)
describe('OrdersView', () => {
  it('should display orders list', async () => {
    const wrapper = mount(OrdersView);
    await flushPromises();
    
    expect(wrapper.findAll('.order-card')).toHaveLength(3);
  });
});
```

#### Backend
```python
# ✅ Services (business logic)
def test_create_order_validates_subscription_limits():
    with pytest.raises(ValidationError):
        create_order(restaurant_with_max_orders, order_data)

# ✅ API endpoints
def test_get_orders_filters_by_restaurant(client, auth_headers):
    response = client.get("/api/v1/orders", headers=auth_headers)
    
    assert response.status_code == 200
    assert all(o['restaurant_id'] == 1 for o in response.json())

# ✅ Models
def test_order_calculates_total_correctly():
    order = Order(items=[...])
    
    assert order.total == 2500  # $25.00
```

### Testing Tools
```yaml
Frontend:
  - Vitest (unit/integration)
  - Vue Test Utils (component testing)
  - Playwright (E2E)
  
Backend:
  - Pytest (unit/integration)
  - pytest-asyncio (async tests)
  - pytest-cov (coverage)
```

---

## 🔄 Git Workflow

### Commit Message Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code refactoring
- `docs`: Documentation
- `style`: Formatting
- `test`: Tests
- `chore`: Maintenance

### Examples
```bash
feat(orders): add multiple diners support

- Created useMultipleDiners composable
- Added diner selection UI
- Updated order creation logic

Closes #123

---

fix(auth): resolve Safari cookie authentication issue

Safari was blocking localStorage access in private mode.
Implemented triple fallback: cookies → memory → storage.

Fixes #456

---

refactor(menu): extract item grouping to composable

Reduced NewOrderModal from 960 to 718 lines (-25%).
Created useItemGrouping composable for reusability.
```

### Branch Naming
```bash
feature/add-multiple-diners
fix/safari-cookie-bug
refactor/menu-item-grouping
hotfix/payment-calculation
docs/update-readme
```

### Workflow
```bash
# 1. Create feature branch
git checkout -b feature/add-reports

# 2. Make changes and commit
git add .
git commit -m "feat(reports): add sales analytics dashboard"

# 3. Push to remote
git push origin feature/add-reports

# 4. Create Pull Request
# 5. Code review
# 6. Merge to main
```

---

## 🚀 Deployment

### Environment Variables

#### Frontend (.env)
```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=Cloud Restaurant Admin
```

#### Backend (.env)
```bash
# Database
DATABASE_URL=mysql+pymysql://root:@localhost/coffee_shop

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=http://localhost:5173,https://example.com
```

### Database Migrations

#### Check Current State
```bash
cd backend
venv\Scripts\activate
alembic current
alembic heads
```

#### Create Migration
```bash
# 1. Check current head
alembic current

# 2. Create migration
alembic revision -m "add_subscription_system"

# 3. Edit migration file
# Set down_revision to current head

# 4. Run migration
alembic upgrade head
```

#### Rollback
```bash
# Rollback one version
alembic downgrade -1

# Rollback to specific version
alembic downgrade abc123
```

### Running the Application

#### Backend
```bash
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## 🎨 Common Patterns

### 1. API Service Pattern
```typescript
// services/orderService.ts
import api from './api';

export const orderService = {
  async getOrders(): Promise<Order[]> {
    return await api.get('/orders');
  },
  
  async createOrder(data: CreateOrderRequest): Promise<Order> {
    return await api.post('/orders', data);
  },
  
  async updateOrder(id: number, data: UpdateOrderRequest): Promise<Order> {
    return await api.put(`/orders/${id}`, data);
  },
};
```

### 2. Composable Pattern
```typescript
// composables/useOrderFilters.ts
export function useOrderFilters(
  orders: Ref<Order[]>,
  status: Ref<OrderStatus>
) {
  const filteredOrders = computed(() => {
    return orders.value.filter(o => o.status === status.value);
  });
  
  return { filteredOrders };
}

// Usage in component
const { filteredOrders } = useOrderFilters(orders, selectedStatus);
```

### 3. Helper Function Pattern
```typescript
// utils/orderHelpers.ts
export function transformOrderToLocal(order: any, t: any): OrderWithLocalFields {
  return {
    ...order,
    statusText: getStatusText(order.status, t),
    totalFormatted: formatCurrency(order.total),
  };
}
```

### 4. Store Pattern (Pinia)
```typescript
// stores/orders.ts
export const useOrdersStore = defineStore('orders', () => {
  const orders = ref<Order[]>([]);
  const loading = ref(false);
  
  async function fetchOrders() {
    loading.value = true;
    try {
      orders.value = await orderService.getOrders();
    } finally {
      loading.value = false;
    }
  }
  
  return { orders, loading, fetchOrders };
});
```

### 5. Backend Service Pattern
```python
# services/order_service.py
def create_order(
    db: Session,
    order_data: OrderCreate,
    current_user: User,
    restaurant_id: int
) -> Order:
    # Validate subscription limits
    check_order_limit(db, restaurant_id)
    
    # Create order
    order = Order(
        restaurant_id=restaurant_id,
        user_id=current_user.id,
        **order_data.dict()
    )
    
    db.add(order)
    db.commit()
    db.refresh(order)
    
    return order
```

### 6. Validation Pattern
```python
# core/validators.py
def validate_email(email: str) -> str:
    """Validate and sanitize email"""
    email = email.strip().lower()
    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
        raise ValueError("Invalid email format")
    return email

# Usage in schema
class UserCreate(BaseModel):
    email: str
    
    @validator('email')
    def validate_email_field(cls, v):
        return validate_email(v)
```

### 7. Permission Check Pattern
```typescript
// utils/permissions.ts
export function canEditMenu(user: User | null): boolean {
  if (!user) return false;
  return user.role === 'admin' || user.role === 'sysadmin';
}

// Usage in component
<button v-if="canEditMenu(authStore.user)" @click="editItem">
  Edit
</button>
```

### 8. Translation Pattern
```typescript
// Always use translation keys
<h1>{{ t('app.views.orders.title') }}</h1>

// Never hardcode text
<h1>Órdenes</h1> <!-- WRONG! -->

// Key structure: app.section.subsection.key
{
  "app": {
    "views": {
      "orders": {
        "title": "Órdenes",
        "new_order": "Nueva Orden"
      }
    }
  }
}
```

---

## 📚 Additional Resources

### Documentation Files
- `agents.md` - Development standards and AI collaboration guidelines
- `README.md` - Project setup and installation
- `doc/*.md` - Feature-specific documentation
- `MIGRATION_GUIDES.md` - Database migration guides

### Key Memories
- SOLID principles implementation
- Subscription system with limits
- Multi-tenant architecture
- Error handling patterns
- Testing strategies

### External References
- [Vue 3 Documentation](https://vuejs.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pinia Documentation](https://pinia.vuejs.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [TailwindCSS Documentation](https://tailwindcss.com/)

---

## 🎯 Quick Reference

### Start Development
```bash
# Backend
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload

# Frontend
cd frontend
npm run dev
```

### Run Migrations
```bash
cd backend
venv\Scripts\activate
alembic upgrade head
```

### Create New Feature
```bash
git checkout -b feature/my-feature
# Make changes
git commit -m "feat(scope): description"
git push origin feature/my-feature
```

### Common Commands
```bash
# Frontend
npm install          # Install dependencies
npm run dev          # Development server
npm run build        # Production build
npm run lint         # Lint code

# Backend
pip install -r requirements.txt  # Install dependencies
alembic upgrade head             # Run migrations
pytest                           # Run tests
```

---

**Last Updated:** November 2025  
**Project Version:** 1.0.0  
**Maintainer:** Development Team
