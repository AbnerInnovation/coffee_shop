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
      <!-- Status Tabs -->
      <div class="border-b border-gray-200 dark:border-gray-700 overflow-x-auto overflow-y-hidden -mx-3 sm:mx-0">
        <nav class="flex -mb-px" aria-label="Tabs">
          <div class="flex space-x-4 sm:space-x-8 px-3 sm:px-0 min-w-max">
            <button v-for="tab in tabs" :key="tab.id" @click="selectTab(tab.id)" :class="[
              'whitespace-nowrap border-b-2 py-3 sm:py-4 px-1 text-sm font-medium touch-manipulation',
              selectedStatus === tab.id
                ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400 dark:border-indigo-400'
                : 'border-transparent text-gray-500 dark:text-gray-400 hover:border-gray-300 dark:hover:border-gray-700 dark:hover:text-gray-100 hover:text-gray-700'
            ]">
              <span class="inline-flex items-center">
                {{ t('app.views.orders.tabs.' + tab.id) }}
                <span v-if="getOrderCount(tab.id) > 0" :class="[
                  selectedStatus === tab.id ? 'bg-indigo-100 text-indigo-600 dark:bg-indigo-900/30 dark:text-indigo-300' : 'bg-gray-100 text-gray-900 dark:bg-gray-700 dark:text-gray-300',
                  'ml-2 py-0.5 px-2 rounded-full text-xs font-medium'
                ]">
                  {{ getOrderCount(tab.id) }}
                </span>
              </span>
            </button>
          </div>
        </nav>
      </div>

      <!-- Additional Filters -->
      <div class="flex flex-col sm:flex-row gap-3 sm:gap-4">
        <!-- Payment Status Filter -->
        <div class="flex-1">
          <label for="payment-filter" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            {{ t('app.views.orders.filters.payment_status') || 'Estado de Pago' }}
          </label>
          <select
            id="payment-filter"
            v-model="selectedPaymentFilter"
            class="block w-full rounded-md border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white py-2 pl-3 pr-10 text-base focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"
          >
            <option value="all">{{ t('app.views.orders.filters.all_payments') || 'Todos' }}</option>
            <option value="paid">{{ t('app.views.orders.filters.paid') || 'Pagados' }}</option>
            <option value="unpaid">{{ t('app.views.orders.filters.unpaid') || 'No Pagados' }}</option>
          </select>
        </div>

        <!-- Order Type Filter -->
        <div class="flex-1">
          <label for="type-filter" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            {{ t('app.views.orders.filters.order_type') || 'Tipo de Orden' }}
          </label>
          <select
            id="type-filter"
            v-model="selectedOrderType"
            class="block w-full rounded-md border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white py-2 pl-3 pr-10 text-base focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"
          >
            <option value="all">{{ t('app.views.orders.filters.all_types') || 'Todos' }}</option>
            <option value="dine_in">{{ t('app.views.orders.filters.dine_in') || 'Comer Aquí' }}</option>
            <option value="takeaway">{{ t('app.views.orders.filters.takeaway') || 'Para Llevar' }}</option>
            <option value="delivery">{{ t('app.views.orders.filters.delivery') || 'A Domicilio' }}</option>
          </select>
        </div>
      </div>

      <!-- Order List -->
      <div class="bg-white dark:bg-gray-900 shadow overflow-hidden rounded-lg sm:rounded-md">
        <!-- Empty State -->
        <div v-if="filteredOrders.length === 0" class="text-center py-12 px-4">
          <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-gray-100">{{ t('app.views.orders.no_orders') }}</h3>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{{ t('app.views.orders.no_orders_description') }}</p>
          <div class="mt-6">
            <button type="button" @click="openNewOrderModal" class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
              <PlusIcon class="-ml-1 mr-2 h-5 w-5" aria-hidden="true" />
              {{ t('app.views.orders.new_order') }}
            </button>
          </div>
        </div>
        <ul v-else role="list" class="divide-y divide-gray-200 dark:divide-gray-700">
          <li v-for="order in filteredOrders" :key="order.id" :data-dropdown-container="`order-${order.id}`" class="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
            <div class="p-4 sm:p-6 border-b border-gray-100 dark:border-gray-700 relative">
              <!-- Three Dots Menu -->
              <div class="absolute top-4 right-4" @click.stop>
                <DropdownMenu
                  v-model="orderMenuStates[order.id]"
                  :id="`order-${order.id}`"
                  button-label="Order actions"
                  width="md"
                >
                  <!-- View Details -->
                  <DropdownMenuItem
                    :icon="EyeIcon"
                    variant="info"
                    @click="closeMenuAndExecute(order.id, () => viewOrderDetails(order))"
                  >
                    {{ t('app.views.orders.buttons.view') }}
                  </DropdownMenuItem>
                  
                  <!-- Edit Order (disabled if paid) -->
                  <DropdownMenuItem
                    v-if="order.status !== 'completed' && order.status !== 'cancelled' && !order.is_paid"
                    :icon="PencilIcon"
                    variant="default"
                    @click="closeMenuAndExecute(order.id, () => openEditOrder(order))"
                  >
                    {{ t('app.actions.edit') }}
                  </DropdownMenuItem>
                  
                  <!-- Status Actions (only complete for ready orders) -->
                  <DropdownMenuDivider v-if="order.status === 'ready' || canCancelOrder(order)" />
                  
                  <DropdownMenuItem
                    v-if="order.status === 'ready'"
                    :icon="CheckCircleIcon"
                    variant="success"
                    @click="closeMenuAndExecute(order.id, () => updateOrderStatus(order.id, 'completed'))"
                  >
                    {{ t('app.views.orders.buttons.complete') }}
                  </DropdownMenuItem>
                  
                  <DropdownMenuDivider v-if="order.status === 'ready' && canCancelOrder(order)" />
                  
                  <!-- Cancel Order -->
                  <DropdownMenuItem
                    v-if="canCancelOrder(order)"
                    :icon="XMarkIcon"
                    variant="danger"
                    @click="closeMenuAndExecute(order.id, () => cancelOrder(order.id))"
                  >
                    {{ t('app.views.orders.buttons.cancel') }}
                  </DropdownMenuItem>
                </DropdownMenu>
              </div>
              
              <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 sm:gap-0 pr-12">
                <div class="flex-1 min-w-0">
                  <!-- Status dropdown -->
                  <div class="flex items-center flex-wrap gap-2">
                    <p class="text-base sm:text-sm font-semibold text-indigo-600 dark:text-indigo-400">
                      #{{ order.id }}
                    </p>
                    <span class="inline-flex px-2.5 py-0.5 rounded-full text-xs font-medium"
                      :class="getStatusBadgeClass(order.status)">
                      {{ t('app.status.' + order.status) }}
                    </span>
                    <span
                      class="inline-flex px-2.5 py-0.5 rounded-full text-xs font-medium"
                      :class="order.is_paid ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-200' : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-200'"
                    >
                      {{ order.is_paid ? t('app.views.orders.payment.paid') : t('app.views.orders.payment.pending') }}
                    </span>
                    <span
                      class="inline-flex px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-200"
                      v-if="(order as any).order_type"
                    >
                      {{ getOrderTypeLabel((order as any).order_type) }}
                    </span>
                  </div>
                  <div class="mt-2 flex flex-wrap gap-x-4 gap-y-2">
                    <div class="flex items-center text-sm text-gray-500 dark:text-gray-400">
                      <RectangleGroupIcon class="flex-shrink-0 mr-1.5 h-4 w-4 text-gray-400 dark:text-gray-500"
                        aria-hidden="true" />
                      <span class="truncate">{{ order.table || t('app.views.orders.labels.takeaway') }}</span>
                    </div>
                    <div class="flex items-center text-sm text-gray-500 dark:text-gray-400">
                      <ClockIcon class="flex-shrink-0 mr-1.5 h-4 w-4 text-gray-400 dark:text-gray-500" aria-hidden="true" />
                      <span>{{ formatTime(order.createdAt) }}</span>
                    </div>
                  </div>
                </div>
                <div class="mt-3 sm:mt-0 sm:ml-4 flex-shrink-0 pr-2">
                  <p class="text-xl sm:text-lg font-semibold text-gray-900 dark:text-white">${{ order.total.toFixed(2) }}</p>
                </div>
              </div>

              <!-- Order Items Summary -->
              <div class="mt-3  pt-3">
                <div class="text-sm text-gray-500 flex flex-col sm:flex-row sm:items-center">
                  <span class="font-medium text-gray-900 dark:text-gray-100">{{ order.items.length }} {{
                    order.items.length === 1 ? t('app.views.orders.summary.item') : t('app.views.orders.summary.items')
                    }}</span>
                  <span class="hidden sm:inline mx-1">•</span>
                  <span class="truncate">{{ getOrderItemsSummary(order.items) }}</span>
                </div>
              </div>
            </div>
          </li>
        </ul>
      </div>

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
import orderService from '@/services/orderService';
import type { Order } from '@/services/orderService';
import {
  PlusIcon,
  EyeIcon,
  CheckIcon,
  XMarkIcon,
  UserIcon,
  RectangleGroupIcon,
  ClockIcon,
  ChevronDownIcon,
  CheckCircleIcon,
  PencilIcon
} from '@heroicons/vue/24/outline';
import OrderDetails from '@/components/orders/OrderDetailsModal.vue';
import NewOrderModal from '@/components/orders/NewOrderModal.vue';
import DropdownMenu from '@/components/ui/DropdownMenu.vue';
import DropdownMenuItem from '@/components/ui/DropdownMenuItem.vue';
import DropdownMenuDivider from '@/components/ui/DropdownMenuDivider.vue';
// Removed unused imports
import { useToast } from '@/composables/useToast';
import { useConfirm } from '@/composables/useConfirm';

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

