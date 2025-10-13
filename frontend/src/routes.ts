import type { RouteRecordRaw } from 'vue-router';

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
    meta: { requiresAuth: true }
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
    meta: { requiresAuth: true }
  },
  {
    path: '/cash-register',
    name: 'CashRegister',
    component: () => import('./views/CashRegisterView.vue'),
    meta: { requiresAuth: true }
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
    meta: { requiresAuth: true }
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
    meta: { requiresAuth: false }
  },

  // Catch-all
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('./views/NotFoundView.vue')
  }
];
