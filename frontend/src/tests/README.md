# Testing Guide

## Overview

This project uses **Vitest** as the testing framework for unit and integration tests. Vitest is a fast, modern testing framework built on top of Vite.

## Setup

### Install Dependencies

```bash
npm install
```

This will install all testing dependencies including:
- `vitest` - Testing framework
- `@vue/test-utils` - Vue component testing utilities
- `@vitest/ui` - UI for running tests
- `@vitest/coverage-v8` - Code coverage reporting
- `jsdom` - DOM environment for tests

## Running Tests

### Watch Mode (Development)
Runs tests in watch mode, re-running on file changes:
```bash
npm run test
```

### Single Run
Runs all tests once and exits:
```bash
npm run test:run
```

### UI Mode
Opens an interactive UI for running and debugging tests:
```bash
npm run test:ui
```

### Coverage Report
Generates a code coverage report:
```bash
npm run test:coverage
```

Coverage reports are generated in the `coverage/` directory and can be viewed in your browser.

## Test Structure

### Directory Organization

```
src/
├── tests/
│   ├── setup.ts                    # Global test setup
│   ├── utils/                      # Tests for utility functions
│   │   ├── orderHelpers.test.ts
│   │   └── cashRegisterHelpers.test.ts
│   ├── composables/                # Tests for composables
│   │   ├── useOrdersView.test.ts
│   │   └── useCashRegisterHandlers.test.ts
│   └── components/                 # Tests for Vue components
│       ├── StatCard.test.ts
│       └── ChartCard.test.ts
└── README.md                       # This file
```

## Writing Tests

### Basic Test Structure

```typescript
import { describe, it, expect } from 'vitest'

describe('MyFunction', () => {
  it('should do something', () => {
    const result = myFunction()
    expect(result).toBe(expectedValue)
  })
})
```

### Testing Utility Functions

```typescript
import { describe, it, expect } from 'vitest'
import { myUtilFunction } from '@/utils/myUtils'

describe('myUtilFunction', () => {
  it('should return correct value', () => {
    const result = myUtilFunction('input')
    expect(result).toBe('expected output')
  })

  it('should handle edge cases', () => {
    expect(myUtilFunction('')).toBe('')
    expect(myUtilFunction(null)).toBe(null)
  })
})
```

### Testing Vue Components

```typescript
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import MyComponent from '@/components/MyComponent.vue'

describe('MyComponent', () => {
  it('should render correctly', () => {
    const wrapper = mount(MyComponent, {
      props: {
        title: 'Test Title'
      }
    })
    
    expect(wrapper.text()).toContain('Test Title')
  })

  it('should emit event on click', async () => {
    const wrapper = mount(MyComponent)
    await wrapper.find('button').trigger('click')
    
    expect(wrapper.emitted('click')).toBeTruthy()
  })
})
```

### Testing Composables

```typescript
import { describe, it, expect } from 'vitest'
import { useMyComposable } from '@/composables/useMyComposable'

describe('useMyComposable', () => {
  it('should initialize with correct values', () => {
    const { value, loading } = useMyComposable()
    
    expect(value.value).toBe(null)
    expect(loading.value).toBe(false)
  })

  it('should update value correctly', async () => {
    const { value, updateValue } = useMyComposable()
    
    await updateValue('new value')
    
    expect(value.value).toBe('new value')
  })
})
```

## Mocking

### Mocking Functions

```typescript
import { vi } from 'vitest'

const mockFunction = vi.fn()
mockFunction.mockReturnValue('mocked value')
```

### Mocking Modules

```typescript
import { vi } from 'vitest'

vi.mock('@/services/myService', () => ({
  myService: {
    getData: vi.fn().mockResolvedValue({ data: 'mocked' })
  }
}))
```

### Mocking Vue Router

```typescript
import { vi } from 'vitest'

const mockRouter = {
  push: vi.fn(),
  replace: vi.fn()
}

const wrapper = mount(MyComponent, {
  global: {
    mocks: {
      $router: mockRouter
    }
  }
})
```

## Best Practices

### 1. Follow TDD (Test-Driven Development)
- Write failing tests first
- Implement code to make tests pass
- Refactor while keeping tests green

### 2. Test Naming Convention
- Use descriptive test names: `should [expected behavior] when [condition]`
- Group related tests with `describe` blocks

### 3. Test Coverage Goals
- Aim for **70%+ coverage** on:
  - Lines
  - Functions
  - Branches
  - Statements

### 4. What to Test
✅ **DO Test:**
- Pure functions (utils, helpers)
- Business logic (composables)
- Component behavior and interactions
- Edge cases and error handling

❌ **DON'T Test:**
- Third-party libraries
- Simple getters/setters
- Implementation details

### 5. Keep Tests Fast
- Mock external dependencies (API calls, localStorage)
- Avoid testing implementation details
- Use `vi.mock()` for heavy imports

### 6. Test Isolation
- Each test should be independent
- Use `beforeEach` to reset state
- Don't rely on test execution order

## Coverage Thresholds

Current minimum coverage requirements (configured in `vitest.config.ts`):

- **Lines:** 70%
- **Functions:** 70%
- **Branches:** 70%
- **Statements:** 70%

## Debugging Tests

### VS Code Debugging
1. Set breakpoints in your test file
2. Run "Debug: JavaScript Debug Terminal"
3. Run `npm run test` in the debug terminal

### Console Logging
```typescript
it('should debug', () => {
  const result = myFunction()
  console.log('Result:', result)
  expect(result).toBe(expected)
})
```

### Vitest UI
The UI mode provides an interactive way to debug tests:
```bash
npm run test:ui
```

## Continuous Integration

Tests should run automatically on:
- Pre-commit (using git hooks)
- Pull requests
- Before deployment

Example CI configuration:
```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
      - run: npm ci
      - run: npm run test:run
      - run: npm run test:coverage
```

## Resources

- [Vitest Documentation](https://vitest.dev/)
- [Vue Test Utils](https://test-utils.vuejs.org/)
- [Testing Library](https://testing-library.com/)
- [Jest Matchers](https://jestjs.io/docs/expect) (Compatible with Vitest)

## Examples

See the following test files for examples:
- `src/tests/utils/orderHelpers.test.ts` - Testing utility functions
- `src/tests/utils/cashRegisterHelpers.test.ts` - Testing calculations

## Troubleshooting

### Tests not running
- Ensure all dependencies are installed: `npm install`
- Check for syntax errors in test files
- Verify `vitest.config.ts` is properly configured

### Coverage not generating
- Run `npm run test:coverage`
- Check that files are not in the exclude list
- Ensure tests are actually running

### Mocks not working
- Verify mock is defined before import
- Use `vi.mock()` at the top of the file
- Check mock implementation matches actual API

## Next Steps

1. ✅ Install dependencies: `npm install`
2. ✅ Run tests: `npm run test`
3. 📝 Write tests for new features
4. 📊 Check coverage: `npm run test:coverage`
5. 🎯 Maintain 70%+ coverage
