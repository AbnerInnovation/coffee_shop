/**
 * Unit tests for validators utility functions
 * Tests form validation logic
 */

import { describe, it, expect } from 'vitest'
import {
  validateEmail,
  validatePassword,
  validateRequired
} from '@/utils/validators'

describe('validators', () => {
  describe('validateEmail', () => {
    it('should return error for empty email', () => {
      const result = validateEmail('')
      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('El correo electrónico es obligatorio')
    })

    it('should return error for invalid email format', () => {
      const result = validateEmail('invalid-email')
      expect(result.isValid).toBe(false)
      expect(result.errors.length).toBeGreaterThan(0)
    })

    it('should return error for email without domain extension', () => {
      const result = validateEmail('user@domain')
      expect(result.isValid).toBe(false)
      expect(result.errors.length).toBeGreaterThan(0)
    })

    it('should validate correct email', () => {
      const result = validateEmail('user@example.com')
      expect(result.isValid).toBe(true)
      expect(result.errors).toEqual([])
    })

    it('should validate email with subdomain', () => {
      const result = validateEmail('user@mail.example.com')
      expect(result.isValid).toBe(true)
      expect(result.errors).toEqual([])
    })
  })

  describe('validatePassword', () => {
    it('should return error for empty required password', () => {
      const result = validatePassword('', true)
      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('La contraseña es obligatoria')
    })

    it('should pass for empty non-required password', () => {
      const result = validatePassword('', false)
      expect(result.isValid).toBe(true)
      expect(result.errors).toEqual([])
    })

    it('should return error for password too short', () => {
      const result = validatePassword('Short1!')
      expect(result.isValid).toBe(false)
      expect(result.errors.some(e => e.includes('8 caracteres'))).toBe(true)
    })

    it('should return error for password without uppercase', () => {
      const result = validatePassword('password123!')
      expect(result.isValid).toBe(false)
      expect(result.errors.some(e => e.includes('mayúscula'))).toBe(true)
    })

    it('should return error for password without lowercase', () => {
      const result = validatePassword('PASSWORD123!')
      expect(result.isValid).toBe(false)
      expect(result.errors.some(e => e.includes('minúscula'))).toBe(true)
    })

    it('should return error for password without number', () => {
      const result = validatePassword('Password!')
      expect(result.isValid).toBe(false)
      expect(result.errors.some(e => e.includes('número'))).toBe(true)
    })

    it('should return error for password without special character', () => {
      const result = validatePassword('Password123')
      expect(result.isValid).toBe(false)
      expect(result.errors.some(e => e.includes('especial'))).toBe(true)
    })

    it('should validate strong password', () => {
      const result = validatePassword('Password123!')
      expect(result.isValid).toBe(true)
      expect(result.errors).toEqual([])
    })

    it('should validate password with multiple special characters', () => {
      const result = validatePassword('P@ssw0rd!#$')
      expect(result.isValid).toBe(true)
      expect(result.errors).toEqual([])
    })
  })

  describe('validateRequired', () => {
    it('should return error for null value', () => {
      const result = validateRequired(null, 'Test field')
      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('Test field es obligatorio')
    })

    it('should return error for undefined value', () => {
      const result = validateRequired(undefined, 'Test field')
      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('Test field es obligatorio')
    })

    it('should return error for empty string', () => {
      const result = validateRequired('', 'Test field')
      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('Test field es obligatorio')
    })

    it('should validate non-empty string', () => {
      const result = validateRequired('value', 'Test field')
      expect(result.isValid).toBe(true)
      expect(result.errors).toEqual([])
    })

    it('should validate number zero', () => {
      const result = validateRequired(0, 'Test field')
      expect(result.isValid).toBe(true)
      expect(result.errors).toEqual([])
    })

    it('should validate positive number', () => {
      const result = validateRequired(123, 'Test field')
      expect(result.isValid).toBe(true)
      expect(result.errors).toEqual([])
    })

    it('should use default field name', () => {
      const result = validateRequired(null)
      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('Este campo es obligatorio')
    })
  })
})

// Import additional validators
import {
  validateMinLength,
  validateMaxLength,
  validateNumeric,
  validatePositive,
  validatePrice,
  validateUrl,
  validatePhone
} from '@/utils/validators'

