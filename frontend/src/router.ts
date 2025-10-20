import { createRouter, createWebHistory } from 'vue-router';
import { routes } from './routes';
import { useAuthStore } from './stores/auth';
import { subscriptionService } from './services/subscriptionService';
import * as permissions from './utils/permissions';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    return savedPosition || { top: 0 };
  }
});

/**
 * Global navigation guard with permission checks
 * Uses the centralized permissions module for consistent access control
 */
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();
  
  // Wait for auth check to complete if there's a token but no user yet
  const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
  
  if (token && !authStore.user) {
    // Give the store a moment to initialize
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // If still no user after wait, try to check auth
    if (!authStore.user && !authStore.loading) {
      try {
        await authStore.checkAuth();
      } catch (error) {
        console.error('Auth check failed in router guard:', error);
      }
    }
  }
  
  const user = authStore.user;

  // 1. Check authentication requirement
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } });
    return;
  }

  // 2. Redirect authenticated users away from login/register
  if ((to.name === 'Login' || to.name === 'Register') && authStore.isAuthenticated) {
    next({ name: 'Dashboard' });
    return;
  }

  // 3. Check permission using permissions module
  if (to.meta.permissionCheck && typeof to.meta.permissionCheck === 'string') {
    const permissionFn = permissions[to.meta.permissionCheck as keyof typeof permissions];
    
    if (typeof permissionFn === 'function') {
      const hasPermission = permissionFn(user);
      
      if (!hasPermission) {
        console.warn(`User lacks permission: ${to.meta.permissionCheck} for route: ${to.path}`);
        next({ name: 'Dashboard' });
        return;
      }
    }
  }

  // 4. Check kitchen module subscription (if required)
  if (to.meta.requiresKitchenModule) {
    if (!authStore.isAuthenticated) {
      next({ name: 'Login', query: { redirect: to.fullPath } });
      return;
    }

    try {
      const usage = await subscriptionService.getUsage();
      
      if (!usage.has_subscription || !usage.limits?.has_kitchen_module) {
        console.warn('Kitchen module not available in subscription');
        next({ name: 'Subscription' });
        return;
      }
    } catch (error) {
      console.error('Error checking kitchen module access:', error);
      next({ name: 'Dashboard' });
      return;
    }
  }

  // 5. All checks passed, proceed
  next();
});

export default router;