// Local type for the view
interface Variant {
  id: number;
  name: string;
  price_adjustment: number;
}

interface MenuItem {
  id: number;
  name: string;
  price: number;
  description?: string;
  category?: string;
  image_url?: string;
  is_available: boolean;
  variants?: Variant[];
}

interface OrderItemLocal {
  id: number;
  menu_item_id: number;
  name: string;
  quantity: number;
  unit_price: number;
  total_price: number;
  notes?: string;
  variant_id?: number | null;
  variant_price_adjustment?: number | null;
  price?: number;
  status?: string;
  variant?: {
    id: number;
    name: string;
  } | null;
  variants?: Array<{
    id: number;
    name: string;
    price_adjustment: number;
  }>;
  menu_item?: {
    id: number;
    name: string;
    category?: string;
    price?: number;
  };
  special_instructions?: string;
}

interface OrderWithLocalFields {
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
  created_at?: string; // For compatibility
  customer_name?: string | null;
  table_number?: number | null;
  is_paid?: boolean;
}

// Define order status type that matches the backend
type BackendOrderStatus = 'pending' | 'preparing' | 'ready' | 'completed' | 'cancelled';
type OrderStatus = BackendOrderStatus | 'all';

// State
// State
const loading = ref(false);
const error = ref<string | null>(null);
const statusDropdownOpen = ref<number | null>(null);
const selectedStatus = ref<OrderStatus>('all');
const selectedPaymentFilter = ref<'all' | 'paid' | 'unpaid'>('all');
const selectedOrderType = ref<'all' | 'dine_in' | 'takeaway' | 'delivery'>('all');
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


