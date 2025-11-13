import { ref } from 'vue';
import { adminService, type GlobalStats } from '@/services/adminService';

/**
 * Composable for managing SysAdmin global statistics
 */
export function useSysAdminStats() {
  const stats = ref<GlobalStats | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  /**
   * Load global statistics
   */
  const loadStats = async () => {
    loading.value = true;
    error.value = null;
    
    try {
      stats.value = await adminService.getGlobalStats();
    } catch (err: any) {
      console.error('Error loading global stats:', err);
      error.value = err.message || 'Failed to load statistics';
    } finally {
      loading.value = false;
    }
  };

  /**
   * Refresh statistics
   */
  const refreshStats = async () => {
    await loadStats();
  };

  /**
   * Clear error
   */
  const clearError = () => {
    error.value = null;
  };

  return {
    // State
    stats,
    loading,
    error,
    
    // Actions
    loadStats,
    refreshStats,
    clearError
  };
}
