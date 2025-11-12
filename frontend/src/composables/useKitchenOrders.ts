import { ref, onMounted, onUnmounted } from 'vue';
import type { Order } from '@/services/orderService';
import orderService from '@/services/orderService';
import { initializeOrderItems } from '@/utils/kitchenHelpers';

/**
 * Composable for kitchen orders management
 * Implements Single Responsibility Principle - only handles order fetching and auto-refresh
 */
export function useKitchenOrders() {
  const loading = ref(true);
  const activeOrders = ref<Order[]>([]);
  let refreshInterval: number | null = null;

  /**
   * Fetch active orders (pending or preparing)
   */
  const fetchActiveOrders = async () => {
    try {
      loading.value = true;
      const pendingOrders = await orderService.getActiveOrders('pending', undefined, 'kitchen');
      const preparingOrders = await orderService.getActiveOrders('preparing', undefined, 'kitchen');

      // Backend already orders by status (pending first) then by updated_at (FIFO)
      // Just combine the arrays
      const allOrders = [...pendingOrders, ...preparingOrders];

      // Initialize item statuses if not set
      activeOrders.value = allOrders.map(order => initializeOrderItems(order));
    } catch (error) {
      console.error('Error fetching active orders:', error);
    } finally {
      loading.value = false;
    }
  };

  /**
   * Set up auto-refresh every 30 seconds
   */
  const setupAutoRefresh = () => {
    // Initial fetch
    fetchActiveOrders();

    // Set up polling every 30 seconds
    refreshInterval = window.setInterval(fetchActiveOrders, 30000);
  };

  /**
   * Clean up interval on unmount
   */
  const cleanup = () => {
    if (refreshInterval) {
      clearInterval(refreshInterval);
      refreshInterval = null;
    }
  };

  // Lifecycle hooks
  onMounted(setupAutoRefresh);
  onUnmounted(cleanup);

  return {
    // State
    loading,
    activeOrders,

    // Methods
    fetchActiveOrders,
    cleanup
  };
}