// Status badge classes
const getStatusBadgeClass = (status: BackendOrderStatus): string => {
  const baseClasses = 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium';

  switch (status) {
    case 'pending':
      return `${baseClasses} bg-yellow-100 text-yellow-800`;
    case 'preparing':
      return `${baseClasses} bg-blue-100 text-blue-800`;
    case 'ready':
      return `${baseClasses} bg-green-100 text-green-800`;
    case 'completed':
      return `${baseClasses} bg-gray-100 text-gray-800`;
    case 'cancelled':
      return `${baseClasses} bg-red-100 text-red-800`;
    default:
      return `${baseClasses} bg-gray-100 text-gray-800`;
  }
};

// Map of status to display names
const statusMap: Record<OrderStatus, string> = {
  'all': 'All',
  'pending': 'Pending',
  'preparing': 'Preparing',
  'ready': 'Ready for Pickup',
  'completed': 'Completed',
  'cancelled': 'Cancelled'
};


const filteredOrders = computed<OrderWithLocalFields[]>(() => {
  let filtered = orders.value;
  
  // Filter by status
  if (selectedStatus.value !== 'all') {
    filtered = filtered.filter(order => order.status === selectedStatus.value);
  }
  
  // Filter by payment status
  if (selectedPaymentFilter.value === 'paid') {
    filtered = filtered.filter(order => order.is_paid === true);
  } else if (selectedPaymentFilter.value === 'unpaid') {
    filtered = filtered.filter(order => !order.is_paid);
  }
  
  // Filter by order type
  if (selectedOrderType.value !== 'all') {
    const typeMap: Record<string, string> = {
      'dine_in': 'dine_in',
      'takeaway': 'takeaway',
      'delivery': 'delivery'
    };
    const targetType = typeMap[selectedOrderType.value];
    filtered = filtered.filter(order => {
      const orderType = (order as any).order_type;
      return orderType === targetType;
    });
  }
  
  return filtered;
});

