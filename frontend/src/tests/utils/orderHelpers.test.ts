/**
 * Unit tests for orderHelpers utility functions
 * Tests pure functions for order management and transformations
 */

import { describe, it, expect } from 'vitest'
import {
  getStatusBadgeClass,
  formatTime,
  getOrderItemsSummary,
  getOrderCount,
  canCancelOrder,
  type OrderWithLocalFields,
  type OrderItemLocal,
  type BackendOrderStatus
} from '@/utils/orderHelpers'

describe('orderHelpers', () => {
  describe('getStatusBadgeClass', () => {
    it('should return yellow classes for pending status', () => {
      const result = getStatusBadgeClass('pending')
      expect(result).toContain('bg-yellow-100')
      expect(result).toContain('text-yellow-800')
    })

    it('should return blue classes for preparing status', () => {
      const result = getStatusBadgeClass('preparing')
      expect(result).toContain('bg-blue-100')
      expect(result).toContain('text-blue-800')
    })

    it('should return green classes for ready status', () => {
      const result = getStatusBadgeClass('ready')
      expect(result).toContain('bg-green-100')
      expect(result).toContain('text-green-800')
    })

    it('should return gray classes for completed status', () => {
      const result = getStatusBadgeClass('completed')
      expect(result).toContain('bg-gray-100')
      expect(result).toContain('text-gray-800')
    })

    it('should return red classes for cancelled status', () => {
      const result = getStatusBadgeClass('cancelled')
      expect(result).toContain('bg-red-100')
      expect(result).toContain('text-red-800')
    })
  })

  describe('formatTime', () => {
    it('should format date string to time', () => {
      const date = '2025-11-14T09:30:00'
      const result = formatTime(date)
      expect(result).toMatch(/\d{1,2}:\d{2}/)
    })

    it('should format Date object to time', () => {
      const date = new Date('2025-11-14T09:30:00')
      const result = formatTime(date)
      expect(result).toMatch(/\d{1,2}:\d{2}/)
    })
  })

  describe('getOrderItemsSummary', () => {
    it('should return empty string for empty array', () => {
      const result = getOrderItemsSummary([])
      expect(result).toBe('')
    })

    it('should return empty string for null/undefined', () => {
      const result = getOrderItemsSummary(null as any)
      expect(result).toBe('')
    })

    it('should format single item without variant', () => {
      const items: OrderItemLocal[] = [
        {
          id: 1,
          menu_item_id: 1,
          name: 'Café',
          quantity: 2,
          unit_price: 30,
          total_price: 60
        }
      ]
      const result = getOrderItemsSummary(items)
      expect(result).toBe('2x Café')
    })

    it('should format item with variant', () => {
      const items: OrderItemLocal[] = [
        {
          id: 1,
          menu_item_id: 1,
          name: 'Café',
          variant_name: 'Grande',
          quantity: 1,
          unit_price: 35,
          total_price: 35
        }
      ]
      const result = getOrderItemsSummary(items)
      expect(result).toBe('1x Café - Grande')
    })

    it('should format item with extras', () => {
      const items: OrderItemLocal[] = [
        {
          id: 1,
          menu_item_id: 1,
          name: 'Café',
          quantity: 1,
          unit_price: 30,
          total_price: 35,
          extras: [
            { id: 1, name: 'Leche', price: 5, quantity: 1 }
          ]
        }
      ]
      const result = getOrderItemsSummary(items)
      expect(result).toBe('1x Café con Leche')
    })

    it('should format item with variant and multiple extras', () => {
      const items: OrderItemLocal[] = [
        {
          id: 1,
          menu_item_id: 1,
          name: 'Café',
          variant_name: 'Grande',
          quantity: 2,
          unit_price: 35,
          total_price: 80,
          extras: [
            { id: 1, name: 'Leche', price: 5, quantity: 1 },
            { id: 2, name: 'Azúcar', price: 0, quantity: 1 }
          ]
        }
      ]
      const result = getOrderItemsSummary(items)
      expect(result).toBe('2x Café - Grande con Leche, Azúcar')
    })

    it('should format multiple items', () => {
      const items: OrderItemLocal[] = [
        {
          id: 1,
          menu_item_id: 1,
          name: 'Café',
          quantity: 2,
          unit_price: 30,
          total_price: 60
        },
        {
          id: 2,
          menu_item_id: 2,
          name: 'Croissant',
          quantity: 1,
          unit_price: 25,
          total_price: 25
        }
      ]
      const result = getOrderItemsSummary(items)
      expect(result).toBe('2x Café, 1x Croissant')
    })
  })

  describe('getOrderCount', () => {
    const mockOrders: OrderWithLocalFields[] = [
      {
        id: 1,
        status: 'pending',
        customerName: 'John',
        table: 'Mesa 1',
        total: 100,
        createdAt: new Date(),
        updated_at: '2025-11-14T09:00:00',
        items: []
      },
      {
        id: 2,
        status: 'pending',
        customerName: 'Jane',
        table: 'Mesa 2',
        total: 150,
        createdAt: new Date(),
        updated_at: '2025-11-14T09:10:00',
        items: []
      },
      {
        id: 3,
        status: 'preparing',
        customerName: 'Bob',
        table: 'Mesa 3',
        total: 200,
        createdAt: new Date(),
        updated_at: '2025-11-14T09:20:00',
        items: []
      }
    ]

    it('should count orders with specific status', () => {
      const count = getOrderCount(mockOrders, 'pending')
      expect(count).toBe(2)
    })

    it('should return 0 for status with no orders', () => {
      const count = getOrderCount(mockOrders, 'completed')
      expect(count).toBe(0)
    })

    it('should return 0 for empty array', () => {
      const count = getOrderCount([], 'pending')
      expect(count).toBe(0)
    })

    it('should return 0 for null/undefined', () => {
      const count = getOrderCount(null as any, 'pending')
      expect(count).toBe(0)
    })
  })

  describe('canCancelOrder', () => {
    it('should allow cancelling pending unpaid order', () => {
      const order = {
        id: 1,
        status: 'pending',
        is_paid: false,
        items: [{ status: 'pending' }]
      } as OrderWithLocalFields

      expect(canCancelOrder(order)).toBe(true)
    })

    it('should not allow cancelling paid order', () => {
      const order = {
        id: 1,
        status: 'pending',
        is_paid: true,
        items: []
      } as OrderWithLocalFields

      expect(canCancelOrder(order)).toBe(false)
    })

    it('should not allow cancelling non-pending order', () => {
      const order = {
        id: 1,
        status: 'completed',
        is_paid: false,
        items: []
      } as OrderWithLocalFields

      expect(canCancelOrder(order)).toBe(false)
    })

    it('should allow cancelling order with no items', () => {
      const order = {
        id: 1,
        status: 'pending',
        is_paid: false,
        items: []
      } as OrderWithLocalFields

      expect(canCancelOrder(order)).toBe(true)
    })

    it('should not allow cancelling if any item is not pending', () => {
      const order: OrderWithLocalFields = {
        id: 1,
        status: 'pending',
        is_paid: false,
        customerName: 'John',
        table: 'Mesa 1',
        total: 100,
        createdAt: new Date(),
        updated_at: '2025-11-14T09:00:00',
        items: [
          {
            id: 1,
            menu_item_id: 1,
            name: 'Café',
            quantity: 1,
            unit_price: 30,
            total_price: 30,
            status: 'pending'
          },
          {
            id: 2,
            menu_item_id: 2,
            name: 'Croissant',
            quantity: 1,
            unit_price: 25,
            total_price: 25,
            status: 'preparing'
          }
        ]
      }
      expect(canCancelOrder(order)).toBe(false)
    })

    it('should allow cancelling if all items are pending', () => {
      const order = {
        id: 1,
        status: 'pending',
        is_paid: false,
        items: [
          { status: 'pending' },
          { status: 'pending' }
        ]
      } as OrderWithLocalFields

      expect(canCancelOrder(order)).toBe(true)
    })

    it('should allow cancelling if items have undefined status', () => {
      const order = {
        id: 1,
        status: 'pending',
        is_paid: false,
        items: [
          { status: undefined },
          { status: 'pending' }
        ]
      } as OrderWithLocalFields

      expect(canCancelOrder(order)).toBe(true)
    })
  })

  describe('transformOrderToLocal', () => {
    const mockT = (key: string, params?: any) => {
      if (key === 'app.views.cashRegister.table_number') {
        return `Mesa ${params.number}`
      }
      if (key === 'app.views.cashRegister.takeaway') {
        return 'Para llevar'
      }
      return key
    }

    it('should return null for null order', () => {
      const result = transformOrderToLocal(null, mockT)
      expect(result).toBeNull()
    })

    it('should return null for undefined order', () => {
      const result = transformOrderToLocal(undefined, mockT)
      expect(result).toBeNull()
    })

    it('should transform basic order with table number', () => {
      const apiOrder = {
        id: 1,
        customer_name: 'John Doe',
        table_number: 5,
        total_amount: 100,
        created_at: '2025-11-14T10:00:00',
        status: 'pending',
        items: []
      }

      const result = transformOrderToLocal(apiOrder, mockT)
      
      expect(result).not.toBeNull()
      expect(result?.customerName).toBe('John Doe')
      expect(result?.table).toBe('Mesa 5')
      expect(result?.total).toBe(100)
      expect(result?.items).toEqual([])
    })

    it('should use Walk-in for missing customer name', () => {
      const apiOrder = {
        id: 1,
        table_number: 3,
        total_amount: 50,
        created_at: '2025-11-14T10:00:00',
        status: 'pending',
        items: []
      }

      const result = transformOrderToLocal(apiOrder, mockT)
      expect(result?.customerName).toBe('Walk-in')
    })

    it('should use takeaway label for no table number', () => {
      const apiOrder = {
        id: 1,
        customer_name: 'Jane Doe',
        total_amount: 75,
        created_at: '2025-11-14T10:00:00',
        status: 'pending',
        items: []
      }

      const result = transformOrderToLocal(apiOrder, mockT)
      expect(result?.table).toBe('Para llevar')
    })

    it('should transform order items with variants', () => {
      const apiOrder = {
        id: 1,
        total_amount: 150,
        created_at: '2025-11-14T10:00:00',
        status: 'pending',
        items: [{
          id: 1,
          menu_item_id: 10,
          menu_item: { id: 10, name: 'Café', price: 50 },
          variant_id: 2,
          variant: { id: 2, name: 'Grande' },
          quantity: 2,
          unit_price: 60,
          status: 'pending',
          extras: []
        }]
      }

      const result = transformOrderToLocal(apiOrder, mockT)
      
      expect(result?.items).toHaveLength(1)
      expect(result?.items[0].name).toBe('Café')
      expect(result?.items[0].variant_name).toBe('Grande')
      expect(result?.items[0].quantity).toBe(2)
      expect(result?.items[0].unit_price).toBe(60)
      expect(result?.items[0].total_price).toBe(120)
    })

    it('should calculate total with extras', () => {
      const apiOrder = {
        id: 1,
        total_amount: 200,
        created_at: '2025-11-14T10:00:00',
        status: 'pending',
        items: [{
          id: 1,
          menu_item_id: 10,
          menu_item: { id: 10, name: 'Café' },
          quantity: 1,
          unit_price: 50,
          extras: [
            { id: 1, name: 'Leche', price: 10, quantity: 1 },
            { id: 2, name: 'Azúcar', price: 5, quantity: 2 }
          ]
        }]
      }

      const result = transformOrderToLocal(apiOrder, mockT)
      
      expect(result?.items[0].total_price).toBe(70) // 50 + 10 + (5*2)
      expect(result?.items[0].extras).toHaveLength(2)
    })

    it('should handle items without menu_item', () => {
      const apiOrder = {
        id: 1,
        total_amount: 100,
        created_at: '2025-11-14T10:00:00',
        status: 'pending',
        items: [{
          id: 1,
          menu_item_id: 10,
          quantity: 1,
          unit_price: 100
        }]
      }

      const result = transformOrderToLocal(apiOrder, mockT)
      
      expect(result?.items[0].name).toBe('Unknown Item')
      expect(result?.items[0].menu_item).toBeUndefined()
    })

    it('should handle items without variant', () => {
      const apiOrder = {
        id: 1,
        total_amount: 50,
        created_at: '2025-11-14T10:00:00',
        status: 'pending',
        items: [{
          id: 1,
          menu_item_id: 10,
          menu_item: { id: 10, name: 'Croissant' },
          quantity: 1,
          unit_price: 50
        }]
      }

      const result = transformOrderToLocal(apiOrder, mockT)
      
      expect(result?.items[0].variant_name).toBeUndefined()
      expect(result?.items[0].variant).toBeNull()
    })

    it('should handle empty extras array', () => {
      const apiOrder = {
        id: 1,
        total_amount: 50,
        created_at: '2025-11-14T10:00:00',
        status: 'pending',
        items: [{
          id: 1,
          menu_item_id: 10,
          menu_item: { id: 10, name: 'Café' },
          quantity: 1,
          unit_price: 50,
          extras: []
        }]
      }

      const result = transformOrderToLocal(apiOrder, mockT)
      expect(result?.items[0].extras).toEqual([])
    })

    it('should handle missing extras', () => {
      const apiOrder = {
        id: 1,
        total_amount: 50,
        created_at: '2025-11-14T10:00:00',
        status: 'pending',
        items: [{
          id: 1,
          menu_item_id: 10,
          menu_item: { id: 10, name: 'Café' },
          quantity: 1,
          unit_price: 50
        }]
      }

      const result = transformOrderToLocal(apiOrder, mockT)
      expect(result?.items[0].extras).toEqual([])
    })

    it('should handle special instructions', () => {
      const apiOrder = {
        id: 1,
        total_amount: 50,
        created_at: '2025-11-14T10:00:00',
        status: 'pending',
        items: [{
          id: 1,
          menu_item_id: 10,
          menu_item: { id: 10, name: 'Café' },
          quantity: 1,
          unit_price: 50,
          special_instructions: 'Sin azúcar'
        }]
      }

      const result = transformOrderToLocal(apiOrder, mockT)
      expect(result?.items[0].notes).toBe('Sin azúcar')
    })

    it('should handle missing unit_price and quantity', () => {
      const apiOrder = {
        id: 1,
        total_amount: 0,
        created_at: '2025-11-14T10:00:00',
        status: 'pending',
        items: [{
          id: 1,
          menu_item_id: 10,
          menu_item: { id: 10, name: 'Café' }
        }]
      }

      const result = transformOrderToLocal(apiOrder, mockT)
      expect(result?.items[0].unit_price).toBe(0)
      expect(result?.items[0].quantity).toBe(0)
      expect(result?.items[0].total_price).toBe(0)
    })

    it('should handle non-array items', () => {
      const apiOrder = {
        id: 1,
        total_amount: 100,
        created_at: '2025-11-14T10:00:00',
        status: 'pending',
        items: null
      }

      const result = transformOrderToLocal(apiOrder, mockT)
      expect(result?.items).toEqual([])
    })
  })
})

// Import additional functions
import { transformOrderToLocal } from '@/utils/orderHelpers'
