import { fileURLToPath } from 'node:url'
import { defineConfig, configDefaults } from 'vitest/config'
import vue from '@vitejs/plugin-vue'

/**
 * Vitest configuration
 * Standalone configuration for testing (does not merge with vite.config)
 * 
 * @see https://vitest.dev/config/
 */
export default defineConfig({
  plugins: [vue()],
  
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  
  test: {
    // Test environment
    environment: 'jsdom',
    
    // Exclude patterns
    exclude: [...configDefaults.exclude, 'e2e/**'],
    
    // Root directory for tests
    root: fileURLToPath(new URL('./', import.meta.url)),
    
    // Global test setup
    globals: true,
    
    // Coverage configuration
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/main.ts',
        '**/*.d.ts',
        '**/*.config.*',
        '**/mockData',
        'dist/',
        '.nuxt/',
        'coverage/',
      ],
      // Minimum coverage thresholds
      // Adjusted based on current project complexity and test coverage
      thresholds: {
        lines: 60,        // Complex helpers with edge cases
        functions: 45,    // Some validators have many optional functions
        branches: 40,     // Conditional logic in business rules
        statements: 60    // Matches lines threshold
      }
    },
    
    // Setup files to run before tests
    setupFiles: ['./src/tests/setup.ts'],
    
    // Test timeout
    testTimeout: 10000,
    
    // Hook timeout
    hookTimeout: 10000,
  },
})
