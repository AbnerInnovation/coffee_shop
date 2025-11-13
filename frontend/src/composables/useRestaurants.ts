import { ref } from 'vue';
import { adminService } from '@/services/adminService';

/**
 * Composable for managing restaurants data and operations
 */
export function useRestaurants() {
  const restaurants = ref<any[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const searchQuery = ref('');
  const filterSubscription = ref<boolean | null>(null);

  /**
   * Load restaurants with optional filters
   */
  const loadRestaurants = async () => {
    loading.value = true;
    error.value = null;
    
    try {
      restaurants.value = await adminService.getRestaurants({
        search: searchQuery.value || undefined,
        has_subscription: filterSubscription.value !== null ? filterSubscription.value : undefined
      });
    } catch (err: any) {
      console.error('Error loading restaurants:', err);
      error.value = err.message || 'Failed to load restaurants';
    } finally {
      loading.value = false;
    }
  };

  /**
   * Debounced search
   */
  let searchTimeout: any = null;
  const debouncedSearch = () => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      loadRestaurants();
    }, 500);
  };

  /**
   * Clear filters
   */
  const clearFilters = () => {
    searchQuery.value = '';
    filterSubscription.value = null;
  };

  return {
    // State
    restaurants,
    loading,
    error,
    searchQuery,
    filterSubscription,
    
    // Actions
    loadRestaurants,
    debouncedSearch,
    clearFilters
  };
}
