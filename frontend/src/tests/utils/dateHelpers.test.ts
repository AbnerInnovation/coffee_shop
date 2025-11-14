/**
 * Unit tests for dateHelpers utility functions
 * Tests date formatting and manipulation
 */

import { describe, it, expect } from 'vitest'
import {
  formatDate,
  formatDateWithOptions,
  formatDateTime,
  formatTime,
  formatTimeAgo,
  formatDateTimeShort
} from '@/utils/dateHelpers'

describe('dateHelpers', () => {
  describe('formatDate', () => {
    it('should format valid date string', () => {
      const result = formatDate('2025-11-14')
      expect(result).toMatch(/\d{1,2}\/\d{1,2}\/\d{4}/)
    })

    it('should format Date object', () => {
      const date = new Date('2025-11-14')
      const result = formatDate(date)
      expect(result).toMatch(/\d{1,2}\/\d{1,2}\/\d{4}/)
    })

    it('should return N/A for null', () => {
      const result = formatDate(null)
      expect(result).toBe('N/A')
    })

    it('should return N/A for undefined', () => {
      const result = formatDate(undefined)
      expect(result).toBe('N/A')
    })

    it('should return Invalid Date for invalid date string', () => {
      const result = formatDate('invalid-date')
      // JavaScript's Date constructor returns 'Invalid Date' for invalid strings
      expect(result).toContain('Invalid Date')
    })

    it('should handle ISO date format', () => {
      const result = formatDate('2025-11-14T10:30:00Z')
      expect(result).toMatch(/\d{1,2}\/\d{1,2}\/\d{4}/)
    })
  })

  describe('formatDateWithOptions', () => {
    it('should format date with default options', () => {
      const result = formatDateWithOptions('2025-11-14')
      expect(result).toBeTruthy()
      expect(result).not.toBe('N/A')
    })

    it('should format date with custom options', () => {
      const options: Intl.DateTimeFormatOptions = {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      }
      const result = formatDateWithOptions('2025-11-14', options)
      expect(result).toBeTruthy()
      expect(result).not.toBe('N/A')
    })

    it('should return N/A for null', () => {
      const result = formatDateWithOptions(null)
      expect(result).toBe('N/A')
    })

    it('should return N/A for undefined', () => {
      const result = formatDateWithOptions(undefined)
      expect(result).toBe('N/A')
    })

    it('should return Invalid Date for invalid date string', () => {
      const result = formatDateWithOptions('invalid')
      // JavaScript's Date constructor returns 'Invalid Date' for invalid strings
      expect(result).toContain('Invalid Date')
    })

    it('should handle Date object', () => {
      const date = new Date('2025-11-14')
      const result = formatDateWithOptions(date)
      expect(result).toBeTruthy()
      expect(result).not.toBe('N/A')
    })
  })

  describe('formatDateTime', () => {
    it('should format date and time', () => {
      const result = formatDateTime('2025-11-14T10:30:00')
      expect(result).toMatch(/\d{1,2}\/\d{1,2}\/\d{4}/)
      expect(result).toMatch(/\d{1,2}:\d{2}/)
    })

    it('should format Date object', () => {
      const date = new Date('2025-11-14T10:30:00')
      const result = formatDateTime(date)
      expect(result).toMatch(/\d{1,2}\/\d{1,2}\/\d{4}/)
    })

    it('should return N/A for null', () => {
      const result = formatDateTime(null)
      expect(result).toBe('N/A')
    })

    it('should return N/A for undefined', () => {
      const result = formatDateTime(undefined)
      expect(result).toBe('N/A')
    })

    it('should return Invalid Date for invalid date string', () => {
      const result = formatDateTime('invalid')
      // JavaScript's Date constructor returns 'Invalid Date' for invalid strings
      expect(result).toContain('Invalid Date')
    })
  })

  describe('formatTime', () => {
    it('should format time from date string', () => {
      const result = formatTime('2025-11-14T10:30:00')
      expect(result).toMatch(/\d{1,2}:\d{2}/)
    })

    it('should format time from Date object', () => {
      const date = new Date('2025-11-14T10:30:00')
      const result = formatTime(date)
      expect(result).toMatch(/\d{1,2}:\d{2}/)
    })

    it('should format midnight correctly', () => {
      const result = formatTime('2025-11-14T00:00:00')
      expect(result).toMatch(/\d{1,2}:\d{2}/)
    })

    it('should format noon correctly', () => {
      const result = formatTime('2025-11-14T12:00:00')
      expect(result).toMatch(/\d{1,2}:\d{2}/)
    })
  })

  describe('formatTimeAgo', () => {
    it('should format recent date', () => {
      const now = new Date()
      const result = formatTimeAgo(now)
      expect(result).toBeTruthy()
      expect(result).not.toBe('')
    })

    it('should return empty string for null', () => {
      const result = formatTimeAgo(null)
      expect(result).toBe('')
    })

    it('should return empty string for undefined', () => {
      const result = formatTimeAgo(undefined)
      expect(result).toBe('')
    })

    it('should return empty string for invalid date', () => {
      const result = formatTimeAgo('invalid')
      expect(result).toBe('')
    })

    it('should format past date', () => {
      const pastDate = new Date('2025-11-13T10:00:00')
      const result = formatTimeAgo(pastDate)
      expect(result).toBeTruthy()
    })

    it('should handle Date object', () => {
      const date = new Date()
      const result = formatTimeAgo(date)
      expect(result).toBeTruthy()
      expect(result).not.toBe('')
    })
  })

  describe('formatDateTimeShort', () => {
    it('should format date and time in short format', () => {
      const result = formatDateTimeShort('2025-11-14T10:30:00')
      expect(result).toMatch(/\d{1,2}\/\d{1,2}\/\d{4}/)
      expect(result).toMatch(/\d{1,2}:\d{2}/)
    })

    it('should return N/A for null', () => {
      const result = formatDateTimeShort(null)
      expect(result).toBe('N/A')
    })

    it('should return N/A for undefined', () => {
      const result = formatDateTimeShort(undefined)
      expect(result).toBe('N/A')
    })

    it('should return Invalid Date for invalid date string', () => {
      const result = formatDateTimeShort('invalid')
      // JavaScript's Date constructor returns 'Invalid Date' for invalid strings
      expect(result).toContain('Invalid Date')
    })

    it('should include both date and time', () => {
      const result = formatDateTimeShort('2025-11-14T15:45:00')
      expect(result).toContain('/')
      expect(result).toContain(':')
    })

    it('should handle midnight', () => {
      const result = formatDateTimeShort('2025-11-14T00:00:00')
      expect(result).toMatch(/\d{1,2}\/\d{1,2}\/\d{4}/)
      expect(result).toMatch(/\d{1,2}:\d{2}/)
    })
  })
})
