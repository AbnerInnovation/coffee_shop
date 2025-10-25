<template>
  <MainLayout>
    <div class="space-y-6">
    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 border-l-4 border-red-400 p-4">
      <div class="flex">
        <div class="flex-shrink-0">
          <XMarkIcon class="h-5 w-5 text-red-400" aria-hidden="true" />
        </div>
        <div class="ml-3">
          <p class="text-sm text-red-700">{{ error }}</p>
          <button @click="() => fetchOrders()"
            class="mt-2 text-sm font-medium text-red-700 hover:text-red-600 focus:outline-none">
            {{ t('app.views.orders.try_again') }} <span aria-hidden="true">&rarr;</span>
          </button>
        </div>
      </div>
    </div>

    <div v-else class="space-y-4 sm:space-y-6">
      <PageHeader
        :title="t('app.views.orders.title')"
        :subtitle="selectedStatus === 'all' ? t('app.views.orders.tabs.all') + ' ' + t('app.views.orders.title').toLowerCase() : t('app.status.' + selectedStatus) + ' ' + t('app.views.orders.title').toLowerCase()"
      >
        <template #actions>
          <button
            type="button"
            @click="openNewOrderModal"
            class="block rounded-md bg-indigo-600 px-3 py-2 text-center text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
          >
            <PlusIcon class="-ml-1 mr-2 h-5 w-5 inline" aria-hidden="true" />
            {{ t('app.views.orders.new_order') }}
          </button>
        </template>
      </PageHeader>
      <!-- Filters Component -->
      <OrderFilters
        :tabs="tabs"
        :selected-status="selectedStatus"
        :payment-filter="selectedPaymentFilter"
        :order-type="selectedOrderType"
        @select-tab="selectTab"
        @update:payment-filter="selectedPaymentFilter = $event"
        @update:order-type="selectedOrderType = $event"
      />

      <!-- Order List Component -->
      <OrderList
        :orders="filteredOrders"
        @new-order="openNewOrderModal"
        @view="viewOrderDetails"
        @edit="openEditOrder"
        @complete="updateOrderStatus($event, 'completed')"
        @cancel="cancelOrder"
      />

      <!-- Order Details Modal -->
      <OrderDetails v-if="isOrderDetailsOpen && selectedOrder" :open="isOrderDetailsOpen" :order="selectedOrder"
        @close="closeOrderDetails" @status-update="handleStatusUpdate" @paymentCompleted="handlePaymentCompleted" @edit-order="openEditOrder" @openCashRegister="handleOpenCashRegister" />

      <!-- New Order Modal - only mount when needed -->
      <NewOrderModal
        v-if="isNewOrderModalOpen"
        :open="isNewOrderModalOpen"
        :mode="newOrderMode"
        :order-to-edit="newOrderMode === 'edit' ? selectedOrderForEdit : null"
        :table-id="newOrderMode === 'create' ? undefined : (selectedOrderForEdit?.table_id ?? undefined)"
        @close="closeNewOrderModal"
        @order-created="handleNewOrder"
        @order-updated="handleOrderUpdated" />
    </div>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import MainLayout from '@/components/layout/MainLayout.vue';
import PageHeader from '@/components/layout/PageHeader.vue';
import OrderFilters from '@/components/orders/OrderFilters.vue';
import OrderList from '@/components/orders/OrderList.vue';
import OrderDetails from '@/components/orders/OrderDetailsModal.vue';
import NewOrderModal from '@/components/orders/NewOrderModal.vue';
import orderService from '@/services/orderService';
import type { Order } from '@/services/orderService';
import { PlusIcon } from '@heroicons/vue/24/outline';
import { useToast } from '@/composables/useToast';
import { useConfirm } from '@/composables/useConfirm';
import { useOrderFilters, type PaymentFilter, type OrderTypeFilter } from '@/composables/useOrderFilters';
import { 
  canCancelOrder as canCancelOrderHelper,
  transformOrderToLocal,
  type OrderWithLocalFields,
  type BackendOrderStatus,
  type OrderStatus
} from '@/utils/orderHelpers';

// i18n
const { t } = useI18n();
const route = useRoute();
const router = useRouter();

// Toasts
const { showSuccess, showError } = useToast();
const { confirm } = useConfirm();

// Open edit order flow from OrderDetails
async function openEditOrder(order: OrderWithLocalFields) {
  try {
    // Close details first
    isOrderDetailsOpen.value = false;
    newOrderMode.value = 'edit';
    // Fetch full order from API to provide complete data to the modal
    const fullOrder = await orderService.getOrder(order.id);
    selectedOrderForEdit.value = fullOrder;
    isNewOrderModalOpen.value = true;
  } catch (e) {
    console.error('Failed to open edit order modal:', e);
  }
}

