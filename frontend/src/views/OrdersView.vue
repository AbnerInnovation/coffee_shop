<template>
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
          <button @click="fetchOrders"
            class="mt-2 text-sm font-medium text-red-700 hover:text-red-600 focus:outline-none">
            {{ t('app.views.orders.try_again') }} <span aria-hidden="true">&rarr;</span>
          </button>
        </div>
      </div>
    </div>

    <div v-else class="space-y-6">
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 class="text-2xl font-bold text-gray-900">{{ t('app.views.orders.title') }}</h2>
          <p class="mt-1 text-sm text-gray-500">
            {{ selectedStatus === 'all' ? t('app.views.orders.tabs.all') : t('app.status.' + selectedStatus) }} {{
              t('app.views.orders.title').toLowerCase() }}
          </p>
        </div>
        <div class="flex items-center space-x-3">
          <button type="button"
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            @click="openNewOrderModal">
            <PlusIcon class="-ml-1 mr-2 h-5 w-5" aria-hidden="true" />
            {{ t('app.views.orders.new_order') }}
          </button>
        </div>
      </div>
      <!-- Status Tabs -->
      <div class="border-b border-gray-200 dark:border-gray-700 overflow-x-auto overflow-y-hidden">
        <nav class="flex -mb-px min-w-max" aria-label="Tabs">
          <div class="flex space-x-8 px-2 sm:px-0">
            <button v-for="tab in tabs" :key="tab.id" @click="selectTab(tab.id)" :class="[
              'whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium',
              selectedStatus === tab.id
                ? 'border-indigo-500 text-indigo-600'
                : 'border-transparent text-gray-500 hover:border-gray-300 dark:hover:border-gray-700 dark:hover:text-gray-100 hover:text-gray-700'
            ]">
              <span class="inline-flex items-center">
                {{ t('app.views.orders.tabs.' + tab.id) }}
                <span v-if="getOrderCount(tab.id) > 0" :class="[
                  selectedStatus === tab.id ? 'bg-indigo-100 text-indigo-600' : 'bg-gray-100 text-gray-900',
                  'ml-2 py-0.5 px-2 rounded-full text-xs font-medium'
                ]">
                  {{ getOrderCount(tab.id) }}
                </span>
              </span>
            </button>
          </div>
        </nav>
      </div>

      <!-- Order List -->
      <div class="bg-white shadow overflow-hidden sm:rounded-md">
        <ul role="list" class="divide-y divide-gray-200">
          <li v-for="order in filteredOrders" :key="order.id" class=" hover:bg-gray-50 dark:bg-gray-900 border-none">
            <div class="p-6 border-b border-gray-100 dark:border-gray-700">
              <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
                <div class="flex-1 min-w-0">
                  <!-- Status dropdown -->
                  <div class="flex items-center mt-2 sm:mt-0">
                    <p class="text-sm font-medium text-indigo-600 truncate">
                      #{{ order.id }}
                    </p>
                    <span class="hidden sm:inline-flex ml-2 px-2.5 py-0.5 rounded-full text-xs font-medium"
                      :class="getStatusBadgeClass(order.status)">
                      {{ t('app.status.' + order.status) }}
                    </span>
                  </div>
                  <div class="mt-2 grid grid-cols-2 gap-x-4 gap-y-2 sm:flex sm:flex-wrap sm:space-x-6">
                    <div class="flex items-center text-sm text-gray-500">
                      <RectangleGroupIcon class="flex-shrink-0 mr-1.5 h-4 w-4 sm:h-5 sm:w-5 text-gray-400"
                        aria-hidden="true" />
                      <span class="truncate">{{ order.table || t('app.views.orders.labels.takeaway') }}</span>
                    </div>
                    <div class="col-span-2 sm:col-auto flex items-center text-sm text-gray-500">
                      <ClockIcon class="flex-shrink-0 mr-1.5 h-4 w-4 sm:h-5 sm:w-5 text-gray-400" aria-hidden="true" />
                      <span>{{ formatTime(order.createdAt) }}</span>
                    </div>
                  </div>
                </div>
                <div class="mt-4 sm:mt-0 sm:ml-4 flex-shrink-0 flex items-center justify-between w-full sm:w-auto">
                  <p class="text-lg font-medium text-gray-900">${{ order.total.toFixed(2) }}</p>
                  <div class="ml-4 flex space-x-1 sm:space-x-2">
                    <button type="button"
                      class="inline-flex items-center p-2 sm:p-1.5 border border-transparent rounded-full shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                      @click="viewOrderDetails(order)" aria-label="View order details">
                      <EyeIcon class="h-4 w-4" aria-hidden="true" />
                      <span class="sr-only sm:not-sr-only ml-1 text-xs">{{ t('app.views.orders.buttons.view') }}</span>
                    </button>
                    <button v-if="order.status === 'preparing'" type="button"
                      class="inline-flex items-center p-2 sm:p-1.5 border border-transparent rounded-full shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                      @click="updateOrderStatus(order.id, 'ready' as const)" aria-label="Mark as ready">
                      <CheckIcon class="h-4 w-4" aria-hidden="true" />
                      <span class="sr-only sm:not-sr-only ml-1 text-xs">{{ t('app.views.orders.buttons.ready') }}</span>
                    </button>
                    <button v-if="order.status === 'ready'" type="button"
                      class="inline-flex items-center p-2 sm:p-1.5 border border-transparent rounded-full shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                      @click="updateOrderStatus(order.id, 'completed' as const)" aria-label="Mark as completed">
                      <CheckCircleIcon class="h-4 w-4" aria-hidden="true" />
                      <span class="sr-only sm:not-sr-only ml-1 text-xs">{{ t('app.views.orders.buttons.complete')
                        }}</span>
                    </button>
                    <button v-if="order.status !== 'cancelled' && order.status !== 'completed'" type="button"
                      class="inline-flex items-center p-2 sm:p-1.5 border border-transparent rounded-full shadow-sm text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                      @click="cancelOrder(order.id)" aria-label="Cancel order">
                      <XMarkIcon class="h-4 w-4" aria-hidden="true" />
                      <span class="sr-only sm:not-sr-only ml-1 text-xs">{{ t('app.views.orders.buttons.cancel')
                        }}</span>
                    </button>
                  </div>
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
        @close="closeOrderDetails" @status-update="handleStatusUpdate" />

      <!-- New Order Modal -->
      <NewOrderModal :open="isNewOrderModalOpen" @close="closeNewOrderModal" @order-created="handleNewOrder" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue';
