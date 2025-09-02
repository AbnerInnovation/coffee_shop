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
          <button 
            @click="fetchOrders"
            class="mt-2 text-sm font-medium text-red-700 hover:text-red-600 focus:outline-none"
          >
            Try again <span aria-hidden="true">&rarr;</span>
          </button>
        </div>
      </div>
    </div>

    <div v-else class="space-y-6">
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 class="text-2xl font-bold text-gray-900">Orders</h2>
          <p class="mt-1 text-sm text-gray-500">
            {{ selectedStatus === 'all' ? 'All' : formatStatus(selectedStatus) }} orders
          </p>
        </div>
        <div class="flex items-center space-x-3">
          <button
            type="button"
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            @click="openNewOrderModal"
          >
            <PlusIcon class="-ml-1 mr-2 h-5 w-5" aria-hidden="true" />
            New Order
          </button>
        </div>
      </div>
      <!-- Status Tabs -->
      <div class="border-b border-gray-200">
        <nav class="-mb-px flex space-x-8" aria-label="Tabs">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="selectTab(tab.id)"
            :class="[
              'flex-1 whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium',
              selectedStatus === tab.id 
                ? 'border-indigo-500 text-indigo-600' 
                : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
            ]"
          >
            {{ tab.name }}
            <span 
              v-if="getOrderCount(tab.id) > 0"
              :class="[
                selectedStatus === tab.id ? 'bg-indigo-100 text-indigo-600' : 'bg-gray-100 text-gray-900',
                'ml-2 py-0.5 px-2 rounded-full text-xs font-medium'
              ]"
            >
              {{ getOrderCount(tab.id) }}
            </span>
          </button>
        </nav>
      </div>

      <!-- Order List -->
      <div class="bg-white shadow overflow-hidden sm:rounded-md">
        <ul role="list" class="divide-y divide-gray-200">
          <li v-for="order in filteredOrders" :key="order.id" class="px-4 py-4 sm:px-6 hover:bg-gray-50">
            <div class="flex items-center justify-between">
              <div class="flex-1 min-w-0">
                <div class="flex items-center">
                  <p class="text-sm font-medium text-indigo-600 truncate">
                    Order #{{ order.id }}
                  </p>
                  <span 
                    class="ml-2 px-2.5 py-0.5 rounded-full text-xs font-medium"
                    :class="getStatusBadgeClass(order.status)"
                  >
                    {{ formatStatus(order.status) }}
                  </span>
                </div>
                <div class="mt-1 flex flex-col sm:flex-row sm:flex-wrap sm:mt-0 sm:space-x-6">
                  <div class="mt-2 flex items-center text-sm text-gray-500">
                    <UserIcon class="flex-shrink-0 mr-1.5 h-5 w-5 text-gray-400" aria-hidden="true" />
                    {{ order.customerName || 'Walk-in' }}
                  </div>
                  <div class="mt-2 flex items-center text-sm text-gray-500">
                    <RectangleGroupIcon class="flex-shrink-0 mr-1.5 h-5 w-5 text-gray-400" aria-hidden="true" />
                    {{ order.table || 'Takeaway' }}
                  </div>
                  <div class="mt-2 flex items-center text-sm text-gray-500">
                    <ClockIcon class="flex-shrink-0 mr-1.5 h-5 w-5 text-gray-400" aria-hidden="true" />
                    {{ formatTime(order.createdAt) }}
                  </div>
                </div>
              </div>
              <div class="ml-4 flex-shrink-0">
                <p class="text-lg font-medium text-gray-900">${{ order.total.toFixed(2) }}</p>
                <div class="mt-2 flex space-x-2">
                  <button
                    type="button"
                    class="inline-flex items-center p-1.5 border border-transparent rounded-full shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                    @click="viewOrderDetails(order)"
                  >
                    <EyeIcon class="h-4 w-4" aria-hidden="true" />
                  </button>
                  <button
                    v-if="order.status === 'preparing'"
                    type="button"
                    class="inline-flex items-center p-1.5 border border-transparent rounded-full shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                    @click="updateOrderStatus(order.id, 'ready' as const)"
                  >
                    <CheckIcon class="h-4 w-4" aria-hidden="true" />
                  </button>
                  <button
                    v-if="order.status === 'ready'"
                    type="button"
                    class="inline-flex items-center p-1.5 border border-transparent rounded-full shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                    @click="updateOrderStatus(order.id, 'completed' as const)"
                  >
                    <CheckCircleIcon class="h-4 w-4" aria-hidden="true" />
                  </button>
                  <button
                    v-if="order.status !== 'cancelled' && order.status !== 'completed'"
                    type="button"
                    class="inline-flex items-center p-1.5 border border-transparent rounded-full shadow-sm text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                    @click="cancelOrder(order.id)"
                  >
                    <XMarkIcon class="h-4 w-4" aria-hidden="true" />
                  </button>
                </div>
              </div>
            </div>
            
            <!-- Order Items Summary -->
            <div class="mt-4 border-t border-gray-100 pt-3">
              <div class="text-sm text-gray-500">
                <span class="font-medium text-gray-900">{{ order.items.length }} items</span>
                <span class="mx-1">•</span>
                <span>{{ getOrderItemsSummary(order.items) }}</span>
              </div>
            </div>
          </li>
        </ul>
      </div>

      <!-- Order Details Modal -->
      <OrderDetails 
        v-if="selectedOrder" 
        :order="selectedOrder" 
        @close="closeOrderDetails"
        @status-update="handleStatusUpdate"
      />
      
      <!-- New Order Modal -->
      <NewOrderModal 
        :open="isNewOrderModalOpen" 
        @close="closeNewOrderModal"
        @order-created="handleNewOrder"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, type Ref } from 'vue';
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
  CheckCircleIcon 
} from '@heroicons/vue/24/outline';
import OrderDetailsModal from '@/components/orders/OrderDetailsModal.vue';
import NewOrderModal from '@/components/orders/NewOrderModal.vue';
// Removed unused imports

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
interface MenuItem {
  id: number;
  name: string;
  price: number;
  description?: string;
  category?: string;
  image_url?: string;
  is_available: boolean;
}

