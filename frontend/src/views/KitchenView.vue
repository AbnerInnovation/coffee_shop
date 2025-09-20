<template>
  <div class="kitchen-view p-4">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold text-gray-900">{{ t('app.views.kitchen.title') }}</h1>
      <div class="text-sm text-gray-500">
        {{ t('app.views.kitchen.last_updated', { time: new Date().toLocaleTimeString() }) }}
      </div>
    </div>

    <div v-if="loading" class="flex justify-center items-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
    </div>

    <div v-else>
      <div v-if="activeOrders.length === 0" class="text-center py-12">
        <p class="text-gray-500 text-lg">{{ t('app.views.kitchen.no_active') }}</p>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-for="order in activeOrders" :key="order.id" class="bg-white dark:bg-gray-900 dark:border-gray-800 border-gray-200 border-2 rounded-lg shadow overflow-hidden">
          <div class="p-4 border-b border-gray-200 dark:border-gray-600">
            <div class="flex justify-between items-start">
              <div>
                <h3 class="text-lg font-semibold">{{ t('app.views.kitchen.order', { id: order.id }) }}</h3>
                <p class="text-sm text-gray-500">
                  {{ formatTime(order.created_at) }}
                  <span v-if="order.table_number" class="ml-2">• {{ t('app.views.kitchen.table', { number: order.table_number }) }}</span>
                </p>
              </div>
              <span 
                class="px-2 py-1 text-xs font-medium rounded-full"
                :class="getStatusBadgeClass(order.status)"
              >
                {{ t(`app.status.${order.status}`) }}
              </span>
            </div>
            <div v-if="order.notes" class="mt-2 p-2 bg-yellow-50 text-sm text-yellow-700 rounded">
              {{ order.notes }}
            </div>
          </div>

          <div class="divide-y divide-gray-200">
            <div 
              v-for="item in order.items" 
              :key="item.id"
              class="p-4 hover:bg-gray-50 dark:hover:bg-gray-900"
              :class="{ 'bg-green-50 dark:bg-green-700': item.status === 'completed' }"
            >
              <div class="flex justify-between items-start">
                <div class="flex-1">
                  <div class="flex items-center">
                    <span class="font-medium text-lg mr-2">{{ item.quantity }}x</span>
                    <span class="text-lg">{{ item.menu_item.name }}</span>
                    <span v-if="item.variant" class="text-lg ml-2">({{ item.variant.name }})</span>
                    
                  </div>
                  
                  <div v-if="item.special_instructions" class="ml-7 mt-1 text-sm text-gray-600 dark:text-gray-400">
                    <div>
                      <span class="font-medium">{{ t('app.views.kitchen.note') }}</span> {{ item.special_instructions }}
                    </div>
                  </div>
                </div>
                
                <div class="flex items-center">
                  <span class="text-gray-500 dark:text-gray-400">
                    {{ getTimeElapsed(item.created_at) }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div class="p-4 bg-gray-50 dark:bg-gray-900 border-t border-gray-200">
            <button
              v-if="order.status === 'preparing'"
              @click="markOrderReady(order)"
              class="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            >
              {{ t('app.views.kitchen.actions.order_ready') }}
            </button>
            <button
              v-else-if="order.status === 'pending'"
              @click="startPreparingOrder(order)"
              class="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              {{ t('app.views.kitchen.actions.start_preparing') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { useI18n } from 'vue-i18n';
import orderService from '@/services/orderService';
import type { Order, OrderItem } from '@/services/orderService';

const loading = ref(true);
const activeOrders = ref<Order[]>([]);
let refreshInterval: number | null = null;

const { t } = useI18n();

// Format time for display
const formatTime = (dateString: string) => {
  return new Date(dateString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

// Format status for display
const formatStatus = (status: string) => {
  return t(`app.status.${status}`) as string;
};

// Get status badge class
const getStatusBadgeClass = (status: string) => {
  const classes = {
    'pending': 'bg-yellow-100 text-yellow-800',
    'preparing': 'bg-blue-100 text-blue-800',
    'ready': 'bg-green-100 text-green-800',
    'completed': 'bg-gray-100 text-gray-800',
    'cancelled': 'bg-red-100 text-red-800'
  };
  return classes[status as keyof typeof classes] || 'bg-gray-100 text-gray-800';
};

// Calculate time elapsed since item was started
const getTimeElapsed = (startedAt: string) => {
  if (!startedAt) return '';
  const start = new Date(startedAt).getTime();
  const now = new Date().getTime();
  const diffInMinutes = Math.floor((now - start) / (1000 * 60));
  if (diffInMinutes < 1) return t('app.views.kitchen.time.just_now') as string;
  if (diffInMinutes < 60) return t('app.views.kitchen.time.minutes_ago', { m: diffInMinutes }) as string;
  const hours = Math.floor(diffInMinutes / 60);
  const minutes = diffInMinutes % 60;
  return t('app.views.kitchen.time.hours_minutes_ago', { h: hours, m: minutes }) as string;
};

// Fetch active orders (pending or preparing)
const fetchActiveOrders = async () => {
  try {
    loading.value = true;
    const pendingOrders = await orderService.getActiveOrders('pending');
    const preparingOrders = await orderService.getActiveOrders('preparing');
    
    // Combine and sort by creation time (newest first)
    const allOrders = [...pendingOrders, ...preparingOrders].sort((a, b) => 
      new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    );
    
    // Initialize item statuses if not set
    activeOrders.value = allOrders.map(order => ({
      ...order,
      items: order.items.map(item => ({
        ...item,
        status: item.status || 'pending',
        started_at: item.started_at || order.created_at
      }))
    }));
  } catch (error) {
    console.error('Error fetching active orders:', error);
  } finally {
    loading.value = false;
  }
};

// Mark item as complete
const markItemComplete = async (item: OrderItem, order: Order) => {
  try {
    // Update local state immediately for better UX
    const orderIndex = activeOrders.value.findIndex(o => o.id === order.id);
    if (orderIndex !== -1) {
      const itemIndex = activeOrders.value[orderIndex].items.findIndex(i => i.id === item.id);
      if (itemIndex !== -1) {
        activeOrders.value[orderIndex].items[itemIndex].status = 'completed';
        
        // Update the order status if all items are completed
        const allItemsCompleted = activeOrders.value[orderIndex].items.every(i => i.status === 'completed');
        if (allItemsCompleted && order.status === 'preparing') {
          // The order will be marked as ready when the user clicks the button
        }
      }
    }
    
    // Update backend
    await orderService.updateOrderItemStatus(order.id, item.id, 'completed');
  } catch (error) {
    console.error('Error updating item status:', error);
    // Revert on error
    fetchActiveOrders();
  }
};

// Start preparing an order
const startPreparingOrder = async (order: Order) => {
  try {
    await orderService.updateOrder(order.id, { status: 'preparing' });
    await fetchActiveOrders();
  } catch (error) {
    console.error('Error updating order status:', error);
  }
};

// Mark order as ready for pickup
const markOrderReady = async (order: Order) => {
  try {
    await orderService.updateOrder(order.id, { status: 'ready' });
    await fetchActiveOrders();
  } catch (error) {
    console.error('Error updating order status:', error);
  }
};

// Set up auto-refresh
const setupAutoRefresh = () => {
  // Initial fetch
  fetchActiveOrders();
  
  // Set up polling every 30 seconds
  refreshInterval = window.setInterval(fetchActiveOrders, 30000);
};

// Clean up on component unmount
onMounted(setupAutoRefresh);
onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval);
  }
});
</script>

<style scoped>
.kitchen-view {
  max-width: 1800px;
  margin: 0 auto;
}

/* Add any additional styles here */
</style>