import { useI18n } from 'vue-i18n';
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
  CheckCircleIcon
} from '@heroicons/vue/24/outline';
import OrderDetails from '@/components/orders/OrderDetailsModal.vue';
import NewOrderModal from '@/components/orders/NewOrderModal.vue';
// Removed unused imports

// i18n
const { t } = useI18n();

// Simple toast functions since we're not using PrimeVue
const showSuccess = (message: string) => {
  console.log('Success:', message);
  // You can replace this with your preferred toast implementation
  alert(`Success: ${message}`);
};

const showError = (message: string) => {
  console.error('Error:', message);
  // You can replace this with your preferred error toast implementation
  alert(`Error: ${message}`);
};

// Simple confirm function
const confirm = async (options: { title?: string; message: string; confirmText?: string; cancelText?: string }) => {
  // You can replace this with your preferred confirm dialog implementation
  return window.confirm(options.message);
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
  variants?: Array<{
    id: number;
    name: string;
    price_adjustment: number;
  }>;
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
const isNewOrderModalOpen = ref(false);
const isOrderDetailsOpen = ref(false);
const selectedOrder = ref<OrderWithLocalFields | null>(null);
const orders = ref<OrderWithLocalFields[]>([]);

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
  if (selectedStatus.value === 'all') return orders.value;
  return orders.value.filter(order => order.status === selectedStatus.value);
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

const isMounted = ref(true);

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

  console.log('Order details closed');
}

function openNewOrderModal() {
  console.log('Opening new order modal');
  isNewOrderModalOpen.value = true;
  console.log('isNewOrderModalOpen after open:', isNewOrderModalOpen.value);
}

function closeNewOrderModal() {
  console.log('Closing new order modal');
  isNewOrderModalOpen.value = false;
  console.log('isNewOrderModalOpen after close:', isNewOrderModalOpen.value);
}

