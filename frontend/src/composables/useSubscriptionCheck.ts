import { ref, onMounted, onUnmounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import { subscriptionService, type SubscriptionStatus } from '@/services/subscriptionService';
import { useAuthStore } from '@/stores/auth';

export function useSubscriptionCheck() {
  const authStore = useAuthStore();
  const route = useRoute();
  const subscriptionStatus = ref<SubscriptionStatus | null>(null);
  const isChecking = ref(false);
  const showSuspendedModal = ref(false);

  /**
   * Check if subscription is active
   */
  const checkSubscription = async (): Promise<boolean> => {
    // SYSADMIN bypasses subscription check
    if (authStore.user?.role === 'sysadmin') {
      return true;
    }

    // Skip check if no user
    if (!authStore.user) {
      return false;
    }

    try {
      isChecking.value = true;
      const status = await subscriptionService.checkStatus();
      subscriptionStatus.value = status;

      // Show modal if subscription is not active
      if (!status.can_operate) {
        showSuspendedModal.value = true;
        return false;
      }

      return true;
    } catch (error) {
      console.error('Error checking subscription:', error);
      // On error, assume active to avoid blocking operations
      return true;
    } finally {
      isChecking.value = false;
    }
  };

  /**
   * Close the suspended modal
   */
  const closeSuspendedModal = () => {
    showSuspendedModal.value = false;
  };

  /**
   * Handle subscription error event from API interceptor
   */
  const handleSubscriptionError = (event: CustomEvent) => {
    const message = event.detail?.message || 'Tu suscripción ha expirado';
    
    // Update status and show modal
    subscriptionStatus.value = {
      is_active: false,
      status: 'expired',
      message: message,
      can_operate: false,
      days_remaining: 0
    };
    
    showSuspendedModal.value = true;
  };

  /**
   * Watch for authentication changes to check subscription after login
   */
  watch(
    () => authStore.isAuthenticated,
    (isAuthenticated) => {
      if (isAuthenticated && authStore.user?.role !== 'sysadmin') {
        // Check subscription immediately after login
        checkSubscription();
      } else if (!isAuthenticated) {
        // Reset state on logout
        subscriptionStatus.value = null;
        showSuspendedModal.value = false;
      }
    }
  );

  /**
   * Watch for route changes to enforce subscription check
   * If subscription is suspended, prevent navigation to other pages (except subscription page)
   */
  watch(
    () => route.path,
    (newPath) => {
      // If user is sysadmin, ignore
      if (authStore.user?.role === 'sysadmin') return;

      // If subscription status is known and invalid
      if (subscriptionStatus.value && !subscriptionStatus.value.can_operate) {
        // Allow access only to subscription page and login
        if (newPath !== '/subscription' && newPath !== '/login') {
          showSuspendedModal.value = true;
        }
      }
    }
  );

  /**
   * Listen for subscription errors and check on mount if authenticated
   */
  onMounted(() => {
    // Listen for subscription errors from API interceptor
    window.addEventListener('subscription-error', handleSubscriptionError as EventListener);
    
    // Check subscription status on mount if user is authenticated
    // This ensures the modal shows immediately after login if subscription is expired
    if (authStore.isAuthenticated && authStore.user?.role !== 'sysadmin') {
      checkSubscription();
    }
  });

  /**
   * Cleanup event listener
   */
  onUnmounted(() => {
    window.removeEventListener('subscription-error', handleSubscriptionError as EventListener);
  });

  return {
    subscriptionStatus,
    isChecking,
    showSuspendedModal,
    checkSubscription,
    closeSuspendedModal
  };
}
