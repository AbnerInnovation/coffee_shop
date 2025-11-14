/**
 * Vitest global setup file
 * Runs before all tests to configure the testing environment
 */

import { vi } from 'vitest'
import { config } from '@vue/test-utils'

/**
 * Mock window.matchMedia for components that use responsive design
 */
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

/**
 * Mock IntersectionObserver for components that use lazy loading
 */
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  takeRecords() {
    return []
  }
  unobserve() {}
} as any

/**
 * Configure Vue Test Utils global properties
 */
config.global.mocks = {
  $t: (key: string) => key, // Mock i18n translation
  $route: {
    params: {},
    query: {},
  },
  $router: {
    push: vi.fn(),
    replace: vi.fn(),
    go: vi.fn(),
    back: vi.fn(),
  },
}

/**
 * Suppress console warnings in tests
 * Uncomment if needed for cleaner test output
 */
// global.console = {
//   ...console,
//   warn: vi.fn(),
//   error: vi.fn(),
// }
