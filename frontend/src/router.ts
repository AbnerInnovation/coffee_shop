import { createRouter, createWebHistory } from 'vue-router';
import { routes } from './routes';
import { useAuthStore } from './stores/auth';
import { subscriptionService } from './services/subscriptionService';
import * as permissions from './utils/permissions';
import { hasRestaurantContext } from './utils/subdomain';
import { safeStorage } from './utils/storage';

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

  // 3. Check if route requires restaurant context (subdomain)
  if (to.meta.requiresRestaurantContext && !hasRestaurantContext()) {
    console.warn(`❌ Route ${to.path} requires restaurant context (subdomain)`);
    // If user is sysadmin, redirect to sysadmin dashboard
    if (user?.role === 'sysadmin') {
      next({ name: 'SysAdmin' });
    } else {
      // For other users, redirect to dashboard (which will show appropriate content)
      next({ name: 'Dashboard' });
    }
    return;
  }

  // 4. Check permission using permissions module
  if (to.meta.permissionCheck && typeof to.meta.permissionCheck === 'string') {
    const permissionFn = permissions[to.meta.permissionCheck as keyof typeof permissions];
    
    if (typeof permissionFn === 'function') {
      const hasPermission = permissionFn(user);
      
      if (!hasPermission) {
        console.warn(`❌ User lacks permission: ${to.meta.permissionCheck} for route: ${to.path}`);
        console.warn('User data:', { role: user?.role, staff_type: user?.staff_type });
        // Redirect to Dashboard instead of Menu to avoid lazy loading issues
        next({ name: 'Dashboard' });
        return;
      }
    }
  }

  // 5. Check kitchen module subscription (if required)
  if (to.meta.requiresKitchenModule) {
    if (!authStore.isAuthenticated) {
      next({ name: 'Login', query: { redirect: to.fullPath } });
      return;
    }

    try {
      const usage = await subscriptionService.getUsage();
      
      if (!usage.has_subscription || !usage.features?.has_kitchen_module) {
        console.warn('❌ Kitchen module not available in subscription');
        next({ name: 'Subscription' });
        return;
      }
    } catch (error) {
      console.error('Error checking kitchen module access:', error);
      next({ name: 'Dashboard' });
      return;
    }
  }

  // 6. All checks passed, proceed
  next();
});

export default router;
