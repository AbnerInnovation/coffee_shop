import { ref, onMounted, computed } from 'vue';
import { getSubdomain, hasRestaurantContext } from '@/utils/subdomain';
import api from '@/services/api';

export interface Restaurant {
  id: number;
  name: string;
  subdomain: string;
  description?: string;
  logo_url?: string;
  timezone: string;
  currency: string;
  address?: string;
  phone?: string;
  email?: string;
}

/**
 * Composable for managing restaurant context
 */
export function useRestaurant() {
  const restaurant = ref<Restaurant | null>(null);
  const loading = ref(true);
  const error = ref<string | null>(null);
  
  const subdomain = computed(() => getSubdomain());
  const hasContext = computed(() => hasRestaurantContext());
  
  /**
   * Fetch the current restaurant information
   */
  const fetchRestaurant = async () => {
    if (!hasContext.value) {
      loading.value = false;
      return;
    }
    
    try {
      loading.value = true;
      error.value = null;
      
      const response = await api.get('/restaurants/current');
      restaurant.value = response.data;
    } catch (err: any) {
      console.error('Failed to fetch restaurant:', err);
      error.value = err.response?.data?.detail || 'Failed to load restaurant information';
      restaurant.value = null;
    } finally {
      loading.value = false;
    }
  };
  
  /**
   * Refresh restaurant data
   */
  const refresh = () => {
    return fetchRestaurant();
  };
  
  // Auto-fetch on mount
  onMounted(() => {
    fetchRestaurant();
  });
  
  return {
    restaurant,
    loading,
    error,
    subdomain,
    hasContext,
    fetchRestaurant,
    refresh
  };
}
