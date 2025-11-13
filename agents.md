# `AGENTS.MD` — Development Standards & Context

## 1. Mission

The developer is the **pilot**.  
The AI Agent (**Jarvis**) is a **copilot** — assists in speed, structure, and consistency, but never replaces human judgment.

---

## 2. Workflow & Methodology

- **TDD:**  
  Always write failing tests → implement code → refactor. Maintain strong test coverage.
- **Branches:**  
  Each feature or ticket → one dedicated branch.
- **User Stories:**  
  “As a user, I want to [action] so that [benefit].”
- **Acceptance Criteria:**  
  Use **Gherkin** syntax (`Given / When / Then`).
- **Tickets:**  
  Include context, criteria, and technical notes.

---

## 3. Code Standards

- **Naming:**  
  `snake_case` for vars/functions, `PascalCase` for classes. Depending on the language, use `camelCase` for functions and variables.  
- **Docs:**  
  Each function/class must have a JSDoc (or equivalent) block.
- **Structure:**  
  Enforce modular architecture with clear separation of concerns (UI, logic, data).
- **Comments:**  
  Use comments to explain the purpose of the code.
- **Standards:**  
  Use language oficial standards and best practices, for example JS ES6+, python PEP 8, etc.

---

## 4. Design Principles

### 4.1 SOLID
1. **S** – Single Responsibility  
2. **O** – Open/Closed  
3. **L** – Liskov Substitution  
4. **I** – Interface Segregation  
5. **D** – Dependency Inversion  

### 4.2 Design Patterns
Use where appropriate: Factory, Singleton, Strategy, Observer, Decorator, etc.

### 4.3 Componentization
- Reuse logic and UI whenever possible.  
- Abstract common functionality into shared modules.  
- Apply **DRY** and **encapsulation** consistently.

---

## 5. Security Standards

- **Security by Design** and **by Default.**  
- No hardcoded or weak credentials.  
- Passwords must be **hashed + salted**.  
- Limit failed logins (brute-force protection).  
- Validate access on all protected routes.  
- Sanitize all external inputs.  
- Regularly audit dependencies (`npm audit`, `pip audit`).

---

## 6. Vue.js Architecture Standards

### 6.1 Component Structure
- **Views** should be < 300 lines (orchestration only)
- **Components** should be < 200 lines (single responsibility)
- **Composables** for business logic (reusable, testable)

### 6.2 Composables Pattern
Create composables for:
- **Data fetching & state** (`useUsers`, `useTables`)
- **Business logic** (`useSubscriptionUsage`)
- **Shared functionality** (permissions, validation)

**Example:**
```typescript
// composables/useUsers.ts
export function useUsers() {
  const users = ref([]);
  const loading = ref(false);
  const error = ref('');
  
  const loadUsers = async () => { /* ... */ };
  const createUser = async (data) => { /* ... */ };
  
  return { users, loading, error, loadUsers, createUser };
}
```

### 6.3 Component Breakdown
Extract UI into focused components:
- **Card components** for list items (`UserCard`, `TableCard`)
- **Table components** for desktop views (`UsersTable`)
- **Form components** for modals (`UserFormModal`, `TableFormModal`)
- **State components** for loading/error/empty (`TableStates`)

### 6.4 Modal Standards
All modals must:
- **Full screen on mobile** (`w-full h-full sm:max-w-lg`)
- **Responsive sizing** (smaller text/padding on mobile)
- **Dark mode support** (all elements)
- **Icons in inputs** for better UX
- **Visual feedback** (loading spinners, error states)
- **Proper z-index** (`z-[10001]` for modals, `z-[10000]` for dropdowns)

**Mobile optimization:**
```vue
<!-- Responsive padding -->
<div class="p-4 sm:p-8">
  <!-- Responsive text -->
  <label class="text-xs sm:text-sm">
  <!-- Responsive inputs -->
  <input class="py-2 sm:py-2.5 text-sm">
</div>
```

### 6.5 Refactoring Checklist
When refactoring large components:
- [ ] Extract business logic to composables
- [ ] Create reusable UI components
- [ ] Reduce main view to < 300 lines
- [ ] Add TypeScript types
- [ ] Maintain all existing functionality
- [ ] Test on mobile and desktop
- [ ] Verify dark mode

### 6.6 File Organization
```
frontend/src/
├── composables/
│   ├── useUsers.ts          # User business logic
│   ├── useTables.ts         # Table business logic
│   └── useSubscriptionUsage.ts
├── components/
│   ├── users/
│   │   ├── UserCard.vue     # Mobile card
│   │   ├── UsersTable.vue   # Desktop table
│   │   └── UserFormModal.vue
│   ├── tables/
│   │   ├── TableCard.vue
│   │   ├── TableStates.vue
│   │   └── TableFormModal.vue
│   └── ui/                  # Shared components
└── views/
    ├── UsersManagementView.vue  # Orchestration only
    └── TablesView.vue
```

### 6.7 UI/UX Standards
- **Icons in inputs** (UserIcon, EnvelopeIcon, LockClosedIcon)
- **Visual hierarchy** (headers with icons and descriptions)
- **Error feedback** (icons + colored backgrounds)
- **Loading states** (spinners with messages)
- **Consistent spacing** (Tailwind scale: 2, 3, 4, 6, 8)
- **Backdrop blur** for modals (`bg-black/60 backdrop-blur-sm`)

---

## 7. Context & References

- **Database schema:** `context/database.sql`  
- **Flows & diagrams:** `doc/*.md`  
- **Configuration:** `.env`, `config.yaml`, etc.  
- **Codebase:** Acts as the **single source of truth**.

---

## **8. Code Review Checklist**

```markdown
## 7. Code Review Checklist

### 7.1 Functionality
- [ ] Code works as intended
- [ ] Edge cases handled
- [ ] Error handling implemented
- [ ] No console errors or warnings

### 7.2 Code Quality
- [ ] Follows SOLID principles
- [ ] No code duplication (DRY)
- [ ] Functions are small and focused
- [ ] Naming is clear and consistent
- [ ] Comments explain "why", not "what"

### 7.3 Security
- [ ] No hardcoded credentials
- [ ] Input validation and sanitization
- [ ] Proper authentication/authorization
- [ ] No SQL injection vulnerabilities
- [ ] Dependencies are up to date

### 7.4 Performance
- [ ] No unnecessary re-renders
- [ ] Efficient database queries
- [ ] Images optimized
- [ ] No memory leaks

### 7.5 Testing
- [ ] Unit tests added/updated
- [ ] Tests pass locally
- [ ] Coverage meets minimum threshold
- [ ] Manual testing completed

### 7.6 Documentation
- [ ] JSDoc comments added
- [ ] README updated if needed
- [ ] API documentation updated
- [ ] Migration guide for breaking changes

## 9. Core Principle

> The developer defines the *why* — the agent optimizes the *how*.
