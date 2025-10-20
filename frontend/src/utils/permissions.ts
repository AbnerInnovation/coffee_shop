/**
 * Permission utilities for role-based access control
 * 
 * This module provides reusable functions to check user permissions
 * based on their role and staff type.
 */

import type { User } from '@/stores/auth';

/**
 * User roles in the system
 */
export enum UserRole {
  SYSADMIN = 'sysadmin',
  ADMIN = 'admin',
  STAFF = 'staff',
  CUSTOMER = 'customer'
}

/**
 * Staff sub-types (for future implementation)
 */
export enum StaffType {
  GENERAL = 'general',
  WAITER = 'waiter',
  CASHIER = 'cashier',
  KITCHEN = 'kitchen'
}

/**
 * Check if user is a system administrator
 */
export function isSysAdmin(user: User | null | undefined): boolean {
  return user?.role === UserRole.SYSADMIN;
}

/**
 * Check if user is an admin (restaurant administrator)
 */
export function isAdmin(user: User | null | undefined): boolean {
  return user?.role === UserRole.ADMIN;
}

/**
 * Check if user is staff
 */
export function isStaff(user: User | null | undefined): boolean {
  return user?.role === UserRole.STAFF;
}

/**
 * Check if user is a customer
 */
export function isCustomer(user: User | null | undefined): boolean {
  return user?.role === UserRole.CUSTOMER;
}

/**
 * Check if user is admin or sysadmin
 * Most common permission check for administrative actions
 */
export function isAdminOrSysAdmin(user: User | null | undefined): boolean {
  return isAdmin(user) || isSysAdmin(user);
}

/**
 * Check if user can edit menu items
 * Only admin and sysadmin can modify menu
 */
export function canEditMenu(user: User | null | undefined): boolean {
  return isAdminOrSysAdmin(user);
}

/**
 * Check if user can edit categories
 * Only admin and sysadmin can modify categories
 */
export function canEditCategories(user: User | null | undefined): boolean {
  return isAdminOrSysAdmin(user);
}

/**
 * Check if user can manage tables
 * Only admin and sysadmin can create/edit/delete tables
 */
export function canManageTables(user: User | null | undefined): boolean {
  return isAdminOrSysAdmin(user);
}

/**
 * Check if user can manage users
 * Only admin and sysadmin can manage users
 */
export function canManageUsers(user: User | null | undefined): boolean {
  return isAdminOrSysAdmin(user);
}

/**
 * Check if user can view subscription
 * Only admin and sysadmin can view subscription details
 */
export function canViewSubscription(user: User | null | undefined): boolean {
  return isAdminOrSysAdmin(user);
}

/**
 * Check if user can create orders
 * Admin, sysadmin, and staff (waiter) can create orders
 */
export function canCreateOrders(user: User | null | undefined): boolean {
  if (isAdminOrSysAdmin(user)) return true;
  if (isStaff(user)) {
    // Waiters can create orders
    return user?.staff_type === StaffType.WAITER;
  }
  return false;
}

/**
 * Check if user can access cash register
 * Admin, sysadmin, and staff (cashier) can access cash register
 */
export function canAccessCashRegister(user: User | null | undefined): boolean {
  if (isAdminOrSysAdmin(user)) return true;
  if (isStaff(user)) {
    // Only cashiers can access cash register
    return user?.staff_type === StaffType.CASHIER;
  }
  return false;
}

/**
 * Check if user can access kitchen module
 * Admin, sysadmin, and staff (kitchen) can access kitchen
 */
export function canAccessKitchen(user: User | null | undefined): boolean {
  if (isAdminOrSysAdmin(user)) return true;
  if (isStaff(user)) {
    // Only kitchen staff can access kitchen module
    return user?.staff_type === StaffType.KITCHEN;
  }
  return false;
}

/**
 * Check if user can view reports
 * Only admin and sysadmin can view reports
 */
export function canViewReports(user: User | null | undefined): boolean {
  return isAdminOrSysAdmin(user);
}

/**
 * Check if user can edit orders
 * Admin, sysadmin, and staff (waiter) can edit orders
 */
export function canEditOrders(user: User | null | undefined): boolean {
  if (isAdminOrSysAdmin(user)) return true;
  if (isStaff(user)) {
    // Only waiters can edit orders
    return user?.staff_type === StaffType.WAITER;
  }
  return false;
}

/**
 * Check if user can delete orders
 * Only admin and sysadmin can delete orders
 */
export function canDeleteOrders(user: User | null | undefined): boolean {
  return isAdminOrSysAdmin(user);
}

/**
 * Check if user can process payments
 * Admin, sysadmin, and staff (cashier) can process payments
 */
export function canProcessPayments(user: User | null | undefined): boolean {
  if (isAdminOrSysAdmin(user)) return true;
  if (isStaff(user)) {
    // Only cashiers can process payments
    return user?.staff_type === StaffType.CASHIER;
  }
  return false;
}

/**
 * Get user role display name (for UI)
 */
export function getRoleDisplayName(role: string): string {
  const roleMap: Record<string, string> = {
    [UserRole.SYSADMIN]: 'Super Admin',
    [UserRole.ADMIN]: 'Administrador',
    [UserRole.STAFF]: 'Personal',
    [UserRole.CUSTOMER]: 'Cliente'
  };
  return roleMap[role] || role;
}

/**
 * Get staff type display name (for UI)
 */
export function getStaffTypeDisplayName(staffType: string): string {
  const staffTypeMap: Record<string, string> = {
    [StaffType.GENERAL]: 'General',
    [StaffType.WAITER]: 'Mesero',
    [StaffType.CASHIER]: 'Cajero',
    [StaffType.KITCHEN]: 'Cocina'
  };
  return staffTypeMap[staffType] || staffType;
}
