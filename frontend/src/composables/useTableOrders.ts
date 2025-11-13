import { ref } from 'vue';
import orderService from '@/services/orderService';

/**
 * Composable for managing table orders
 * Tracks open orders and provides order-related operations
 */
export function useTableOrders() {
  const openOrderTableIds = ref<Set<number>>(new Set());
  const loading = ref(false);
  const error = ref('');

  /**
   * Refresh the list of tables with open orders
   */
  const refreshOpenOrders = async () => {
    try {
      loading.value = true;
      error.value = '';
      
      // Fetch active orders (pending, preparing, ready) and not paid
      const allOrders = await orderService.getActiveOrders();
      const activeOrders = (Array.isArray(allOrders) ? allOrders : []).filter(
        o => o && 
             o.table_id && 
             o.status !== 'completed' && 
             o.status !== 'cancelled' && 
             !o.is_paid
      );
      
      openOrderTableIds.value = new Set(
        activeOrders.map(o => o.table_id).filter((id): id is number => id !== null)
      );
    } catch (e) {
      console.warn('Failed to fetch open orders for tables view:', e);
      error.value = 'Failed to load open orders';
    } finally {
      loading.value = false;
    }
  };

  /**
   * Check if a table has an open order
   */
  const hasOpenOrder = (tableId: number): boolean => {
    return openOrderTableIds.value.has(tableId);
  };

  /**
   * Get the open order for a specific table
   */
  const getOpenOrderForTable = async (tableId: number) => {
    try {
      const orders = await orderService.getActiveOrders(undefined, tableId);
      const openOrder = orders.find(
        o => o.table_id === tableId && 
             o.status !== 'completed' && 
             o.status !== 'cancelled' && 
             !o.is_paid
      );
      
      return openOrder || null;
    } catch (err) {
      console.error('Error fetching order for table:', err);
      throw new Error('Failed to fetch order. Please try again.');
    }
  };

  /**
   * Get full order details for viewing bill
   */
  const getOrderDetails = async (orderId: number) => {
    try {
      return await orderService.getOrder(orderId);
    } catch (err) {
      console.error('Error fetching order details:', err);
      throw new Error('Failed to fetch order details. Please try again.');
    }
  };

  /**
   * Clear error message
   */
  const clearError = () => {
    error.value = '';
  };

  return {
    // State
    openOrderTableIds,
    loading,
    error,
    
    // Actions
    refreshOpenOrders,
    hasOpenOrder,
    getOpenOrderForTable,
    getOrderDetails,
    clearError
  };
}