// After an order is updated in the modal
function handleOrderUpdated(updated: any) {
  try {
    const idx = orders.value.findIndex(o => o.id === updated.id);
    if (idx !== -1) {
      // Merge fields; keep local computed fields where possible
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
    // Ensure full consistency by refetching
    fetchOrders(true);
    // Reset edit state
    selectedOrderForEdit.value = null;
    newOrderMode.value = 'create';
  } catch (e) {
    console.error('Failed updating local order after edit:', e);
  }
}

// showError now provided by toast composable

// Confirm helper using the global ConfirmationDialog
const confirmCancelOrder = async () => {
  return await confirm(
    t('app.views.orders.modals.confirm.cancel_title') as string,
    t('app.views.orders.modals.confirm.cancel_message') as string,
    t('app.views.orders.modals.confirm.confirm') as string,
    t('app.views.orders.modals.confirm.cancel') as string,
    'bg-red-600 hover:bg-red-700 focus:ring-red-500'
  );
};

// Types are now imported from orderHelpers

// State
// State
const loading = ref(false);
const error = ref<string | null>(null);
const selectedStatus = ref<OrderStatus>('all');
const selectedPaymentFilter = ref<PaymentFilter>('all');
const selectedOrderType = ref<OrderTypeFilter>('all');
const isNewOrderModalOpen = ref(false);
const newOrderMode = ref<'create' | 'edit'>('create');
const selectedOrderForEdit = ref<Order | null>(null);
const isOrderDetailsOpen = ref(false);
const hasAutoOpenedFromTable = ref(false);
const selectedOrder = ref<OrderWithLocalFields | null>(null);
const orders = ref<OrderWithLocalFields[]>([]);
const orderMenuStates = ref<Record<number, boolean>>({});

// Tab definitions
const tabs = [
  { id: 'all' as const, name: 'All', count: 0 },
  { id: 'pending' as const, name: 'Pending', count: 0 },
  { id: 'preparing' as const, name: 'Preparing', count: 0 },
  { id: 'ready' as const, name: 'Ready', count: 0 },
  { id: 'completed' as const, name: 'Completed', count: 0 },
  { id: 'cancelled' as const, name: 'Cancelled', count: 0 },
];

// Update tab counts when orders change
watch(orders, (newOrders) => {
  tabs.forEach(tab => {
    if (tab.id === 'all') {
      tab.count = newOrders.length;
    } else {
      tab.count = newOrders.filter(order => order.status === tab.id).length;
    }
  });
}, { immediate: true });

// Tab selection
const selectTab = (tabId: OrderStatus) => {
  selectedStatus.value = tabId;
};

// Format status for display (using i18n status keys when possible)
const formatStatus = (status: OrderStatus): string => {
  const key = `app.status.${status}`;
  const translated = t(key);
  return typeof translated === 'string' && translated.length > 0 ? translated : (statusMap[status] || status);
};


// Helper functions now imported from orderHelpers

// Map of status to display names
const statusMap: Record<OrderStatus, string> = {
  'all': 'All',
  'pending': 'Pending',
  'preparing': 'Preparing',
  'ready': 'Ready for Pickup',
  'completed': 'Completed',
  'cancelled': 'Cancelled'
};


// Use order filters composable
const { filteredOrders, getOrderCount } = useOrderFilters(
  orders,
  selectedStatus,
  selectedPaymentFilter,
  selectedOrderType
);

const viewOrderDetails = (order: OrderWithLocalFields) => {
  selectedOrder.value = { ...order };
  nextTick(() => {
    isOrderDetailsOpen.value = true;
  });
};

// Track cleanup timeout for proper cleanup on unmount
let closeDetailsTimeout: ReturnType<typeof setTimeout> | null = null;

function closeOrderDetails() {
  isOrderDetailsOpen.value = false;
  
  // Clear any existing timeout
  if (closeDetailsTimeout) {
    clearTimeout(closeDetailsTimeout);
  }
  
  // Wait for the transition to complete before clearing the selected order
  closeDetailsTimeout = setTimeout(() => {
    selectedOrder.value = null;
    closeDetailsTimeout = null;
  }, 300); // Match this with your transition duration (300ms)
}

function openNewOrderModal() {
  isNewOrderModalOpen.value = true;
}

function closeNewOrderModal() {
  isNewOrderModalOpen.value = false;
  // Reset mode back to create when closing
  newOrderMode.value = 'create';
}

const handleNewOrder = async (newOrder: Order) => {
  try {
    await fetchOrders();
    closeNewOrderModal();
  } catch (err) {
    console.error('Error processing new order:', err);
    // Only show error if we don't have an order ID
    if (!newOrder?.id) {
      showError(t('app.views.orders.messages.fetch_failed') as string);
    } else {
      // If we have an order ID, it was created successfully
      closeNewOrderModal();
    }
  }
};

const handleStatusUpdate = ({ orderId, status }: { orderId: number; status: OrderStatus }) => {
  if (status !== 'all') {
    updateOrderStatus(orderId, status as BackendOrderStatus);
    closeOrderDetails();
  }
};

const handlePaymentCompleted = async (updatedOrder: any) => {
  try {
    showSuccess(t('app.views.orders.messages.payment_completed_success', { id: updatedOrder.id }) as string);

    // Refresh the orders list
    await fetchOrders(true);

    // Emit event to refresh cash register if it's open
    window.dispatchEvent(new CustomEvent('orderPaymentCompleted', {
      detail: { orderId: updatedOrder.id }
    }));
  } catch (e) {
    console.error('Failed to update order after payment completion:', e);
  }
};

const handleOpenCashRegister = () => {
  // Navigate to cash register view
  router.push('/cash-register');
};

// Fetch orders from API
const fetchOrders = async (fetchAll = false) => {
  try {
    loading.value = true;
    error.value = null;

    // Fetch orders with the selected status filter
    const statusToFetch = selectedStatus.value === 'all' || fetchAll ? undefined : selectedStatus.value;
    const tableIdParam = route.query.table_id ? Number(route.query.table_id) : undefined;
    const response = await orderService.getActiveOrders(statusToFetch, tableIdParam);

    // The service should return an array, but we'll double-check here
    const ordersData = Array.isArray(response) ? response : [];

    // Transform using helper function
    const processedOrders = ordersData
      .map(order => transformOrderToLocal(order, t))
      .filter((order): order is OrderWithLocalFields => order !== null);

    orders.value = processedOrders;

    // If filtered by table_id and there is at least one order, auto-open it for quick edit/view
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

// Update order status
const updateOrderStatus = async (orderId: number, newStatus: BackendOrderStatus) => {
  try {
    // Update the order status in the backend
    await orderService.updateOrder(orderId, { status: newStatus });

    // Update the order status in the local state
    const orderIndex = orders.value.findIndex(o => o.id === orderId);
    if (orderIndex !== -1) {
      const updatedOrder = { ...orders.value[orderIndex], status: newStatus };
      orders.value.splice(orderIndex, 1, updatedOrder);
    }

    showSuccess(t('app.views.orders.messages.status_updated_success', { id: orderId, status: formatStatus(newStatus) }) as string);
  } catch (err) {
    console.error('Error updating order status:', err);
    showError(t('app.views.orders.messages.status_update_failed') as string);
  }
};

// Use canCancelOrder from orderHelpers
const canCancelOrder = canCancelOrderHelper;

// Cancel order
const cancelOrder = async (orderId: number) => {
  // Find the order to validate
  const order = orders.value.find(o => o.id === orderId);
  
  if (!order) {
    showError(t('app.views.orders.messages.order_not_found') as string);
    return;
  }
  
  // Validate if order can be cancelled
  if (!canCancelOrder(order)) {
    showError('No se puede cancelar una orden que ya está en preparación o lista. Solo se pueden cancelar órdenes pendientes con todos sus items pendientes.');
    return;
  }
  
  const confirmed = await confirmCancelOrder();

  if (!confirmed) return;

  try {
    await orderService.updateOrder(orderId, { status: 'cancelled' });

    // Update the order status in the local state
    const orderIndex = orders.value.findIndex(o => o.id === orderId);
    if (orderIndex !== -1) {
      const updatedOrder = {
        ...orders.value[orderIndex],
        status: 'cancelled' as const
      };
      orders.value.splice(orderIndex, 1, updatedOrder);
    }

    showSuccess(t('app.views.orders.messages.order_cancelled_success') as string);
  } catch (err) {
    console.error('Error cancelling order:', err);
    showError(t('app.views.orders.messages.cancel_failed') as string);
  }
};

// Initialize component
onMounted(() => {
  fetchOrders();
});

// Cleanup on unmount
onUnmounted(() => {
  if (closeDetailsTimeout) {
    clearTimeout(closeDetailsTimeout);
  }
});
</script>