const handleNewOrder = async (newOrder: Order) => {
  try {
    console.log('New order received:', newOrder);

    // Create a properly typed order object
    const localOrder: OrderWithLocalFields = {
      id: newOrder.id,
      status: newOrder.status as BackendOrderStatus,
      customerName: newOrder.customer_name || (newOrder.table_number ? 'Table ' + newOrder.table_number : 'Takeaway'),
      table: newOrder.table_number ? `Table ${newOrder.table_number}` : (newOrder.customer_name ? 'Takeaway' : 'Dine-in'),
      total: newOrder.total_amount || 0,
      createdAt: newOrder.created_at ? new Date(newOrder.created_at) : new Date(),
      updated_at: newOrder.updated_at || new Date().toISOString(),
      items: (newOrder.items || []).map(item => {
        // Safely find the variant if it exists
        let variant: Variant | undefined;
        if (item.variant_id && Array.isArray(item.menu_item?.variants)) {
          variant = item.menu_item?.variants.find((v: Variant) => v.id === item.variant_id);
        }

        const unitPrice = item.unit_price || item.menu_item?.price || 0;
        const quantity = item.quantity || 0;

        const orderItem: OrderItemLocal = {
          id: item.id || 0,
          menu_item_id: item.menu_item_id,
          name: item.menu_item?.name || 'Unknown Item',
          quantity: quantity,
          unit_price: unitPrice,
          total_price: unitPrice * quantity,
          variant_id: item.variant_id || undefined,
          variant_price_adjustment: variant?.price_adjustment
        };

        console.log('Processed order item:', orderItem);

        // Only add notes if they exist
        if (item.special_instructions) {
          orderItem.notes = item.special_instructions;
        }

        return orderItem;
      }),
      // Copy over any additional fields from the new order
      ...(newOrder.table_id !== undefined && { table_id: newOrder.table_id }),
      ...(newOrder.customer_name !== undefined && { customer_name: newOrder.customer_name }),
      ...(newOrder.notes !== undefined && { notes: newOrder.notes }),
      ...(newOrder.table_number !== undefined && { table_number: newOrder.table_number })
    };

    console.log('Processed order for display:', localOrder);

    // Add the new order to the beginning of the list
    orders.value = [localOrder, ...orders.value];
    showSuccess('Order created successfully');
    closeNewOrderModal();
  } catch (err) {
    console.error('Error processing new order:', err);
    // Only show error if we don't have an order ID
    if (!newOrder?.id) {
      showError('Failed to create new order. Please try again.');
    } else {
      // If we have an order ID, it was created successfully
      showSuccess('Order created successfully');
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
const fetchOrders = async () => {
  try {
    loading.value = true;
    error.value = null;

    // Fetch orders with the selected status filter
    const statusToFetch = selectedStatus.value === 'all' ? undefined : selectedStatus.value;
    console.log('Fetching orders with status:', statusToFetch);
    const response = await orderService.getActiveOrders(statusToFetch);
    console.log('API Response:', JSON.stringify(response, null, 2));

    // The service should return an array, but we'll double-check here
    const ordersData = Array.isArray(response) ? response : [];
    console.log('Processed orders data:', JSON.stringify(ordersData, null, 2));

    // Transform the API response to match our local OrderWithLocalFields type
    const processedOrders = ordersData
      .map((order): OrderWithLocalFields | null => {
        if (!order) return null;

        console.log('Processing order:', order.id);

        const mappedItems = Array.isArray(order.items) ? order.items.map((item) => {
          console.log('Processing order item:', {
            id: item.id,
            menu_item_id: item.menu_item_id,
            variant_id: item.variant_id,
            menu_item: item.menu_item
          });

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
            variants: variant ? [{
              id: variant.id,
              name: variant.name,
              price_adjustment: variant.price
            }] : []
          };
        }) : [];

        return {
          ...order,
          customerName: order.customer_name || 'Walk-in',
          table: order.table_number ? `Table ${order.table_number}` : 'Takeaway',
          total: order.total_amount || 0,
          createdAt: new Date(order.created_at || new Date()),
          items: mappedItems,
          // Add any additional required fields for OrderWithLocalFields
          status: order.status as BackendOrderStatus,
          table_number: order.table_number,
          customer_name: order.customer_name,
          notes: order.notes,
          updated_at: order.updated_at
        };
      })
      .filter((order): order is OrderWithLocalFields => order !== null);

    orders.value = processedOrders;
  } catch (err) {
    console.error('Error fetching orders:', err);
    error.value = 'Failed to fetch orders. Please try again.';
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

    showSuccess(`Order #${orderId} status updated to ${formatStatus(newStatus)}`);
  } catch (err) {
    console.error('Error updating order status:', err);
    showError('Failed to update order status. Please try again.');
  }
};

// Cancel order
const cancelOrder = async (orderId: number) => {
  const confirmed = await confirm({
    message: 'Are you sure you want to cancel this order?',
    confirmText: 'Yes, cancel order',
    cancelText: 'No, keep it'
  });

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

    showSuccess('Order has been cancelled');
  } catch (err) {
    console.error('Error cancelling order:', err);
    showError('Failed to cancel order. Please try again.');
  }
};

// Initialize component
onMounted(() => {
  fetchOrders();
});
</script>
