/**
 * Unit tests for permissions utility functions
 * Tests role-based access control logic
 */

import { describe, it, expect } from 'vitest'
import {
  isSysAdmin,
  isAdmin,
  isStaff,
  isCustomer,
  isAdminOrSysAdmin,
  canEditMenu,
  canEditCategories,
  canManageTables,
  canManageUsers,
  canViewSubscription,
  canCreateOrders,
  canAccessCashRegister,
  canAccessKitchen,
  canViewReports,
  canEditOrders,
  canDeleteOrders,
  canCancelOrders,
  canProcessPayments,
  getRoleDisplayName,
  getStaffTypeDisplayName,
  UserRole,
  StaffType
} from '@/utils/permissions'
import type { User } from '@/stores/auth'

describe('permissions', () => {
  describe('Role checks', () => {
    it('should identify sysadmin', () => {
      const user: User = { id: 1, email: 'admin@test.com', role: UserRole.SYSADMIN } as User
      expect(isSysAdmin(user)).toBe(true)
      expect(isAdmin(user)).toBe(false)
      expect(isStaff(user)).toBe(false)
      expect(isCustomer(user)).toBe(false)
    })

    it('should identify admin', () => {
      const user: User = { id: 1, email: 'admin@test.com', role: UserRole.ADMIN } as User
      expect(isSysAdmin(user)).toBe(false)
      expect(isAdmin(user)).toBe(true)
      expect(isStaff(user)).toBe(false)
      expect(isCustomer(user)).toBe(false)
    })

    it('should identify staff', () => {
      const user: User = { id: 1, email: 'staff@test.com', role: UserRole.STAFF } as User
      expect(isSysAdmin(user)).toBe(false)
      expect(isAdmin(user)).toBe(false)
      expect(isStaff(user)).toBe(true)
      expect(isCustomer(user)).toBe(false)
    })

    it('should identify customer', () => {
      const user: User = { id: 1, email: 'customer@test.com', role: UserRole.CUSTOMER } as User
      expect(isSysAdmin(user)).toBe(false)
      expect(isAdmin(user)).toBe(false)
      expect(isStaff(user)).toBe(false)
      expect(isCustomer(user)).toBe(true)
    })

    it('should handle null user', () => {
      expect(isSysAdmin(null)).toBe(false)
      expect(isAdmin(null)).toBe(false)
      expect(isStaff(null)).toBe(false)
      expect(isCustomer(null)).toBe(false)
    })

    it('should handle undefined user', () => {
      expect(isSysAdmin(undefined)).toBe(false)
      expect(isAdmin(undefined)).toBe(false)
      expect(isStaff(undefined)).toBe(false)
      expect(isCustomer(undefined)).toBe(false)
    })
  })

  describe('isAdminOrSysAdmin', () => {
    it('should return true for sysadmin', () => {
      const user: User = { id: 1, email: 'admin@test.com', role: UserRole.SYSADMIN } as User
      expect(isAdminOrSysAdmin(user)).toBe(true)
    })

    it('should return true for admin', () => {
      const user: User = { id: 1, email: 'admin@test.com', role: UserRole.ADMIN } as User
      expect(isAdminOrSysAdmin(user)).toBe(true)
    })

    it('should return false for staff', () => {
      const user: User = { id: 1, email: 'staff@test.com', role: UserRole.STAFF } as User
      expect(isAdminOrSysAdmin(user)).toBe(false)
    })

    it('should return false for customer', () => {
      const user: User = { id: 1, email: 'customer@test.com', role: UserRole.CUSTOMER } as User
      expect(isAdminOrSysAdmin(user)).toBe(false)
    })
  })

  describe('Menu and Categories permissions', () => {
    it('should allow admin to edit menu', () => {
      const user: User = { id: 1, email: 'admin@test.com', role: UserRole.ADMIN } as User
      expect(canEditMenu(user)).toBe(true)
      expect(canEditCategories(user)).toBe(true)
    })

    it('should allow sysadmin to edit menu', () => {
      const user: User = { id: 1, email: 'admin@test.com', role: UserRole.SYSADMIN } as User
      expect(canEditMenu(user)).toBe(true)
      expect(canEditCategories(user)).toBe(true)
    })

    it('should not allow staff to edit menu', () => {
      const user: User = { id: 1, email: 'staff@test.com', role: UserRole.STAFF } as User
      expect(canEditMenu(user)).toBe(false)
      expect(canEditCategories(user)).toBe(false)
    })
  })

  describe('Management permissions', () => {
    it('should allow admin to manage tables and users', () => {
      const user: User = { id: 1, email: 'admin@test.com', role: UserRole.ADMIN } as User
      expect(canManageTables(user)).toBe(true)
      expect(canManageUsers(user)).toBe(true)
      expect(canViewSubscription(user)).toBe(true)
    })

    it('should not allow staff to manage tables and users', () => {
      const user: User = { id: 1, email: 'staff@test.com', role: UserRole.STAFF } as User
      expect(canManageTables(user)).toBe(false)
      expect(canManageUsers(user)).toBe(false)
      expect(canViewSubscription(user)).toBe(false)
    })
  })

  describe('Order permissions', () => {
    it('should allow waiter to create and edit orders', () => {
      const user: User = { 
        id: 1, 
        email: 'waiter@test.com', 
        role: UserRole.STAFF,
        staff_type: StaffType.WAITER
      } as User
      expect(canCreateOrders(user)).toBe(true)
      expect(canEditOrders(user)).toBe(true)
    })

    it('should not allow cashier to create orders', () => {
      const user: User = { 
        id: 1, 
        email: 'cashier@test.com', 
        role: UserRole.STAFF,
        staff_type: StaffType.CASHIER
      } as User
      expect(canCreateOrders(user)).toBe(false)
      expect(canEditOrders(user)).toBe(false)
    })

    it('should allow admin to delete and cancel orders', () => {
      const user: User = { id: 1, email: 'admin@test.com', role: UserRole.ADMIN } as User
      expect(canDeleteOrders(user)).toBe(true)
      expect(canCancelOrders(user)).toBe(true)
    })

    it('should not allow staff to delete orders', () => {
      const user: User = { id: 1, email: 'staff@test.com', role: UserRole.STAFF } as User
      expect(canDeleteOrders(user)).toBe(false)
      expect(canCancelOrders(user)).toBe(false)
    })
  })

  describe('Cash register permissions', () => {
    it('should allow cashier to access cash register', () => {
      const user: User = { 
        id: 1, 
        email: 'cashier@test.com', 
        role: UserRole.STAFF,
        staff_type: StaffType.CASHIER
      } as User
      expect(canAccessCashRegister(user)).toBe(true)
      expect(canProcessPayments(user)).toBe(true)
    })

    it('should not allow waiter to access cash register', () => {
      const user: User = { 
        id: 1, 
        email: 'waiter@test.com', 
        role: UserRole.STAFF,
        staff_type: StaffType.WAITER
      } as User
      expect(canAccessCashRegister(user)).toBe(false)
      expect(canProcessPayments(user)).toBe(false)
    })

    it('should allow admin to access cash register', () => {
      const user: User = { id: 1, email: 'admin@test.com', role: UserRole.ADMIN } as User
      expect(canAccessCashRegister(user)).toBe(true)
      expect(canProcessPayments(user)).toBe(true)
    })
  })

  describe('Kitchen permissions', () => {
    it('should allow kitchen staff to access kitchen', () => {
      const user: User = { 
        id: 1, 
        email: 'kitchen@test.com', 
        role: UserRole.STAFF,
        staff_type: StaffType.KITCHEN
      } as User
      expect(canAccessKitchen(user)).toBe(true)
    })

    it('should not allow waiter to access kitchen', () => {
      const user: User = { 
        id: 1, 
        email: 'waiter@test.com', 
        role: UserRole.STAFF,
        staff_type: StaffType.WAITER
      } as User
      expect(canAccessKitchen(user)).toBe(false)
    })

    it('should allow admin to access kitchen', () => {
      const user: User = { id: 1, email: 'admin@test.com', role: UserRole.ADMIN } as User
      expect(canAccessKitchen(user)).toBe(true)
    })
  })

  describe('Reports permissions', () => {
    it('should allow admin to view reports', () => {
      const user: User = { id: 1, email: 'admin@test.com', role: UserRole.ADMIN } as User
      expect(canViewReports(user)).toBe(true)
    })

    it('should not allow staff to view reports', () => {
      const user: User = { id: 1, email: 'staff@test.com', role: UserRole.STAFF } as User
      expect(canViewReports(user)).toBe(false)
    })
  })

  describe('Display names', () => {
    it('should return correct role display names', () => {
      expect(getRoleDisplayName(UserRole.SYSADMIN)).toBe('Super Admin')
      expect(getRoleDisplayName(UserRole.ADMIN)).toBe('Administrador')
      expect(getRoleDisplayName(UserRole.STAFF)).toBe('Personal')
      expect(getRoleDisplayName(UserRole.CUSTOMER)).toBe('Cliente')
    })

    it('should return role itself for unknown role', () => {
      expect(getRoleDisplayName('unknown')).toBe('unknown')
    })

    it('should return correct staff type display names', () => {
      expect(getStaffTypeDisplayName(StaffType.GENERAL)).toBe('General')
      expect(getStaffTypeDisplayName(StaffType.WAITER)).toBe('Mesero')
      expect(getStaffTypeDisplayName(StaffType.CASHIER)).toBe('Cajero')
      expect(getStaffTypeDisplayName(StaffType.KITCHEN)).toBe('Cocina')
    })

    it('should return staff type itself for unknown type', () => {
      expect(getStaffTypeDisplayName('unknown')).toBe('unknown')
    })
  })
})
