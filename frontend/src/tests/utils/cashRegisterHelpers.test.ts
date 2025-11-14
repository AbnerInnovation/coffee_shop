/**
 * Unit tests for cashRegisterHelpers utility functions
 * Tests pure functions for cash register calculations and formatting
 */

import { describe, it, expect } from 'vitest'
import {
  calculateSessionDuration,
  calculateSessionExpenses,
  calculateCurrentBalance,
  calculateCutReport,
  calculatePaymentBreakdown,
  getPaymentMethodBadgeClass,
  createEmptyDenominations,
  type Transaction
} from '@/utils/cashRegisterHelpers'

describe('cashRegisterHelpers', () => {
  describe('calculateSessionDuration', () => {
    it('should calculate duration correctly', () => {
      const openedAt = '2025-11-14T09:00:00'
      const currentTime = new Date('2025-11-14T11:35:00')
      const result = calculateSessionDuration(openedAt, currentTime)
      expect(result).toBe('2h 35m')
    })

    it('should return 0h 0m for empty openedAt', () => {
      const result = calculateSessionDuration('', new Date())
      expect(result).toBe('0h 0m')
    })

    it('should handle same time', () => {
      const time = '2025-11-14T09:00:00'
      const result = calculateSessionDuration(time, new Date(time))
      expect(result).toBe('0h 0m')
    })
  })

  describe('calculateSessionExpenses', () => {
    it('should calculate total expenses correctly', () => {
      const transactions: Transaction[] = [
        {
          id: 1,
          amount: -50,
          description: 'Expense 1',
          transaction_type: 'expense',
          created_at: '2025-11-14T09:00:00'
        },
        {
          id: 2,
          amount: -30,
          description: 'Expense 2',
          transaction_type: 'expense',
          created_at: '2025-11-14T10:00:00'
        },
        {
          id: 3,
          amount: 100,
          description: 'Sale',
          transaction_type: 'sale',
          created_at: '2025-11-14T11:00:00'
        }
      ]
      const result = calculateSessionExpenses(transactions)
      expect(result).toBe(80) // 50 + 30 (absolute values)
    })

    it('should return 0 for no expenses', () => {
      const transactions: Transaction[] = [
        {
          id: 1,
          amount: 100,
          description: 'Sale',
          transaction_type: 'sale',
          created_at: '2025-11-14T09:00:00'
        }
      ]
      const result = calculateSessionExpenses(transactions)
      expect(result).toBe(0)
    })

    it('should return 0 for empty array', () => {
      const result = calculateSessionExpenses([])
      expect(result).toBe(0)
    })
  })

  describe('calculateCurrentBalance', () => {
    it('should calculate balance with sales and expenses', () => {
      const initialBalance = 1000
      const transactions: Transaction[] = [
        {
          id: 1,
          amount: 500,
          description: 'Sale',
          transaction_type: 'sale',
          created_at: '2025-11-14T09:00:00'
        },
        {
          id: 2,
          amount: -100,
          description: 'Expense',
          transaction_type: 'expense',
          created_at: '2025-11-14T10:00:00'
        }
      ]
      const result = calculateCurrentBalance(initialBalance, transactions)
      expect(result).toBe(1400) // 1000 + 500 - 100
    })

    it('should return initial balance for no transactions', () => {
      const result = calculateCurrentBalance(1000, [])
      expect(result).toBe(1000)
    })

    it('should handle zero initial balance', () => {
      const transactions: Transaction[] = [
        {
          id: 1,
          amount: 100,
          description: 'Sale',
          transaction_type: 'sale',
          created_at: '2025-11-14T09:00:00'
        }
      ]
      const result = calculateCurrentBalance(0, transactions)
      expect(result).toBe(100)
    })
  })

  describe('calculateCutReport', () => {
    it('should calculate comprehensive cut report', () => {
      const transactions: Transaction[] = [
        {
          id: 1,
          amount: 500,
          description: 'Sale 1',
          transaction_type: 'sale',
          created_at: '2025-11-14T09:00:00'
        },
        {
          id: 2,
          amount: 300,
          description: 'Sale 2',
          transaction_type: 'sale',
          created_at: '2025-11-14T10:00:00'
        },
        {
          id: 3,
          amount: -50,
          description: 'Refund',
          transaction_type: 'refund',
          created_at: '2025-11-14T11:00:00'
        },
        {
          id: 4,
          amount: 25,
          description: 'Tip',
          transaction_type: 'tip',
          created_at: '2025-11-14T12:00:00'
        },
        {
          id: 5,
          amount: -100,
          description: 'Expense',
          transaction_type: 'expense',
          created_at: '2025-11-14T13:00:00'
        }
      ]

      const result = calculateCutReport(transactions)

      expect(result.total_sales).toBe(800) // 500 + 300
      expect(result.total_refunds).toBe(-50)
      expect(result.total_tips).toBe(25)
      expect(result.total_expenses).toBe(100) // absolute value
      expect(result.total_transactions).toBe(5)
      expect(result.net_cash_flow).toBe(775) // 800 - (-50) + 25 - 100 = 800 + 50 + 25 - 100
    })

    it('should handle empty transactions', () => {
      const result = calculateCutReport([])
      expect(result.total_sales).toBe(0)
      expect(result.total_refunds).toBe(0)
      expect(result.total_tips).toBe(0)
      expect(result.total_expenses).toBe(0)
      expect(result.total_transactions).toBe(0)
      expect(result.net_cash_flow).toBe(0)
    })
  })

  describe('calculatePaymentBreakdown', () => {
    it('should calculate breakdown by payment method', () => {
      const transactions: Transaction[] = [
        {
          id: 1,
          amount: 500,
          description: 'Sale',
          transaction_type: 'sale',
          payment_method: 'CASH',
          created_at: '2025-11-14T09:00:00'
        },
        {
          id: 2,
          amount: 300,
          description: 'Sale',
          transaction_type: 'sale',
          payment_method: 'CARD',
          created_at: '2025-11-14T10:00:00'
        },
        {
          id: 3,
          amount: 200,
          description: 'Sale',
          transaction_type: 'sale',
          payment_method: 'DIGITAL',
          created_at: '2025-11-14T11:00:00'
        },
        {
          id: 4,
          amount: -50,
          description: 'Refund',
          transaction_type: 'refund',
          payment_method: 'CASH',
          created_at: '2025-11-14T12:00:00'
        }
      ]

      const result = calculatePaymentBreakdown(transactions)

      expect(result.cash).toBe(500) // Only positive amounts
      expect(result.card).toBe(300)
      expect(result.digital).toBe(200)
      expect(result.other).toBe(0)
    })

    it('should handle case-insensitive payment methods', () => {
      const transactions: Transaction[] = [
        {
          id: 1,
          amount: 100,
          description: 'Sale',
          transaction_type: 'sale',
          payment_method: 'cash',
          created_at: '2025-11-14T09:00:00'
        },
        {
          id: 2,
          amount: 200,
          description: 'Sale',
          transaction_type: 'sale',
          payment_method: 'Cash',
          created_at: '2025-11-14T10:00:00'
        }
      ]

      const result = calculatePaymentBreakdown(transactions)
      expect(result.cash).toBe(300)
    })
  })

  describe('getPaymentMethodBadgeClass', () => {
    it('should return green classes for CASH', () => {
      const result = getPaymentMethodBadgeClass('CASH')
      expect(result).toContain('bg-green-100')
      expect(result).toContain('text-green-700')
    })

    it('should return blue classes for CARD', () => {
      const result = getPaymentMethodBadgeClass('CARD')
      expect(result).toContain('bg-blue-100')
      expect(result).toContain('text-blue-700')
    })

    it('should return purple classes for DIGITAL', () => {
      const result = getPaymentMethodBadgeClass('DIGITAL')
      expect(result).toContain('bg-purple-100')
      expect(result).toContain('text-purple-700')
    })

    it('should return gray classes for OTHER', () => {
      const result = getPaymentMethodBadgeClass('OTHER')
      expect(result).toContain('bg-gray-100')
      expect(result).toContain('text-gray-700')
    })

    it('should handle case-insensitive input', () => {
      const result = getPaymentMethodBadgeClass('cash')
      expect(result).toContain('bg-green-100')
    })

    it('should return default classes for unknown method', () => {
      const result = getPaymentMethodBadgeClass('UNKNOWN')
      expect(result).toContain('bg-gray-100')
    })
  })

  describe('createEmptyDenominations', () => {
    it('should create object with all denominations at 0', () => {
      const result = createEmptyDenominations()
      
      expect(result.bills_1000).toBe(0)
      expect(result.bills_500).toBe(0)
      expect(result.bills_200).toBe(0)
      expect(result.bills_100).toBe(0)
      expect(result.bills_50).toBe(0)
      expect(result.bills_20).toBe(0)
      expect(result.coins_20).toBe(0)
      expect(result.coins_10).toBe(0)
      expect(result.coins_5).toBe(0)
      expect(result.coins_2).toBe(0)
      expect(result.coins_1).toBe(0)
      expect(result.coins_50_cent).toBe(0)
    })

    it('should create new object each time', () => {
      const result1 = createEmptyDenominations()
      const result2 = createEmptyDenominations()
      
      expect(result1).not.toBe(result2)
      expect(result1).toEqual(result2)
    })
  })

  describe('formatTransactionDate', () => {
    it('should format valid date string', () => {
      const result = formatTransactionDate('2025-11-14T10:30:00')
      expect(result).toBeTruthy()
      expect(result).not.toBe('No date')
      expect(result).not.toBe('Invalid date')
    })

    it('should return "No date" for empty string', () => {
      const result = formatTransactionDate('')
      expect(result).toBe('No date')
    })

    it('should return "Invalid date" for invalid date string', () => {
      const result = formatTransactionDate('invalid-date-string')
      expect(result).toBe('Invalid Date')
    })

    it('should handle null as empty string', () => {
      const result = formatTransactionDate(null as any)
      expect(result).toBe('No date')
    })
  })

  describe('translateDescription', () => {
    const mockT = (key: string, params?: any) => {
      if (key === 'app.views.cashRegister.paymentForOrder') {
        return `Pago de orden #${params.orderNumber}`
      }
      return key
    }

    it('should translate payment for order pattern', () => {
      const result = translateDescription('Payment for order #123', mockT)
      expect(result).toBe('Pago de orden #123')
    })

    it('should handle case insensitive matching', () => {
      const result = translateDescription('PAYMENT FOR ORDER #456', mockT)
      expect(result).toBe('Pago de orden #456')
    })

    it('should return original description if no pattern matches', () => {
      const result = translateDescription('Regular transaction', mockT)
      expect(result).toBe('Regular transaction')
    })

    it('should handle empty description', () => {
      const result = translateDescription('', mockT)
      expect(result).toBe('')
    })
  })

  describe('translateTransactionType', () => {
    const mockT = (key: string) => {
      const translations: Record<string, string> = {
        'app.views.cashRegister.typeSale': 'Venta',
        'app.views.cashRegister.typeRefund': 'Reembolso',
        'app.views.cashRegister.typeCancellation': 'Cancelación',
        'app.views.cashRegister.typeTip': 'Propina',
        'app.views.cashRegister.typeManualAdd': 'Añadir manual',
        'app.views.cashRegister.typeManualWithdraw': 'Retiro manual',
        'app.views.cashRegister.typeExpense': 'Gasto'
      }
      return translations[key] || key
    }

    it('should translate sale type', () => {
      const result = translateTransactionType('sale', mockT)
      expect(result).toBe('Venta')
    })

    it('should translate refund type', () => {
      const result = translateTransactionType('refund', mockT)
      expect(result).toBe('Reembolso')
    })

    it('should translate cancellation type', () => {
      const result = translateTransactionType('cancellation', mockT)
      expect(result).toBe('Cancelación')
    })

    it('should translate tip type', () => {
      const result = translateTransactionType('tip', mockT)
      expect(result).toBe('Propina')
    })

    it('should translate expense type', () => {
      const result = translateTransactionType('expense', mockT)
      expect(result).toBe('Gasto')
    })

    it('should return original type for unknown types', () => {
      const result = translateTransactionType('unknown_type', mockT)
      expect(result).toBe('unknown_type')
    })
  })

  describe('translatePaymentMethod', () => {
    const mockT = (key: string) => {
      const translations: Record<string, string> = {
        'app.views.cashRegister.cash': 'Efectivo',
        'app.views.cashRegister.card': 'Tarjeta',
        'app.views.cashRegister.digital': 'Digital',
        'app.views.cashRegister.other': 'Otro'
      }
      return translations[key] || key
    }

    it('should translate cash method', () => {
      const result = translatePaymentMethod('cash', mockT)
      expect(result).toBe('Efectivo')
    })

    it('should translate card method', () => {
      const result = translatePaymentMethod('card', mockT)
      expect(result).toBe('Tarjeta')
    })

    it('should translate digital method', () => {
      const result = translatePaymentMethod('digital', mockT)
      expect(result).toBe('Digital')
    })

    it('should translate other method', () => {
      const result = translatePaymentMethod('other', mockT)
      expect(result).toBe('Otro')
    })

    it('should handle uppercase method names', () => {
      const result = translatePaymentMethod('CASH', mockT)
      expect(result).toBe('Efectivo')
    })

    it('should handle null method', () => {
      const result = translatePaymentMethod(null as any, mockT)
      expect(result).toBeNull()
    })

    it('should return original method for unknown methods', () => {
      const result = translatePaymentMethod('crypto', mockT)
      expect(result).toBe('crypto')
    })
  })
})

// Import additional functions for new tests
import {
  formatTransactionDate,
  translateDescription,
  translateTransactionType,
  translatePaymentMethod
} from '@/utils/cashRegisterHelpers'
