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

## 6. Context & References

- **Database schema:** `context/database.sql`  
- **Flows & diagrams:** `doc/*.md`  
- **Configuration:** `.env`, `config.yaml`, etc.  
- **Codebase:** Acts as the **single source of truth**.

---

## **7. Code Review Checklist**

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

## 8. Core Principle

> The developer defines the *why* — the agent optimizes the *how*.
