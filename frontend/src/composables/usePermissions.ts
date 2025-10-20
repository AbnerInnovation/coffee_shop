/**
 * Composable for permission checks
 * 
 * Provides reactive permission checks based on current user
 */

import { computed } from 'vue';
import { useAuthStore } from '@/stores/auth';
import * as permissions from '@/utils/permissions';

export function usePermissions() {
  const authStore = useAuthStore();
  
  // Reactive user
  const currentUser = computed(() => authStore.user);
  
  // Role checks
  const isSysAdmin = computed(() => permissions.isSysAdmin(currentUser.value));
  const isAdmin = computed(() => permissions.isAdmin(currentUser.value));
  const isStaff = computed(() => permissions.isStaff(currentUser.value));
  const isCustomer = computed(() => permissions.isCustomer(currentUser.value));
  const isAdminOrSysAdmin = computed(() => permissions.isAdminOrSysAdmin(currentUser.value));
  
  // Feature permissions
  const canEditMenu = computed(() => permissions.canEditMenu(currentUser.value));
  const canEditCategories = computed(() => permissions.canEditCategories(currentUser.value));
  const canManageTables = computed(() => permissions.canManageTables(currentUser.value));
  const canManageUsers = computed(() => permissions.canManageUsers(currentUser.value));
  const canViewSubscription = computed(() => permissions.canViewSubscription(currentUser.value));
  const canCreateOrders = computed(() => permissions.canCreateOrders(currentUser.value));
  const canAccessCashRegister = computed(() => permissions.canAccessCashRegister(currentUser.value));
  const canAccessKitchen = computed(() => permissions.canAccessKitchen(currentUser.value));
  const canViewReports = computed(() => permissions.canViewReports(currentUser.value));
  const canEditOrders = computed(() => permissions.canEditOrders(currentUser.value));
  const canDeleteOrders = computed(() => permissions.canDeleteOrders(currentUser.value));
  const canProcessPayments = computed(() => permissions.canProcessPayments(currentUser.value));
  
  return {
    // User
    currentUser,
    
    // Role checks
    isSysAdmin,
    isAdmin,
    isStaff,
    isCustomer,
    isAdminOrSysAdmin,
    
    // Feature permissions
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
    canProcessPayments,
    
    // Utility functions (non-reactive)
    getRoleDisplayName: permissions.getRoleDisplayName,
    getStaffTypeDisplayName: permissions.getStaffTypeDisplayName
  };
}