interface OrderItemLocal {
  id: number;
  name: string;
  price: number;
  quantity: number;
  special_instructions?: string;
  menu_item?: MenuItem;
}

interface OrderWithLocalFields {
  id: number;
  status: BackendOrderStatus;
  customerName: string;
  table: string;
  total: number;
  createdAt: Date;
  updated_at: string;
  total_amount: number;
  table_id: number;
  notes?: string;
  items: OrderItemLocal[];
  created_at: string; // For compatibility
}

const orders = ref<OrderWithLocalFields[]>([]);

// Define order status type that matches the backend
type BackendOrderStatus = 'pending' | 'preparing' | 'ready' | 'completed' | 'cancelled';
type OrderStatus = BackendOrderStatus | 'all';

// Map of status to display names
const statusMap: Record<OrderStatus, string> = {
  'all': 'All',
  'pending': 'Pending',
  'preparing': 'Preparing',
  'ready': 'Ready',
  'completed': 'Completed',
  'cancelled': 'Cancelled'
} as const;

const orderStatuses = Object.keys(statusMap).filter(k => k !== 'all') as BackendOrderStatus[];
const isOrderDetailsOpen = ref(false);
const selectedOrder = ref<OrderWithLocalFields | null>(null);
const isNewOrderModalOpen = ref(false);

const filteredOrders = computed<OrderWithLocalFields[]>(() => {
  if (selectedStatus.value === 'all') return orders.value;
  return orders.value.filter(order => order.status === selectedStatus.value);
});

const getOrderCount = (status: OrderStatus): number => {
  if (!orders.value || !orders.value.length) return 0;
  if (status === 'all') return orders.value.length;
  return orders.value.filter(order => order.status === status).length;
};


// Tab definitions with proper status types
const tabs = [
  { id: 'all', name: 'All' },
  { id: 'pending', name: 'Pending' },
  { id: 'preparing', name: 'Preparing' },
  { id: 'ready', name: 'Ready' },
  { id: 'completed', name: 'Completed' },
  { id: 'cancelled', name: 'Cancelled' }
] as const;
const selectedStatus = ref<OrderStatus>('all');

const selectTab = (tabId: OrderStatus) => {
  selectedStatus.value = tabId;
  fetchOrders();
};

