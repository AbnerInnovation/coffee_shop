import { ref } from 'vue';
import { subscriptionService, type SubscriptionUsage } from '@/services/subscriptionService';

/**
 * Composable for managing subscription usage
 */
export function useSubscriptionUsage() {
  const usage = ref<SubscriptionUsage | null>(null);
  const loading = ref(false);
  const error = ref('');

  /**
   * Load subscription usage
   */
  const loadUsage = async () => {
    loading.value = true;
    error.value = '';
    try {
      usage.value = await subscriptionService.getUsage();
    } catch (err) {
      console.error('Error loading usage:', err);
      error.value = 'Failed to load usage';
    } finally {
      loading.value = false;
    }
  };

  /**
   * Calculate percentage of usage
   */
  const calculatePercentage = (current: number, max: number): number => {
    if (max === -1 || max === 0) return 0;
    return Math.round((current / max) * 100);
  };

  /**
   * Clear error
   */
  const clearError = () => {
    error.value = '';
  };

  return {
    // State
    usage,
    loading,
    error,
    
    // Actions
    loadUsage,
    calculatePercentage,
    clearError
  };
}
