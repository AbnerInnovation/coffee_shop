import type { RouteRecordRaw } from 'vue-router';
import type { User } from '@/stores/auth';

// Static imports for all views
import DashboardView from './views/DashboardView.vue';
import TablesView from './views/TablesView.vue';
import MenuView from './views/MenuView.vue';
import CategoriesView from './views/CategoriesView.vue';
import CashRegisterView from './views/CashRegisterView.vue';
import OrdersView from './views/OrdersView.vue';
import POSView from './views/POSView.vue';
import KitchenView from './views/KitchenView.vue';
import SysAdminView from './views/SysAdminView.vue';
import PendingPaymentsView from './views/PendingPaymentsView.vue';
import SubscriptionView from './views/SubscriptionView.vue';
import UsersManagementView from './views/UsersManagementView.vue';
import ReportsView from './views/ReportsView.vue';
import ProfileView from './views/ProfileView.vue';
import ConfigurationView from './views/ConfigurationView.vue';
import LoginView from './views/LoginView.vue';
import RegisterView from './views/RegisterView.vue';
import LandingView from './views/LandingView.vue';
import NotFoundView from './views/NotFoundView.vue';
import PrintTestView from './views/PrintTestView.vue';
import PrintersView from './views/PrintersView.vue';

// Permission check function type
export type PermissionCheck = (user: User | null) => boolean;

export const routes: RouteRecordRaw[] = [
  // Protected routes
  {
    path: '/',
    name: 'Dashboard',
    component: DashboardView,
    meta: { requiresAuth: true }
  },
  {
    path: '/tables',
    name: 'Tables',
    component: TablesView,
    meta: { 
      requiresAuth: true,
      requiresRestaurantContext: true,
      permissionCheck: 'canManageTables' // Admin only for management
    }
  },
  {
    path: '/menu',
    name: 'Menu',
    component: MenuView,
    meta: { 
      requiresAuth: true,
      requiresRestaurantContext: true
    }
  },
  {
    path: '/categories',
    name: 'Categories',
    component: CategoriesView,
    meta: { 
      requiresAuth: true,
      requiresRestaurantContext: true,
      permissionCheck: 'canEditCategories' // Admin only
    }
  },
  {
    path: '/printers',
    name: 'Printers',
    component: PrintersView,
    meta: { 
      requiresAuth: true,
      requiresRestaurantContext: true,
      permissionCheck: 'canEditCategories' // Admin only (cloud-only)
    }
  },
  {
    path: '/cash-register',
    name: 'CashRegister',
    component: CashRegisterView,
    meta: { 
      requiresAuth: true,
      requiresRestaurantContext: true,
      permissionCheck: 'canAccessCashRegister' // Admin + Cashier
    }
  },
  {
    path: '/orders',
    name: 'Orders',
    component: OrdersView,
    meta: { 
      requiresAuth: true,
      requiresRestaurantContext: true
    }
  },
  {
    path: '/pos',
    name: 'POS',
    component: POSView,
    meta: { 
      requiresAuth: true,
      requiresRestaurantContext: true,
      requiresPOSMode: true // Only accessible in POS mode
    }
  },
  {
    path: '/kitchen',
    name: 'Kitchen',
    component: KitchenView,
    meta: { 
      requiresAuth: true,
      requiresRestaurantContext: true,
      requiresKitchenModule: true,
      permissionCheck: 'canAccessKitchen' // Admin + Kitchen staff
    }
  },
  {
    path: '/sysadmin',
    name: 'SysAdmin',
    component: SysAdminView,
    meta: { 
      requiresAuth: true,
      permissionCheck: 'isSysAdmin' // SysAdmin only
    }
  },
  {
    path: '/sysadmin/payments',
    name: 'PendingPayments',
    component: PendingPaymentsView,
    meta: { 
      requiresAuth: true,
      permissionCheck: 'isSysAdmin' // SysAdmin only
    }
  },
  {
    path: '/subscription',
    name: 'Subscription',
    component: SubscriptionView,
    meta: { 
      requiresAuth: true,
      requiresRestaurantContext: true, // Only accessible in restaurant subdomains
      permissionCheck: 'canViewSubscription' // Admin + SysAdmin
    }
  },
  {
    path: '/configuration',
    name: 'Configuration',
    component: ConfigurationView,
    meta: { 
      requiresAuth: true,
      requiresRestaurantContext: true,
      permissionCheck: 'canViewSubscription' // Admin + SysAdmin (same as subscription)
    }
  },
  {
    path: '/users',
    name: 'Users',
    component: UsersManagementView,
    meta: { 
      requiresAuth: true,
      requiresRestaurantContext: true,
      permissionCheck: 'canManageUsers' // Admin + SysAdmin
    }
  },
  {
    path: '/reports',
    name: 'Reports',
    component: ReportsView,
    meta: { 
      requiresAuth: true,
      requiresRestaurantContext: true,
      permissionCheck: 'canViewSubscription' // Admin + SysAdmin (same as subscription)
    }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: ProfileView,
    meta: { 
      requiresAuth: true // All authenticated users can view their profile
    }
  },

  // Public routes
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterView,
    meta: { requiresAuth: false }
  },

  // Marketing landing
  {
    path: '/plans',
    name: 'Plans',
    component: LandingView,
    meta: { requiresAuth: false, hideNavbar: true }
  },

  // Print testing (development only)
  {
    path: '/print-test',
    name: 'PrintTest',
    component: PrintTestView,
    meta: { requiresAuth: true }
  },

  // Catch-all
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFoundView
  }
];