const getOrderCount = (status: OrderStatus): number => {
  if (!orders.value || !orders.value.length) return 0;
  if (status === 'all') return orders.value.length;
  return orders.value.filter(order => order.status === status).length;
};

const formatTime = (date: string | Date): string => {
  return new Date(date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

const getOrderItemsSummary = (items: OrderItemLocal[]): string => {
  if (!items || !Array.isArray(items)) return '';
  return items.map(item => {
    // Start with quantity and item name
    let itemText = `${item.quantity}x ${item.name}`;

    // Handle variant display and pricing
    const price = item.unit_price || 0;
    itemText += ` = $${(price * item.quantity).toFixed(2)}`;

    return itemText;
  }).join(', ');
};

const getOrderTypeLabel = (orderType: string): string => {
  const typeMap: Record<string, string> = {
    'dine_in': t('app.views.orders.filters.dine_in') as string,
    'takeaway': t('app.views.orders.filters.takeaway') as string,
    'delivery': t('app.views.orders.filters.delivery') as string
  };
  return typeMap[orderType] || orderType;
};

const isMounted = ref(true);

// Helper function to close menu and execute action
const closeMenuAndExecute = (orderId: number, action: () => void) => {
  orderMenuStates.value[orderId] = false;
  action();
};

const viewOrderDetails = (order: OrderWithLocalFields) => {
  if (!isMounted.value) return;
  selectedOrder.value = { ...order };
  nextTick(() => {
    isOrderDetailsOpen.value = true;
  });
};

function closeOrderDetails() {
  if (!isMounted.value) return;

  isOrderDetailsOpen.value = false;
  // Wait for the transition to complete before clearing the selected order
  const cleanup = setTimeout(() => {
    if (isMounted.value) {
      selectedOrder.value = null;
    }
  }, 300); // Match this with your transition duration (300ms)

  // Cleanup the timeout if the component unmounts
  onUnmounted(() => {
    clearTimeout(cleanup);
  });
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


// Close dropdown when clicking outside
const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement;
  if (!target.closest('.status-dropdown')) {
    statusDropdownOpen.value = null;
  }
};

// Toggle status dropdown
const toggleStatusDropdown = (orderId: number) => {
  statusDropdownOpen.value = statusDropdownOpen.value === orderId ? null : orderId;
};

// Close dropdown when clicking outside
onMounted(() => {
  isMounted.value = true;
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  isMounted.value = false;
  document.removeEventListener('click', handleClickOutside);
});

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

    // Transform the API response to match our local OrderWithLocalFields type
    const processedOrders = ordersData
      .map((order): OrderWithLocalFields | null => {
        if (!order) return null;

        const mappedItems = Array.isArray(order.items) ? order.items.map((item) => {

          // Get the variant if it exists
          const variant = item.variant;

          // Get the menu item name and variants
          const menuItemName = item.menu_item?.name || 'Unknown Item';
          const variantName = variant?.name;
          const itemName = variantName ? `${menuItemName} (${variantName})` : menuItemName;

          // Calculate price adjustment if variant exists
          const basePrice = item.menu_item?.price || 0;
          const variantPrice = variant?.price || 0;
          const priceAdjustment = variant ? variantPrice - basePrice : 0;

          const unitPrice = item.unit_price || 0;
          const quantity = item.quantity || 0;
          const total = unitPrice * quantity;

          return {
            id: item.id,
            menu_item_id: item.menu_item_id,
            name: itemName,
            variant_id: item.variant_id,
            quantity: quantity,
            price: unitPrice,
            unit_price: unitPrice,
            total_price: total,
            notes: item.special_instructions || undefined,
            variant: variant ? {
              id: variant.id,
              name: variant.name
            } : null,
            variants: variant ? [{
              id: variant.id,
              name: variant.name,
              price_adjustment: variant.price
            }] : [],
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
          // Add any additional required fields for OrderWithLocalFields
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

// Check if order can be cancelled
const canCancelOrder = (order: OrderWithLocalFields): boolean => {
  // Can only cancel if order status is pending
  if (order.status !== 'pending') {
    return false;
  }
  
  // If no items or items don't have status, allow cancellation (pending order with no preparation started)
  if (!order.items || order.items.length === 0) {
    return true;
  }
  
  // Can only cancel if ALL items are pending or don't have status (none started preparing)
  const allItemsPending = order.items.every(item => !item.status || item.status === 'pending');
  return allItemsPending;
};

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
</script>
