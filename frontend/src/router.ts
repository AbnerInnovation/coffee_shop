import { createRouter, createWebHistory } from 'vue-router';
import { routes } from './routes';
import { useAuthStore } from './stores/auth';
import { subscriptionService } from './services/subscriptionService';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    return savedPosition || { top: 0 };
  }
});

// Preserve original auth guard logic
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } });
  } else if ((to.name === 'Login' || to.name === 'Register') && authStore.isAuthenticated) {
    next({ name: 'Dashboard' });
  } else if (to.meta.requiresSysAdmin && authStore.user?.role !== 'sysadmin') {
    // Redirect non-sysadmin users trying to access sysadmin routes
    next({ name: 'Dashboard' });
  } else if (to.meta.requiresKitchenModule) {
    // Check if user has access to kitchen module (only if authenticated)
    if (!authStore.isAuthenticated) {
      next({ name: 'Login', query: { redirect: to.fullPath } });
    } else {
      try {
        const usage = await subscriptionService.getUsage();
        if (!usage.has_subscription || !usage.limits?.has_kitchen_module) {
          // Redirect to subscription page if kitchen module not available
          next({ name: 'Subscription' });
        } else {
          next();
        }
      } catch (error) {
        console.error('Error checking kitchen module access:', error);
        next({ name: 'Dashboard' });
      }
    }
  } else {
    next();
  }
});

export default router;