const getStatusBadgeClass = (status: BackendOrderStatus) => {
  const statusClasses: Record<BackendOrderStatus, string> = {
    'pending': 'bg-yellow-100 text-yellow-800',
    'preparing': 'bg-blue-100 text-blue-800',
    'ready': 'bg-green-100 text-green-800',
    'completed': 'bg-purple-100 text-purple-800',
    'cancelled': 'bg-red-100 text-red-800'
  };
  return statusClasses[status] || 'bg-gray-100 text-gray-800';
};

// Format status for display
const formatStatus = (status: OrderStatus): string => {
  if (!status || status === 'all') return 'All';
  const displayMap: Record<BackendOrderStatus, string> = {
    'pending': 'Pending',
    'preparing': 'Preparing',
    'ready': 'Ready',
    'completed': 'Completed',
    'cancelled': 'Cancelled'
  };
  return displayMap[status as BackendOrderStatus] || status;
};

const formatTime = (date: string | Date): string => {
  return new Date(date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

const getOrderItemsSummary = (items: OrderItemLocal[]): string => {
  if (!items || !Array.isArray(items)) return '';
  return items.map(item => `${item.quantity}x ${item.name}`).join(', ');
};

const viewOrderDetails = (order: OrderWithLocalFields) => {
  selectedOrder.value = order;
  isOrderDetailsOpen.value = true;
};

function closeOrderDetails() {
  isOrderDetailsOpen.value = false;
  selectedOrder.value = null;
  console.log('Order details closed');
}

function openNewOrderModal() {
  isNewOrderModalOpen.value = true;
}

function closeNewOrderModal() {
  isNewOrderModalOpen.value = false;
}

const handleNewOrder = async (newOrder: Order) => {
  try {
    const createdOrder = await orderService.createOrder({
      table_id: newOrder.table_id,
      items: (newOrder.items || []).map(item => ({
        menu_item_id: item.menu_item_id,
        quantity: item.quantity,
        special_instructions: item.special_instructions
      })),
      notes: newOrder.notes
    });
    const localOrder: OrderWithLocalFields = {
      ...createdOrder,
      customerName: createdOrder.customer_name || 'Walk-in',
      table: createdOrder.table_number ? `Table ${createdOrder.table_number}` : 'Takeaway',
      total: createdOrder.total_amount,
      createdAt: new Date(createdOrder.created_at),
      items: (createdOrder.items || []).map(item => ({
        id: item.id,
        name: item.menu_item?.name || 'Unknown Item',
        price: item.menu_item?.price || 0,
        quantity: item.quantity,
        special_instructions: item.special_instructions,
        menu_item: item.menu_item
      }))
    };
    orders.value = [localOrder, ...orders.value];
    showSuccess('Order created successfully');
    closeNewOrderModal();
  } catch (err) {
    console.error('Error creating new order:', err);
    showError('Failed to create new order. Please try again.');
  }
};

const handleStatusUpdate = ({ orderId, status }: { orderId: number; status: OrderStatus }) => {
  if (status !== 'all') {
    updateOrderStatus(orderId, status as BackendOrderStatus);
    closeOrderDetails();
  }
};

const loading = ref(false);
const error = ref<string | null>(null) as Ref<string | null>;

// Fetch orders from API
const fetchOrders = async () => {
  try {
    loading.value = true;
    error.value = null;
    
    // Fetch orders with the selected status filter
    const statusToFetch = selectedStatus.value === 'all' ? undefined : selectedStatus.value;
    const response = await orderService.getActiveOrders(statusToFetch);
    
    // The service should return an array, but we'll double-check here
    const ordersData = Array.isArray(response) ? response : [];
    
    // Transform the API response to match our local OrderWithLocalFields type
    orders.value = ordersData.map((order) => {
      if (!order) return null;
      
      return {
        ...order,
        customerName: order.customer_name || 'Walk-in',
        table: order.table_number ? `Table ${order.table_number}` : 'Takeaway',
        total: order.total_amount || 0,
        createdAt: new Date(order.created_at || new Date()),
        items: Array.isArray(order.items) ? order.items.map(item => ({
          id: item.id || 0,
          name: item.menu_item?.name || 'Unknown Item',
          price: item.menu_item?.price || 0,
          quantity: item.quantity || 0,
          special_instructions: item.special_instructions,
          menu_item: item.menu_item
        })) : []
      };
    }).filter(Boolean) as OrderWithLocalFields[];
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
    await orderService.updateOrderStatus(orderId, newStatus);
    
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
    await orderService.updateOrderStatus(orderId, 'cancelled');
    
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
