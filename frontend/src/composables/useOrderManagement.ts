import { ref, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { useToast } from '@/composables/useToast';
import { useConfirm } from '@/composables/useConfirm';
import orderService from '@/services/orderService';
import type { Order } from '@/services/orderService';

// Types
type BackendOrderStatus = 'pending' | 'preparing' | 'ready' | 'completed' | 'cancelled';
type OrderStatus = BackendOrderStatus | 'all';

interface OrderItemLocal {
  id: number;
  menu_item_id: number;
  name: string;
  quantity: number;
  unit_price: number;
  total_price: number;
  notes?: string;
  variant_id?: number | null;
  status?: string;
  variant?: { id: number; name: string } | null;
  menu_item?: { id: number; name: string; category?: string; price?: number };
}

export interface OrderWithLocalFields {
  id: number;
  status: BackendOrderStatus;
  customerName: string;
  table: string;
  total: number;
  createdAt: Date;
  updated_at: string;
  total_amount?: number;
  table_id?: number | null;
  notes?: string | null;
  items: OrderItemLocal[];
  created_at?: string;
  customer_name?: string | null;
  table_number?: number | null;
  is_paid?: boolean;
}

export function useOrderManagement() {
  const route = useRoute();
  const router = useRouter();
  const { t } = useI18n();
  const { showSuccess, showError } = useToast();
  const { confirm } = useConfirm();

  // State
  const loading = ref(false);
  const error = ref<string | null>(null);
  const orders = ref<OrderWithLocalFields[]>([]);
  const selectedStatus = ref<OrderStatus>('all');
  const selectedPaymentFilter = ref<'all' | 'paid' | 'unpaid'>('all');
  const selectedOrderType = ref<'all' | 'dine_in' | 'takeaway' | 'delivery'>('all');
  const isNewOrderModalOpen = ref(false);
  const newOrderMode = ref<'create' | 'edit'>('create');
  const selectedOrderForEdit = ref<Order | null>(null);
  const isOrderDetailsOpen = ref(false);
  const selectedOrder = ref<OrderWithLocalFields | null>(null);
  const hasAutoOpenedFromTable = ref(false);
  const orderMenuStates = ref<Record<number, boolean>>({});

  // Computed
  const filteredOrders = computed<OrderWithLocalFields[]>(() => {
    let filtered = orders.value;
    
    if (selectedStatus.value !== 'all') {
      filtered = filtered.filter(order => order.status === selectedStatus.value);
    }
    
    if (selectedPaymentFilter.value === 'paid') {
      filtered = filtered.filter(order => order.is_paid === true);
    } else if (selectedPaymentFilter.value === 'unpaid') {
      filtered = filtered.filter(order => !order.is_paid);
    }
    
    if (selectedOrderType.value !== 'all') {
      const typeMap: Record<string, string> = {
        'dine_in': 'dine_in',
        'takeaway': 'takeaway',
        'delivery': 'delivery'
      };
      const targetType = typeMap[selectedOrderType.value];
      filtered = filtered.filter(order => (order as any).order_type === targetType);
    }
    
    return filtered;
  });

  // Fetch orders
  async function fetchOrders(fetchAll = false) {
    try {
      loading.value = true;
      error.value = null;

      const statusToFetch = selectedStatus.value === 'all' || fetchAll ? undefined : selectedStatus.value;
      const tableIdParam = route.query.table_id ? Number(route.query.table_id) : undefined;
      const response = await orderService.getActiveOrders(statusToFetch, tableIdParam);

      const ordersData = Array.isArray(response) ? response : [];

      const processedOrders = ordersData
        .map((order): OrderWithLocalFields | null => {
          if (!order) return null;

          const mappedItems = Array.isArray(order.items) ? order.items.map((item) => {
            const variant = item.variant;
            const menuItemName = item.menu_item?.name || 'Unknown Item';
            const variantName = variant?.name;
            const itemName = variantName ? `${menuItemName} (${variantName})` : menuItemName;

            const unitPrice = item.unit_price || 0;
            const quantity = item.quantity || 0;
            const total = unitPrice * quantity;

            return {
              id: item.id,
              menu_item_id: item.menu_item_id,
              name: itemName,
              variant_id: item.variant_id,
              quantity: quantity,
              unit_price: unitPrice,
              total_price: total,
              notes: item.special_instructions || undefined,
              status: item.status,
              variant: variant ? { id: variant.id, name: variant.name } : null,
              menu_item: item.menu_item ? {
                id: item.menu_item.id,
                name: item.menu_item.name,
                category: item.menu_item.category,
                price: item.menu_item.price
              } : undefined
            };
          }) : [];

          return {
            ...order,
            customerName: order.customer_name || 'Walk-in',
            table: order.table_number ? t('app.views.cashRegister.table_number', { number: order.table_number }) : t('app.views.cashRegister.takeaway'),
            total: order.total_amount || 0,
            createdAt: new Date(order.created_at || new Date()),
            items: mappedItems,
            status: order.status as BackendOrderStatus,
            table_number: order.table_number,
            customer_name: order.customer_name,
            notes: order.notes,
            updated_at: order.updated_at,
            is_paid: (order as any).is_paid ?? false
          };
        })
        .filter((order): order is OrderWithLocalFields => order !== null);

      orders.value = processedOrders;

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
  }

  // Update order status
  async function updateOrderStatus(orderId: number, newStatus: BackendOrderStatus) {
    try {
      await orderService.updateOrder(orderId, { status: newStatus });

      const orderIndex = orders.value.findIndex(o => o.id === orderId);
      if (orderIndex !== -1) {
        const updatedOrder = { ...orders.value[orderIndex], status: newStatus };
        orders.value.splice(orderIndex, 1, updatedOrder);
      }

      showSuccess(t('app.views.orders.messages.status_updated_success', { id: orderId, status: newStatus }) as string);
    } catch (err) {
      console.error('Error updating order status:', err);
      showError(t('app.views.orders.messages.status_update_failed') as string);
    }
  }

  // Check if order can be cancelled
  function canCancelOrder(order: OrderWithLocalFields): boolean {
    if (order.status !== 'pending') return false;
    if (!order.items || order.items.length === 0) return true;
    return order.items.every(item => !item.status || item.status === 'pending');
  }

  // Cancel order
  async function cancelOrder(orderId: number) {
    const order = orders.value.find(o => o.id === orderId);
    
    if (!order) {
      showError(t('app.views.orders.messages.order_not_found') as string);
      return;
    }
    
    if (!canCancelOrder(order)) {
      showError('No se puede cancelar una orden que ya está en preparación o lista.');
      return;
    }
    
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

      const orderIndex = orders.value.findIndex(o => o.id === orderId);
      if (orderIndex !== -1) {
        const updatedOrder = { ...orders.value[orderIndex], status: 'cancelled' as const };
        orders.value.splice(orderIndex, 1, updatedOrder);
      }

      showSuccess(t('app.views.orders.messages.order_cancelled_success') as string);
    } catch (err) {
      console.error('Error cancelling order:', err);
      showError(t('app.views.orders.messages.cancel_failed') as string);
    }
  }

  // View order details
  function viewOrderDetails(order: OrderWithLocalFields) {
    selectedOrder.value = { ...order };
    isOrderDetailsOpen.value = true;
  }

  // Close order details
  function closeOrderDetails() {
    isOrderDetailsOpen.value = false;
    setTimeout(() => {
      selectedOrder.value = null;
    }, 300);
  }

  // Open new order modal
  function openNewOrderModal() {
    isNewOrderModalOpen.value = true;
  }

  // Close new order modal
  function closeNewOrderModal() {
    isNewOrderModalOpen.value = false;
    newOrderMode.value = 'create';
  }

  // Open edit order
  async function openEditOrder(order: OrderWithLocalFields) {
    try {
      isOrderDetailsOpen.value = false;
      newOrderMode.value = 'edit';
      const fullOrder = await orderService.getOrder(order.id);
      selectedOrderForEdit.value = fullOrder;
      isNewOrderModalOpen.value = true;
    } catch (e) {
      console.error('Failed to open edit order modal:', e);
    }
  }

  // Handle new order
  async function handleNewOrder(newOrder: Order) {
    try {
      await fetchOrders();
      closeNewOrderModal();
    } catch (err) {
      console.error('Error processing new order:', err);
      if (!newOrder?.id) {
        showError(t('app.views.orders.messages.fetch_failed') as string);
      } else {
        closeNewOrderModal();
      }
    }
  }

  // Handle order updated
  function handleOrderUpdated(updated: any) {
    try {
      const idx = orders.value.findIndex(o => o.id === updated.id);
      if (idx !== -1) {
        const existing = orders.value[idx];
        orders.value.splice(idx, 1, {
          ...existing,
          status: updated.status as BackendOrderStatus,
          table: updated.table_number ? t('app.views.cashRegister.table_number', { number: updated.table_number }) : t('app.views.cashRegister.takeaway'),
          total: updated.total_amount || 0,
          updated_at: updated.updated_at || existing.updated_at,
          items: (updated.items || existing.items),
          table_id: updated.table_id ?? existing.table_id,
          notes: updated.notes ?? existing.notes,
          is_paid: (updated as any).is_paid ?? existing.is_paid
        });
      }
      showSuccess(t('app.views.orders.messages.order_updated_success', { id: updated.id }) as string);
      fetchOrders(true);
      selectedOrderForEdit.value = null;
      newOrderMode.value = 'create';
    } catch (e) {
      console.error('Failed updating local order after edit:', e);
    }
  }

  // Handle status update
  function handleStatusUpdate({ orderId, status }: { orderId: number; status: OrderStatus }) {
    if (status !== 'all') {
      updateOrderStatus(orderId, status as BackendOrderStatus);
      closeOrderDetails();
    }
  }

  // Handle payment completed
  async function handlePaymentCompleted(updatedOrder: any) {
    try {
      showSuccess(t('app.views.orders.messages.payment_completed_success', { id: updatedOrder.id }) as string);
      await fetchOrders(true);
      window.dispatchEvent(new CustomEvent('orderPaymentCompleted', {
        detail: { orderId: updatedOrder.id }
      }));
    } catch (e) {
      console.error('Failed to update order after payment completion:', e);
    }
  }

  // Handle open cash register
  function handleOpenCashRegister() {
    router.push('/cash-register');
  }

  // Close menu and execute action
  function closeMenuAndExecute(orderId: number, action: () => void) {
    orderMenuStates.value[orderId] = false;
    action();
  }

  return {
    // State
    loading,
    error,
    orders,
    selectedStatus,
    selectedPaymentFilter,
    selectedOrderType,
    isNewOrderModalOpen,
    newOrderMode,
    selectedOrderForEdit,
    isOrderDetailsOpen,
    selectedOrder,
    orderMenuStates,
    filteredOrders,
    
    // Methods
    fetchOrders,
    updateOrderStatus,
    canCancelOrder,
    cancelOrder,
    viewOrderDetails,
    closeOrderDetails,
    openNewOrderModal,
    closeNewOrderModal,
    openEditOrder,
    handleNewOrder,
    handleOrderUpdated,
    handleStatusUpdate,
    handlePaymentCompleted,
    handleOpenCashRegister,
    closeMenuAndExecute
  };
}
