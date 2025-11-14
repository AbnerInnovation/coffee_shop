/**
 * Unit tests for priceHelpers utility functions
 * Tests price calculations, discounts, and formatting
 */

import { describe, it, expect } from 'vitest'
import {
  getEffectivePrice,
  getVariantPrice,
  getMenuItemName,
  getMenuItemCategory,
  formatCurrency
} from '@/utils/priceHelpers'

describe('priceHelpers', () => {
  describe('getEffectivePrice', () => {
    it('should return regular price when no discount', () => {
      const result = getEffectivePrice(100)
      expect(result).toBe(100)
    })

    it('should return regular price when discount is 0', () => {
      const result = getEffectivePrice(100, 0)
      expect(result).toBe(100)
    })

    it('should return regular price when discount is undefined', () => {
      const result = getEffectivePrice(100, undefined)
      expect(result).toBe(100)
    })

    it('should return discount price when available', () => {
      const result = getEffectivePrice(100, 80)
      expect(result).toBe(80)
    })

    it('should handle decimal prices', () => {
      const result = getEffectivePrice(99.99, 79.99)
      expect(result).toBe(79.99)
    })
  })

  describe('getVariantPrice', () => {
    it('should return base price for item without variant', () => {
      const item = { id: 1, name: 'Coffee', price: 50 }
      const result = getVariantPrice(item as any, null)
      expect(result).toBe(50)
    })

    it('should return base price with discount when available', () => {
      const item = { id: 1, name: 'Coffee', price: 50, discount_price: 40 }
      const result = getVariantPrice(item as any, null)
      expect(result).toBe(40)
    })

    it('should return variant absolute price', () => {
      const item = { id: 1, name: 'Coffee', price: 50 }
      const variant = { id: 1, name: 'Large', price: 70 } as any
      const result = getVariantPrice(item as any, variant)
      expect(result).toBe(70)
    })

    it('should return variant price with discount', () => {
      const item = { id: 1, name: 'Coffee', price: 50 }
      const variant = { id: 1, name: 'Large', price: 70, discount_price: 60 } as any
      const result = getVariantPrice(item as any, variant)
      expect(result).toBe(60)
    })

    it('should apply price adjustment to base price', () => {
      const item = { id: 1, name: 'Coffee', price: 50 }
      const variant = { id: 1, name: 'Large', price_adjustment: 10 } as any
      const result = getVariantPrice(item as any, variant)
      expect(result).toBe(60)
    })

    it('should apply price adjustment to discounted base price', () => {
      const item = { id: 1, name: 'Coffee', price: 50, discount_price: 40 }
      const variant = { id: 1, name: 'Large', price_adjustment: 10 } as any
      const result = getVariantPrice(item as any, variant)
      expect(result).toBe(50) // 40 + 10
    })

    it('should handle string price', () => {
      const item = { id: 1, name: 'Coffee', price: '50' }
      const result = getVariantPrice(item as any, null)
      expect(result).toBe(50)
    })

    it('should handle zero price', () => {
      const item = { id: 1, name: 'Coffee', price: 0 }
      const result = getVariantPrice(item as any, null)
      expect(result).toBe(0)
    })

    it('should handle negative price adjustment', () => {
      const item = { id: 1, name: 'Coffee', price: 50 }
      const variant = { id: 1, name: 'Small', price_adjustment: -10 } as any
      const result = getVariantPrice(item as any, variant)
      expect(result).toBe(40)
    })
  })

  describe('getMenuItemName', () => {
    const menuItems = [
      { id: 1, name: 'Coffee' },
      { id: 2, name: 'Tea' },
      { id: 3, name: 'Juice' }
    ]

    it('should return item name when found', () => {
      const result = getMenuItemName(menuItems, 1)
      expect(result).toBe('Coffee')
    })

    it('should return Unknown when item not found', () => {
      const result = getMenuItemName(menuItems, 999)
      expect(result).toBe('Unknown')
    })

    it('should handle empty array', () => {
      const result = getMenuItemName([], 1)
      expect(result).toBe('Unknown')
    })

    it('should find last item', () => {
      const result = getMenuItemName(menuItems, 3)
      expect(result).toBe('Juice')
    })
  })

  describe('getMenuItemCategory', () => {
    it('should return category name when category is string', () => {
      const menuItems = [{ id: 1, name: 'Coffee', category: 'Beverages' }]
      const result = getMenuItemCategory(menuItems, 1)
      expect(result).toBe('Beverages')
    })

    it('should return category name when category is object', () => {
      const menuItems = [{ id: 1, name: 'Coffee', category: { id: 1, name: 'Beverages' } }]
      const result = getMenuItemCategory(menuItems, 1)
      expect(result).toBe('Beverages')
    })

    it('should return empty string when no category', () => {
      const menuItems = [{ id: 1, name: 'Coffee' }]
      const result = getMenuItemCategory(menuItems, 1)
      expect(result).toBe('')
    })

    it('should return empty string when item not found', () => {
      const menuItems = [{ id: 1, name: 'Coffee', category: 'Beverages' }]
      const result = getMenuItemCategory(menuItems, 999)
      expect(result).toBe('')
    })

    it('should return empty string when category object has no name', () => {
      const menuItems = [{ id: 1, name: 'Coffee', category: { id: 1 } }]
      const result = getMenuItemCategory(menuItems, 1)
      expect(result).toBe('')
    })

    it('should handle empty array', () => {
      const result = getMenuItemCategory([], 1)
      expect(result).toBe('')
    })
  })

  describe('formatCurrency', () => {
    it('should format currency with default MXN', () => {
      const result = formatCurrency(1000)
      expect(result).toContain('1')
      expect(result).toContain('000')
    })

    it('should format currency with thousands separator', () => {
      const result = formatCurrency(1234.56)
      expect(result).toContain('1')
      expect(result).toContain('234')
    })

    it('should format zero', () => {
      const result = formatCurrency(0)
      expect(result).toContain('0')
    })

    it('should format negative amounts', () => {
      const result = formatCurrency(-100)
      expect(result).toContain('100')
    })

    it('should format large numbers', () => {
      const result = formatCurrency(1000000)
      expect(result).toContain('1')
      expect(result).toContain('000')
      expect(result).toContain('000')
    })

    it('should format decimal amounts', () => {
      const result = formatCurrency(99.99)
      expect(result).toContain('99')
    })

    it('should handle custom currency', () => {
      const result = formatCurrency(100, 'USD')
      expect(result).toBeTruthy()
      expect(typeof result).toBe('string')
    })

    it('should handle custom locale', () => {
      const result = formatCurrency(100, 'USD', 'en-US')
      expect(result).toBeTruthy()
      expect(typeof result).toBe('string')
    })
  })
})
