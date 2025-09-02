<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div>
        <h2 class="text-2xl font-bold text-gray-900">Orders</h2>
        <p class="mt-1 text-sm text-gray-500">Manage and track all orders</p>
      </div>
      <div class="flex items-center space-x-3">
        <div class="relative">
          <select 
            v-model="statusFilter" 
            class="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
          >
            <option value="">All Statuses</option>
            <option v-for="status in orderStatuses" :key="status" :value="status">
              {{ status }}
            </option>
          </select>
        </div>
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
                  {{ order.status }}
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
                  v-if="order.status === 'Preparing'"
                  type="button"
                  class="inline-flex items-center p-1.5 border border-transparent rounded-full shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                  @click="updateOrderStatus(order.id, 'Ready')"
                >
                  <CheckIcon class="h-4 w-4" aria-hidden="true" />
                </button>
                <button
                  v-if="order.status === 'Ready'"
                  type="button"
                  class="inline-flex items-center p-1.5 border border-transparent rounded-full shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                  @click="updateOrderStatus(order.id, 'Completed')"
                >
                  <CheckCircleIcon class="h-4 w-4" aria-hidden="true" />
                </button>
                <button
                  v-if="order.status !== 'Cancelled' && order.status !== 'Completed'"
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
    <OrderDetailsModal 
      :open="isOrderDetailsOpen" 
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
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
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
import { useConfirm } from '@/composables/useConfirm';
import { useToast } from '@/composables/useToast';

const { confirm } = useConfirm();
const { showSuccess, showError } = useToast();

// Mock data - replace with API calls
const orders = ref([
  {
    id: '1001',
    status: 'Preparing',
    customerName: 'John Doe',
    table: 'T-05',
    total: 24.50,
    createdAt: new Date(),
    items: [
      { name: 'Cappuccino', quantity: 2, price: 4.50 },
      { name: 'Croissant', quantity: 1, price: 3.50 }
    ]
  },
  // Add more mock orders as needed
]);

const orderStatuses = ['Pending', 'Preparing', 'Ready', 'Completed', 'Cancelled'];
const statusFilter = ref('');
const isOrderDetailsOpen = ref(false);
const selectedOrder = ref(null);
const isNewOrderModalOpen = ref(false);

const filteredOrders = computed(() => {
  if (!statusFilter.value) return orders.value;
  return orders.value.filter(order => order.status === statusFilter.value);
});

function getStatusBadgeClass(status) {
  const statusClasses = {
    'Pending': 'bg-yellow-100 text-yellow-800',
    'Preparing': 'bg-blue-100 text-blue-800',
    'Ready': 'bg-green-100 text-green-800',
    'Completed': 'bg-gray-100 text-gray-800',
    'Cancelled': 'bg-red-100 text-red-800',
  };
  return statusClasses[status] || 'bg-gray-100 text-gray-800';
}

function formatTime(date) {
  return new Date(date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function getOrderItemsSummary(items) {
  return items.map(item => `${item.quantity}x ${item.name}`).join(', ');
}

function viewOrderDetails(order) {
  selectedOrder.value = order;
  isOrderDetailsOpen.value = true;
}

function closeOrderDetails() {
  isOrderDetailsOpen.value = false;
  selectedOrder.value = null;
}

async function updateOrderStatus(orderId, newStatus) {
  try {
    // In a real app, you would call an API here
    const orderIndex = orders.value.findIndex(o => o.id === orderId);
    if (orderIndex !== -1) {
      orders.value[orderIndex].status = newStatus;
      showSuccess(`Order #${orderId} marked as ${newStatus}`);
    }
  } catch (error) {
    console.error('Error updating order status:', error);
    showError('Failed to update order status');
  }
}

async function cancelOrder(orderId) {
  const confirmed = await confirm({
    title: 'Cancel Order',
    message: 'Are you sure you want to cancel this order? This action cannot be undone.',
    confirmText: 'Yes, cancel order',
    cancelText: 'No, keep it',
    confirmClass: 'bg-red-600 hover:bg-red-700 focus:ring-red-500'
  });
  
  if (confirmed) {
    try {
      // In a real app, you would call an API here
      const orderIndex = orders.value.findIndex(o => o.id === orderId);
      if (orderIndex !== -1) {
        orders.value[orderIndex].status = 'Cancelled';
        showSuccess('Order has been cancelled');
      }
    } catch (error) {
      console.error('Error cancelling order:', error);
      showError('Failed to cancel order');
    }
  }
}

function openNewOrderModal() {
  isNewOrderModalOpen.value = true;
}

function closeNewOrderModal() {
  isNewOrderModalOpen.value = false;
}

function handleNewOrder(newOrder) {
  // In a real app, you would add the new order to the list from the API response
  orders.value.unshift({
    ...newOrder,
    id: Math.floor(1000 + Math.random() * 9000).toString(),
    createdAt: new Date(),
    status: 'Pending'
  });
  showSuccess('New order created successfully');
  closeNewOrderModal();
}

function handleStatusUpdate({ orderId, status }) {
  updateOrderStatus(orderId, status);
  closeOrderDetails();
}

// In a real app, you would fetch orders from an API
onMounted(() => {
  // fetchOrders();
});
</script>
