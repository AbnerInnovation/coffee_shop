import { ref, watch, type Ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import orderService from '@/services/orderService';
import type { Order } from '@/services/orderService';
import tableService, { type Table } from '@/services/tableService';
import { useToast } from '@/composables/useToast';
import { useConfirm } from '@/composables/useConfirm';
import {
  canCancelOrder as canCancelOrderHelper,
  transformOrderToLocal,
  type OrderWithLocalFields,
  type BackendOrderStatus,
  type OrderStatus
} from '@/utils/orderHelpers';

/**
 * Tab definition for order status filtering
 */
interface OrderTab {
  id: OrderStatus;
  name: string;
  count: number;
  loaded: boolean;
}

/**
 * Composable for managing OrdersView business logic
 * 
 * Handles:
 * - Order fetching and state management
 * - Status updates and cancellations
 * - Tab management with lazy loading
 * - Modal state (new order, edit, details)
 * - Table filtering
 * 
 * @returns Object with all order management functions and state
 * 
 * @example
 * ```typescript
 * const {
 *   orders,
 *   loading,
 *   fetchOrders,
 *   updateOrderStatus,
 *   cancelOrder
 * } = useOrdersView();
 * 
 * onMounted(() => {
 *   fetchOrders();
 * });
 * ```
 */
export function useOrdersView() {
  const { t } = useI18n();
  const route = useRoute();
  const router = useRouter();
  const { showSuccess, showError } = useToast();
  const { confirm } = useConfirm();

  // ==================== State ====================
  const loading = ref(false);
  const error = ref<string | null>(null);
  const orders = ref<OrderWithLocalFields[]>([]);
  const tables = ref<Table[]>([]);
  const selectedStatus = ref<OrderStatus>('pending');
  
  // Modal states
  const isNewOrderModalOpen = ref(false);
  const newOrderMode = ref<'create' | 'edit'>('create');
  const selectedOrderForEdit = ref<Order | null>(null);
  const isOrderDetailsOpen = ref(false);
  const selectedOrder = ref<OrderWithLocalFields | null>(null);
  const hasAutoOpenedFromTable = ref(false);
  
  // Cleanup tracking
  let closeDetailsTimeout: ReturnType<typeof setTimeout> | null = null;

  // Tab definitions with cache tracking
  const tabs: OrderTab[] = [
    { id: 'pending' as const, name: 'Pending', count: 0, loaded: false },
    { id: 'preparing' as const, name: 'Preparing', count: 0, loaded: false },
    { id: 'ready' as const, name: 'Ready', count: 0, loaded: false },
    { id: 'completed' as const, name: 'Completed', count: 0, loaded: false },
  ];

  // ==================== Tab Management ====================
  
  /**
   * Fetches the count for a specific tab (lazy loading)
   * Skips if already loaded to avoid unnecessary API calls
   * 
   * @param tabId - The status to fetch count for
   */
  const fetchTabCount = async (tabId: OrderStatus) => {
    try {
      const tab = tabs.find(t => t.id === tabId);
      if (!tab || tab.loaded) return;
      
      const response = await orderService.getActiveOrders(tabId, undefined);
      tab.count = response.length;
      tab.loaded = true;
    } catch (error) {
      console.error(`Error fetching count for tab ${tabId}:`, error);
    }
  };

  /**
   * Invalidates all tab counts to force reload on next access
   * Called after order creation, updates, or status changes
   */
  const invalidateTabCounts = () => {
    tabs.forEach(tab => {
      tab.loaded = false;
    });
  };

  /**
   * Handles tab selection and lazy loads count if needed
   * 
   * @param tabId - The tab to select
   */
  const selectTab = async (tabId: OrderStatus) => {
    selectedStatus.value = tabId;
    await fetchTabCount(tabId);
  };

  // ==================== Order Fetching ====================
  
  /**
   * Fetches orders from API with optional filtering
   * Transforms orders to local format with translated fields
   * Handles auto-opening of order details when filtered by table
   * 
   * @param fetchAll - If true, fetches all orders regardless of status filter
   */
  const fetchOrders = async (fetchAll = false) => {
    try {
      loading.value = true;
      error.value = null;

      const statusToFetch = fetchAll ? undefined : selectedStatus.value;
      const tableIdParam = route.query.table_id ? Number(route.query.table_id) : undefined;
      const response = await orderService.getActiveOrders(statusToFetch, tableIdParam);

      const ordersData = Array.isArray(response) ? response : [];

      // Transform using helper function with i18n
      const processedOrders = ordersData
        .map(order => transformOrderToLocal(order, t))
        .filter((order): order is OrderWithLocalFields => order !== null);

      orders.value = processedOrders;

      // Update current tab count
      const currentTab = tabs.find(t => t.id === selectedStatus.value);
      if (currentTab) {
        currentTab.count = processedOrders.length;
        currentTab.loaded = true;
      }

      // Auto-open first order if filtered by table (one-time only)
      if (tableIdParam && orders.value.length > 0 && !hasAutoOpenedFromTable.value) {
        hasAutoOpenedFromTable.value = true;
        viewOrderDetails(orders.value[0]);
      }
    } catch (err) {
      console.error('Error fetching orders:', err);
      error.value = t('app.views.orders.messages.fetch_failed') as string;
    } finally {
      loading.value = false;
    }
  };

  /**
   * Fetches available tables for filtering
   */
  const fetchTables = async () => {
    try {
      tables.value = await tableService.getTables();
    } catch (err) {
      console.error('Error fetching tables for filter:', err);
    }
  };

  // ==================== Order Status Management ====================
  
  /**
   * Updates an order's status in the backend and local state
   * 
   * @param orderId - ID of the order to update
   * @param newStatus - New status to set
   */
  const updateOrderStatus = async (orderId: number, newStatus: BackendOrderStatus) => {
    try {
      await orderService.updateOrder(orderId, { status: newStatus });

      // Update local state
      const orderIndex = orders.value.findIndex(o => o.id === orderId);
      if (orderIndex !== -1) {
        const updatedOrder = { ...orders.value[orderIndex], status: newStatus };
        orders.value.splice(orderIndex, 1, updatedOrder);
      }

      invalidateTabCounts();

      const statusText = t(`app.status.${newStatus}`);
      showSuccess(t('app.views.orders.messages.status_updated_success', { id: orderId, status: statusText }) as string);
    } catch (err) {
      console.error('Error updating order status:', err);
      showError(t('app.views.orders.messages.status_update_failed') as string);
    }
  };

  /**
   * Cancels an order after validation and confirmation
   * Only allows cancellation of pending orders that are not paid
   * 
   * @param orderId - ID of the order to cancel
   */
  const cancelOrder = async (orderId: number) => {
    const order = orders.value.find(o => o.id === orderId);

    if (!order) {
      showError(t('app.views.orders.messages.order_not_found') as string);
      return;
    }

    // Validate if order can be cancelled using helper
    if (!canCancelOrderHelper(order)) {
      if (order.is_paid) {
        showError('No se puede cancelar un pedido que ya está pagado.');
      } else {
        showError('No se puede cancelar una orden que ya está en preparación o lista. Solo se pueden cancelar órdenes pendientes con todos sus items pendientes.');
      }
      return;
    }

    // Confirm with user
    const confirmed = await confirm(
      t('app.views.orders.modals.confirm.cancel_title') as string,
      t('app.views.orders.modals.confirm.cancel_message') as string,
      t('app.views.orders.modals.confirm.confirm') as string,
      t('app.views.orders.modals.confirm.cancel') as string,
      'bg-red-600 hover:bg-red-700 focus:ring-red-500'
    );

    if (!confirmed) return;

    try {
      await orderService.updateOrder(orderId, { status: 'cancelled' });

      // Update local state
      const orderIndex = orders.value.findIndex(o => o.id === orderId);
      if (orderIndex !== -1) {
        const updatedOrder = {
          ...orders.value[orderIndex],
          status: 'cancelled' as const
        };
        orders.value.splice(orderIndex, 1, updatedOrder);
      }

      invalidateTabCounts();
      showSuccess(t('app.views.orders.messages.order_cancelled_success') as string);
    } catch (err) {
      console.error('Error cancelling order:', err);
      showError(t('app.views.orders.messages.cancel_failed') as string);
    }
  };

  // ==================== Modal Management ====================
  
  /**
   * Opens the new order modal in create mode
   */
  const openNewOrderModal = () => {
    isNewOrderModalOpen.value = true;
  };

  /**
   * Closes the new order modal and resets mode to create
   */
  const closeNewOrderModal = () => {
    isNewOrderModalOpen.value = false;
    newOrderMode.value = 'create';
  };

  /**
   * Opens the edit order modal with full order data
   * Fetches complete order data from API before opening
   * 
   * @param order - The order to edit
   */
  const openEditOrder = async (order: OrderWithLocalFields) => {
    try {
      isOrderDetailsOpen.value = false;
      newOrderMode.value = 'edit';
      
      // Fetch full order data from API
      const fullOrder = await orderService.getOrder(order.id);
      selectedOrderForEdit.value = fullOrder;
      isNewOrderModalOpen.value = true;
    } catch (e) {
      console.error('Failed to open edit order modal:', e);
    }
  };

  /**
   * Opens the order details modal
   * 
   * @param order - The order to view
   */
  const viewOrderDetails = (order: OrderWithLocalFields) => {
    selectedOrder.value = { ...order };
    // Use nextTick in component
    isOrderDetailsOpen.value = true;
  };

  /**
   * Closes the order details modal with transition delay
   * Clears selected order after transition completes
   */
  const closeOrderDetails = () => {
    isOrderDetailsOpen.value = false;

    if (closeDetailsTimeout) {
      clearTimeout(closeDetailsTimeout);
    }

    // Wait for transition to complete (300ms)
    closeDetailsTimeout = setTimeout(() => {
      selectedOrder.value = null;
      closeDetailsTimeout = null;
    }, 300);
  };

  // ==================== Event Handlers ====================
  
  /**
   * Handles successful order creation
   * Refetches orders and invalidates tab counts
   * 
   * @param newOrder - The newly created order
   */
  const handleNewOrder = async (newOrder: Order) => {
    try {
      await fetchOrders();
      invalidateTabCounts();
      closeNewOrderModal();
    } catch (err) {
      console.error('Error processing new order:', err);
      
      // Only show error if order wasn't created
      if (!newOrder?.id) {
        showError(t('app.views.orders.messages.fetch_failed') as string);
      } else {
        closeNewOrderModal();
      }
    }
  };

  /**
   * Handles successful order update
   * Updates local state and refetches for consistency
   * 
   * @param updated - The updated order data
   */
  const handleOrderUpdated = (updated: any) => {
    try {
      const idx = orders.value.findIndex(o => o.id === updated.id);
      if (idx !== -1) {
        const existing = orders.value[idx];
        orders.value.splice(idx, 1, {
          ...existing,
          status: updated.status as BackendOrderStatus,
          table: updated.table_number 
            ? t('app.views.cashRegister.table_number', { number: updated.table_number }) 
            : t('app.views.cashRegister.takeaway'),
          total: updated.total_amount || 0,
          updated_at: updated.updated_at || existing.updated_at,
          items: (updated.items || existing.items),
          table_id: updated.table_id ?? existing.table_id,
          notes: updated.notes ?? existing.notes,
          is_paid: (updated as any).is_paid ?? existing.is_paid
        });
      }
      
      showSuccess(t('app.views.orders.messages.order_updated_success', { id: updated.id }) as string);
      
      // Ensure consistency by refetching
      fetchOrders(true);
      invalidateTabCounts();
      
      // Reset edit state
      selectedOrderForEdit.value = null;
      newOrderMode.value = 'create';
    } catch (e) {
      console.error('Failed updating local order after edit:', e);
    }
  };

  /**
   * Handles status update from order details modal
   * 
   * @param payload - Object containing orderId and new status
   */
  const handleStatusUpdate = ({ orderId, status }: { orderId: number; status: OrderStatus }) => {
    updateOrderStatus(orderId, status as BackendOrderStatus);
    closeOrderDetails();
  };

  /**
   * Handles payment completion
   * Refreshes orders and dispatches event for cash register
   * 
   * @param updatedOrder - The order with completed payment
   */
  const handlePaymentCompleted = async (updatedOrder: any) => {
    try {
      showSuccess(t('app.views.orders.messages.payment_completed_success', { id: updatedOrder.id }) as string);

      await fetchOrders(true);
      invalidateTabCounts();

      // Notify cash register component if open
      window.dispatchEvent(new CustomEvent('orderPaymentCompleted', {
        detail: { orderId: updatedOrder.id }
      }));
    } catch (e) {
      console.error('Failed to update order after payment completion:', e);
    }
  };

  /**
   * Navigates to cash register view
   */
  const handleOpenCashRegister = () => {
    router.push('/cash-register');
  };

  // ==================== Watchers ====================
  
  /**
   * Refetch orders when status filter changes
   */
  watch(selectedStatus, () => {
    fetchOrders();
  });

  // ==================== Cleanup ====================
  
  /**
   * Cleanup function to be called on component unmount
   * Clears any pending timeouts
   */
  const cleanup = () => {
    if (closeDetailsTimeout) {
      clearTimeout(closeDetailsTimeout);
    }
  };

  // ==================== Return ====================
  
  return {
    // State
    loading,
    error,
    orders,
    tables,
    selectedStatus,
    tabs,
    
    // Modal states
    isNewOrderModalOpen,
    newOrderMode,
    selectedOrderForEdit,
    isOrderDetailsOpen,
    selectedOrder,
    
    // Fetching
    fetchOrders,
    fetchTables,
    
    // Tab management
    selectTab,
    fetchTabCount,
    invalidateTabCounts,
    
    // Order operations
    updateOrderStatus,
    cancelOrder,
    
    // Modal operations
    openNewOrderModal,
    closeNewOrderModal,
    openEditOrder,
    viewOrderDetails,
    closeOrderDetails,
    
    // Event handlers
    handleNewOrder,
    handleOrderUpdated,
    handleStatusUpdate,
    handlePaymentCompleted,
    handleOpenCashRegister,
    
    // Cleanup
    cleanup
  };
}