describe('Additional validators', () => {
  describe('validateMinLength', () => {
    it('should return error when value is too short', () => {
      const result = validateMinLength('abc', 5, 'Name')
      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('Name debe tener al menos 5 caracteres')
    })

    it('should validate when value meets minimum length', () => {
      const result = validateMinLength('abcde', 5)
      expect(result.isValid).toBe(true)
      expect(result.errors).toEqual([])
    })

    it('should validate when value exceeds minimum length', () => {
      const result = validateMinLength('abcdefgh', 5)
      expect(result.isValid).toBe(true)
    })
  })

  describe('validateMaxLength', () => {
    it('should return error when value is too long', () => {
      const result = validateMaxLength('abcdefgh', 5, 'Name')
      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('Name no puede tener más de 5 caracteres')
    })

    it('should validate when value meets maximum length', () => {
      const result = validateMaxLength('abcde', 5)
      expect(result.isValid).toBe(true)
      expect(result.errors).toEqual([])
    })

    it('should validate when value is below maximum length', () => {
      const result = validateMaxLength('abc', 5)
      expect(result.isValid).toBe(true)
    })
  })

  describe('validateNumeric', () => {
    it('should validate numeric string', () => {
      const result = validateNumeric('123')
      expect(result.isValid).toBe(true)
      expect(result.errors).toEqual([])
    })

    it('should validate numeric value', () => {
      const result = validateNumeric(123)
      expect(result.isValid).toBe(true)
    })

    it('should return error for non-numeric string', () => {
      const result = validateNumeric('abc', 'Amount')
      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('Amount debe ser un número válido')
    })

    it('should validate decimal numbers', () => {
      const result = validateNumeric('123.45')
      expect(result.isValid).toBe(true)
    })

    it('should validate negative numbers', () => {
      const result = validateNumeric(-123)
      expect(result.isValid).toBe(true)
    })
  })

  describe('validatePositive', () => {
    it('should validate positive number', () => {
      const result = validatePositive(10)
      expect(result.isValid).toBe(true)
      expect(result.errors).toEqual([])
    })

    it('should return error for zero', () => {
      const result = validatePositive(0, 'Amount')
      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('Amount debe ser un número positivo')
    })

    it('should return error for negative number', () => {
      const result = validatePositive(-5, 'Amount')
      expect(result.isValid).toBe(false)
    })
  })

  describe('validatePrice', () => {
    it('should validate valid price', () => {
      const result = validatePrice(99.99)
      expect(result.isValid).toBe(true)
      expect(result.errors).toEqual([])
    })

    it('should validate price from string', () => {
      const result = validatePrice('49.50')
      expect(result.isValid).toBe(true)
    })

    it('should return error for non-numeric price', () => {
      const result = validatePrice('abc')
      expect(result.isValid).toBe(false)
      expect(result.errors.length).toBeGreaterThan(0)
    })

    it('should return error for zero or negative price', () => {
      const result = validatePrice(0)
      expect(result.isValid).toBe(false)
      expect(result.errors.some(e => e.includes('mayor a 0'))).toBe(true)
    })

    it('should return error for more than 2 decimals', () => {
      const result = validatePrice(99.999)
      expect(result.isValid).toBe(false)
      expect(result.errors.some(e => e.includes('2 decimales'))).toBe(true)
    })

    it('should validate price with 1 decimal', () => {
      const result = validatePrice(99.9)
      expect(result.isValid).toBe(true)
    })

    it('should validate integer price', () => {
      const result = validatePrice(100)
      expect(result.isValid).toBe(true)
    })
  })

  describe('validateUrl', () => {
    it('should validate valid URL', () => {
      const result = validateUrl('https://example.com')
      expect(result.isValid).toBe(true)
      expect(result.errors).toEqual([])
    })

    it('should validate URL with path', () => {
      const result = validateUrl('https://example.com/path/to/page')
      expect(result.isValid).toBe(true)
    })

    it('should validate URL with query params', () => {
      const result = validateUrl('https://example.com?param=value')
      expect(result.isValid).toBe(true)
    })

    it('should return error for invalid URL', () => {
      const result = validateUrl('not-a-url')
      expect(result.isValid).toBe(false)
      expect(result.errors.length).toBeGreaterThan(0)
    })

    it('should validate empty URL as optional', () => {
      const result = validateUrl('')
      expect(result.isValid).toBe(true)
    })

    it('should validate http URL', () => {
      const result = validateUrl('http://example.com')
      expect(result.isValid).toBe(true)
    })
  })

  describe('validatePhone', () => {
    it('should validate valid phone number', () => {
      const result = validatePhone('1234567890')
      expect(result.isValid).toBe(true)
      expect(result.errors).toEqual([])
    })

    it('should validate phone with country code', () => {
      const result = validatePhone('+521234567890')
      expect(result.isValid).toBe(true)
    })

    it('should validate phone with formatting', () => {
      const result = validatePhone('(123) 456-7890')
      expect(result.isValid).toBe(true)
    })

    it('should validate phone with spaces', () => {
      const result = validatePhone('123 456 7890')
      expect(result.isValid).toBe(true)
    })

    it('should return error for phone with letters', () => {
      const result = validatePhone('123abc7890')
      expect(result.isValid).toBe(false)
    })

    it('should return error for too short phone', () => {
      const result = validatePhone('12345')
      expect(result.isValid).toBe(false)
    })

    it('should return error for too long phone', () => {
      const result = validatePhone('12345678901234567890')
      expect(result.isValid).toBe(false)
    })

    it('should validate empty phone as optional', () => {
      const result = validatePhone('')
      expect(result.isValid).toBe(true)
    })
  })

  describe('validateName', () => {
    it('should validate valid name', () => {
      const result = validateName('John Doe')
      expect(result.isValid).toBe(true)
      expect(result.errors).toEqual([])
    })

    it('should validate name with Spanish characters', () => {
      const result = validateName('José María')
      expect(result.isValid).toBe(true)
    })

    it('should validate name with hyphens', () => {
      const result = validateName('Mary-Jane')
      expect(result.isValid).toBe(true)
    })

    it('should validate name with apostrophes', () => {
      const result = validateName("O'Brien")
      expect(result.isValid).toBe(true)
    })

    it('should return error for empty name', () => {
      const result = validateName('')
      expect(result.isValid).toBe(false)
      expect(result.errors.length).toBeGreaterThan(0)
    })

    it('should return error for name with numbers', () => {
      const result = validateName('John123')
      expect(result.isValid).toBe(false)
      expect(result.errors.some(e => e.includes('inválidos'))).toBe(true)
    })

    it('should return error for name with special characters', () => {
      const result = validateName('John@Doe')
      expect(result.isValid).toBe(false)
    })
  })

  describe('validateAlphanumeric', () => {
    it('should validate alphanumeric string', () => {
      const result = validateAlphanumeric('abc123')
      expect(result.isValid).toBe(true)
      expect(result.errors).toEqual([])
    })

    it('should validate only letters', () => {
      const result = validateAlphanumeric('abcdef')
      expect(result.isValid).toBe(true)
    })

    it('should validate only numbers', () => {
      const result = validateAlphanumeric('123456')
      expect(result.isValid).toBe(true)
    })

    it('should return error for spaces', () => {
      const result = validateAlphanumeric('abc 123')
      expect(result.isValid).toBe(false)
      expect(result.errors.some(e => e.includes('letras y números'))).toBe(true)
    })

    it('should return error for special characters', () => {
      const result = validateAlphanumeric('abc-123')
      expect(result.isValid).toBe(false)
    })
  })

  describe('validateRange', () => {
    it('should validate value within range', () => {
      const result = validateRange(50, 0, 100)
      expect(result.isValid).toBe(true)
      expect(result.errors).toEqual([])
    })

    it('should validate minimum value', () => {
      const result = validateRange(0, 0, 100)
      expect(result.isValid).toBe(true)
    })

    it('should validate maximum value', () => {
      const result = validateRange(100, 0, 100)
      expect(result.isValid).toBe(true)
    })

    it('should return error for value below minimum', () => {
      const result = validateRange(-1, 0, 100)
      expect(result.isValid).toBe(false)
      expect(result.errors.some(e => e.includes('entre 0 y 100'))).toBe(true)
    })

    it('should return error for value above maximum', () => {
      const result = validateRange(101, 0, 100)
      expect(result.isValid).toBe(false)
    })
  })

  describe('validateFutureDate', () => {
    it('should validate future date', () => {
      const futureDate = new Date()
      futureDate.setDate(futureDate.getDate() + 1)
      const result = validateFutureDate(futureDate)
      expect(result.isValid).toBe(true)
      expect(result.errors).toEqual([])
    })

    it('should validate future date from string', () => {
      const futureDate = new Date()
      futureDate.setDate(futureDate.getDate() + 7)
      const result = validateFutureDate(futureDate.toISOString())
      expect(result.isValid).toBe(true)
    })

    it('should return error for past date', () => {
      const pastDate = new Date()
      pastDate.setDate(pastDate.getDate() - 1)
      const result = validateFutureDate(pastDate)
      expect(result.isValid).toBe(false)
      expect(result.errors.some(e => e.includes('pasada'))).toBe(true)
    })
  })

  describe('combineValidations', () => {
    it('should combine multiple valid results', () => {
      const result1 = { isValid: true, errors: [] }
      const result2 = { isValid: true, errors: [] }
      const combined = combineValidations(result1, result2)
      expect(combined.isValid).toBe(true)
      expect(combined.errors).toEqual([])
    })

    it('should combine results with errors', () => {
      const result1 = { isValid: false, errors: ['Error 1'] }
      const result2 = { isValid: false, errors: ['Error 2'] }
      const combined = combineValidations(result1, result2)
      expect(combined.isValid).toBe(false)
      expect(combined.errors).toEqual(['Error 1', 'Error 2'])
    })

    it('should combine mixed results', () => {
      const result1 = { isValid: true, errors: [] }
      const result2 = { isValid: false, errors: ['Error'] }
      const combined = combineValidations(result1, result2)
      expect(combined.isValid).toBe(false)
      expect(combined.errors).toEqual(['Error'])
    })

    it('should handle empty array', () => {
      const combined = combineValidations()
      expect(combined.isValid).toBe(true)
      expect(combined.errors).toEqual([])
    })
  })

  describe('validateForm', () => {
    it('should validate entire form', () => {
      const formData = {
        name: 'John Doe',
        email: 'john@example.com',
        age: 25
      }

      const rules = {
        name: (value: string) => validateRequired(value, 'Name'),
        email: (value: string) => validateEmail(value),
        age: (value: number) => validatePositive(value, 'Age')
      }

      const results = validateForm(formData, rules)

      expect(results.name.isValid).toBe(true)
      expect(results.email.isValid).toBe(true)
      expect(results.age.isValid).toBe(true)
    })

    it('should return errors for invalid fields', () => {
      const formData = {
        name: '',
        email: 'invalid-email'
      }

      const rules = {
        name: (value: string) => validateRequired(value, 'Name'),
        email: (value: string) => validateEmail(value)
      }

      const results = validateForm(formData, rules)

      expect(results.name.isValid).toBe(false)
      expect(results.email.isValid).toBe(false)
    })
  })

  describe('hasFormErrors', () => {
    it('should return false when no errors', () => {
      const results = {
        field1: { isValid: true, errors: [] },
        field2: { isValid: true, errors: [] }
      }

      expect(hasFormErrors(results)).toBe(false)
    })

    it('should return true when has errors', () => {
      const results = {
        field1: { isValid: true, errors: [] },
        field2: { isValid: false, errors: ['Error'] }
      }

      expect(hasFormErrors(results)).toBe(true)
    })

    it('should return false for empty object', () => {
      const results = {}
      expect(hasFormErrors(results)).toBe(false)
    })
  })

  describe('getFormErrors', () => {
    it('should return empty array when no errors', () => {
      const results = {
        field1: { isValid: true, errors: [] },
        field2: { isValid: true, errors: [] }
      }

      const errors = getFormErrors(results)
      expect(errors).toEqual([])
    })

    it('should return all errors from all fields', () => {
      const results = {
        field1: { isValid: false, errors: ['Error 1', 'Error 2'] },
        field2: { isValid: false, errors: ['Error 3'] }
      }

      const errors = getFormErrors(results)
      expect(errors).toEqual(['Error 1', 'Error 2', 'Error 3'])
    })

    it('should return errors from mixed results', () => {
      const results = {
        field1: { isValid: true, errors: [] },
        field2: { isValid: false, errors: ['Error'] }
      }

      const errors = getFormErrors(results)
      expect(errors).toEqual(['Error'])
    })
  })
})

// Import additional validators for new tests
import {
  validateName,
  validateAlphanumeric,
  validateRange,
  validateFutureDate,
  combineValidations,
  validateForm,
  hasFormErrors,
  getFormErrors
} from '@/utils/validators'
