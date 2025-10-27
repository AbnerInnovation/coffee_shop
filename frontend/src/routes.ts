import type { RouteRecordRaw } from 'vue-router';
import type { User } from '@/stores/auth';

// Permission check function type
export type PermissionCheck = (user: User | null) => boolean;

export const routes: RouteRecordRaw[] = [
  // Protected routes
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('./views/DashboardView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/tables',
    name: 'Tables',
    component: () => import('./views/TablesView.vue'),
    meta: { 
      requiresAuth: true,
      permissionCheck: 'canManageTables' // Admin only for management
    }
  },
  {
    path: '/menu',
    name: 'Menu',
    component: () => import('./views/MenuView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/categories',
    name: 'Categories',
    component: () => import('./views/CategoriesView.vue'),
    meta: { 
      requiresAuth: true,
      permissionCheck: 'canEditCategories' // Admin only
    }
  },
  {
    path: '/cash-register',
    name: 'CashRegister',
    component: () => import('./views/CashRegisterView.vue'),
    meta: { 
      requiresAuth: true,
      permissionCheck: 'canAccessCashRegister' // Admin + Cashier
    }
  },
  {
    path: '/orders',
    name: 'Orders',
    component: () => import('./views/OrdersView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/kitchen',
    name: 'Kitchen',
    component: () => import('./views/KitchenView.vue'),
    meta: { 
      requiresAuth: true,
      requiresKitchenModule: true,
      permissionCheck: 'canAccessKitchen' // Admin + Kitchen staff
    }
  },
  {
    path: '/sysadmin',
    name: 'SysAdmin',
    component: () => import('./views/SysAdminView.vue'),
    meta: { 
      requiresAuth: true,
      permissionCheck: 'isSysAdmin' // SysAdmin only
    }
  },
  {
    path: '/subscription',
    name: 'Subscription',
    component: () => import('./views/SubscriptionView.vue'),
    meta: { 
      requiresAuth: true,
      permissionCheck: 'canViewSubscription' // Admin + SysAdmin
    }
  },
  {
    path: '/users',
    name: 'Users',
    component: () => import('./views/UsersManagementView.vue'),
    meta: { 
      requiresAuth: true,
      permissionCheck: 'canManageUsers' // Admin + SysAdmin
    }
  },
  {
    path: '/reports',
    name: 'Reports',
    component: () => import('./views/ReportsView.vue'),
    meta: { 
      requiresAuth: true,
      permissionCheck: 'canViewSubscription' // Admin + SysAdmin (same as subscription)
    }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('./views/ProfileView.vue'),
    meta: { 
      requiresAuth: true // All authenticated users can view their profile
    }
  },

  // Public routes
  {
    path: '/login',
    name: 'Login',
    component: () => import('./views/LoginView.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('./views/RegisterView.vue'),
    meta: { requiresAuth: false }
  },

  // Marketing landing
  {
    path: '/plans',
    name: 'Plans',
    component: () => import('./views/LandingView.vue'),
    meta: { requiresAuth: false, hideNavbar: true }
  },

  // Catch-all
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('./views/NotFoundView.vue')
  }
];
