import { ref } from 'vue';
import { adminService } from '@/services/adminService';

/**
 * Composable for managing restaurant statistics
 */
export function useRestaurantStats() {
  const stats = ref<any>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  /**
   * Load restaurant statistics
   */
  const loadStats = async () => {
    loading.value = true;
    error.value = null;
    
    try {
      stats.value = await adminService.getStats();
    } catch (err: any) {
      console.error('Error loading stats:', err);
      error.value = err.message || 'Failed to load statistics';
    } finally {
      loading.value = false;
    }
  };

  return {
    // State
    stats,
    loading,
    error,
    
    // Actions
    loadStats
  };
}
